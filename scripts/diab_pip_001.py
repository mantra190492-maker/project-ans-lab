"""DIAB-PIP-001: resting heart-rate fragmentation in type 2 diabetes vs controls.

Implements docs/DIAB_PIP_001_PLAN.md (frozen in commit d033849 before any ECG was read).
Stage 1 computes every ECG-derived value and quality decision and hashes them.
Stage 2 only then parses group labels. Aggregates only.
"""
from __future__ import annotations

import hashlib
import json
import math
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from scipy import stats

from anslab.physio_qc import detect_ecg_rpeaks
from scripts.cded_inventory import parse_sha256sums
from scripts.diab_prepare import DATASETS, GE71, MISSING, fetch, find_col, subject_key
from scripts.diab_prepare2 import ID_PATTERNS, cell, read_table
from scripts.ge71_analysis import ENV_HZ, N_BOOT, WINDOW_S, hrv_metrics, ols, refine_peaks, window_qc
from scripts.ge71_prepare import envelope
from scripts.vr_core import template_quality

MIN_TEMPLATE = 0.90
CO2_SWING = (10.0, 80.0)
ORDER = ("GE75", "CDED")          # record preference for a person present in both datasets
FIELDS = ("pip", "hr", "log_rmssd")
COLUMNS = {"group": [r"group"], "beta": [r"beta blockers"], "age": [r"age"], "sex": [r"sex", r"gender"]}


# ---------- stage 1: blind measurements ----------
def co2_plausible(co2_env, hz=ENV_HZ):
    x = np.asarray(co2_env, dtype=float)
    win = 10 * hz
    rng = np.array([np.ptp(x[i:i + win]) for i in range(0, len(x) - win + 1, hz)])
    return bool(len(rng)) and CO2_SWING[0] <= float(np.percentile(rng, 75)) <= CO2_SWING[1]


def measure(ecg, co2, fs):
    env = envelope(co2, fs, ENV_HZ)
    status = window_qc(env)
    if status != "ok":
        return status, None
    if not co2_plausible(env):
        return "co2_implausible", None
    ecg = np.nan_to_num(ecg - np.nanmedian(ecg))
    ecg = ecg / (np.percentile(np.abs(ecg), 99) + 1e-12)
    p1, _, _ = detect_ecg_rpeaks(ecg, fs)
    peaks = refine_peaks(ecg, p1, fs)
    if template_quality(ecg, peaks, fs) < MIN_TEMPLATE:
        return "beat_shape_inconsistent", None
    m = hrv_metrics(peaks / fs)
    return m["status"], (m if m["status"] == "ok" else None)


def load_window(project, path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            (Path(tmp) / (name + ext)).write_bytes(fetch(project, path + ext, session))
        header = wfdb.rdheader(str(Path(tmp) / name))
        fs = float(header.fs)
        if header.sig_len < WINDOW_S[1] * fs:
            raise ValueError("record shorter than rest window")
        names = [n.lower() for n in header.sig_name]
        rec = wfdb.rdrecord(str(Path(tmp) / name), sampfrom=int(WINDOW_S[0] * fs), sampto=int(WINDOW_S[1] * fs),
                            channels=[names.index("ecg"), names.index("co2")])
        return rec.p_signal[:, 0], rec.p_signal[:, 1], fs


def predictor_hash(rows):
    lines = []
    for r in sorted(rows, key=lambda r: (r["dataset"], r["id"])):
        vals = [f"{r[f]:.6f}" for f in FIELDS] if r["status"] == "ok" else []
        lines.append(",".join([r["dataset"], r["id"], r["status"]] + vals))
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


# ---------- stage 2: labels ----------
def to_group(text):
    t = (text or "").strip().lower()
    return 1 if t == "dm" else 0 if t == "control" else None


def people_from_tables(tables):
    """Merge several (header, rows) tables into {id: {field: first non-missing value}}; visit-2 rows only where a Visit column exists."""
    out = {}
    for header, rows in tables:
        idc, visit = find_col(header, ID_PATTERNS), find_col(header, [r"visit"])
        cols = {f: find_col(header, pats) for f, pats in COLUMNS.items()}
        for r in rows:
            k = subject_key(cell(r, idc))
            if not k or (visit is not None and cell(r, visit) not in ("2", "2.0")):
                continue
            slot = out.setdefault(k, {f: "" for f in COLUMNS})
            for f, c in cols.items():
                v = cell(r, c)
                if not slot[f] and v.upper() not in MISSING:
                    slot[f] = v.strip().lower()
    return out


def choose_records(rows, people, ge71_ids):
    """One record per person, following the frozen rules. Returns (analysed rows with labels, person-level flow)."""
    by_id = {}
    for r in rows:
        by_id.setdefault(r["id"], {})[r["dataset"]] = r
    flow, chosen, selection = Counter(), [], {0: Counter(), 1: Counter()}
    flow["unique_people"] = len(by_id)
    flow["people_with_records_in_both_datasets"] = sum(1 for v in by_id.values() if len(v) > 1)
    for pid, recs in sorted(by_id.items()):
        if pid in ge71_ids:
            flow["excluded_also_in_ge71"] += 1
            continue
        labelled = [(ds, recs[ds], to_group(people[ds].get(pid, {}).get("group"))) for ds in ORDER if ds in recs]
        labelled = [(ds, r, g) for ds, r, g in labelled if g is not None]
        if not labelled:
            flow["excluded_no_group_label"] += 1
            continue
        passing = [(ds, r, g) for ds, r, g in labelled if r["status"] == "ok"]
        group = labelled[0][2]
        if not passing:
            flow["no_record_passed_quality_rules"] += 1
            selection[group]["failed"] += 1
            continue
        ds, r, g = passing[0]
        selection[g]["passed"] += 1
        flow["analysed"] += 1
        info = people[ds].get(pid, {})
        chosen.append({**r, "dm": float(g), "beta": info.get("beta", ""), "age": info.get("age", ""), "sex": info.get("sex", "")})
    return chosen, dict(flow), {("diabetes" if g else "control"): dict(c) for g, c in selection.items()}


# ---------- statistics ----------
def design(g, covs):
    cols = [np.ones(len(g)), np.asarray(g, dtype=float)]
    for c in covs:
        c = np.asarray(c, dtype=float)
        sd = c.std(ddof=0)
        if sd > 0:                                   # a covariate that is constant in this sample is dropped
            cols.append((c - c.mean()) / sd)
    return np.column_stack(cols)


def coef(y, g, covs):
    beta, *_ = np.linalg.lstsq(design(g, covs), y, rcond=None)
    return float(beta[1])


def group_difference(y, g, covs, n_boot=N_BOOT, seed=20261117):
    """Adjusted difference (group 1 minus group 0) with t-test, within-group bootstrap and leave-one-out."""
    y, g = np.asarray(y, dtype=float), np.asarray(g, dtype=float)
    covs = [np.asarray(c, dtype=float) for c in covs]
    X = design(g, covs)
    beta, se, _, p, df, r2 = ols(y, X)
    tcrit = float(stats.t.ppf(0.975, df))
    rng = np.random.default_rng(seed)
    i0, i1 = np.where(g == 0)[0], np.where(g == 1)[0]
    boot = []
    for _ in range(n_boot):
        idx = np.concatenate([rng.choice(i0, len(i0)), rng.choice(i1, len(i1))])
        boot.append(coef(y[idx], g[idx], [c[idx] for c in covs]))
    keep = np.ones(len(y), dtype=bool)
    loo = []
    for i in range(len(y)):
        keep[i] = False
        loo.append(coef(y[keep], g[keep], [c[keep] for c in covs]))
        keep[i] = True
    sd_pooled = math.sqrt((y[i0].var(ddof=1) * (len(i0) - 1) + y[i1].var(ddof=1) * (len(i1) - 1)) / (len(y) - 2))
    return {"n": int(len(y)), "n_diabetes": int(len(i1)), "n_control": int(len(i0)), "difference": float(beta[1]),
            "ci95": [float(beta[1] - tcrit * se[1]), float(beta[1] + tcrit * se[1])], "p": float(p[1]),
            "bootstrap_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "loo_min": float(min(loo)), "loo_max": float(max(loo)), "r2": float(r2),
            "difference_in_pooled_sd": float(beta[1] / sd_pooled) if sd_pooled > 0 else None, "n_boot": int(n_boot)}


def is_pass(res):
    return bool(res["p"] < 0.05 and res["difference"] > 0 and res["bootstrap_ci95"][0] > 0 and res["loo_min"] > 0)


def quartiles(v):
    v = np.asarray(v, dtype=float)
    return [float(np.percentile(v, q)) for q in (25, 50, 75)] if len(v) else None


def fit_or_none(data, covariate_names, min_per_group=5):
    g = np.array([d["dm"] for d in data])
    if (g == 0).sum() < min_per_group or (g == 1).sum() < min_per_group:
        return None
    return group_difference(np.array([d["pip"] for d in data]), g, [np.array([d[c] for d in data], dtype=float) for c in covariate_names])


def as_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def analyse(chosen):
    for d in chosen:
        d["ge75"] = 1.0 if d["dataset"] == "GE75" else 0.0
    primary = fit_or_none(chosen, ["ge75", "hr", "log_rmssd"])
    sens = {"S1_without_hr_and_rmssd": fit_or_none(chosen, ["ge75"]),
            "S2_cded_only": fit_or_none([d for d in chosen if d["dataset"] == "CDED"], ["hr", "log_rmssd"]),
            "S3_excluding_beta_blocker_users": fit_or_none([d for d in chosen if not d["beta"].startswith("y")], ["ge75", "hr", "log_rmssd"])}
    sexes = sorted({d["sex"] for d in chosen if d["sex"]})
    sub = [dict(d, age_n=as_number(d["age"]), sex_n=float(sexes.index(d["sex"]))) for d in chosen
           if as_number(d["age"]) is not None and d["sex"] and len(sexes) == 2]
    sens["S4_adding_age_and_sex_where_available"] = fit_or_none(sub, ["ge75", "hr", "log_rmssd", "age_n", "sex_n"], min_per_group=10)
    desc = {}
    for label, flag in (("diabetes", 1.0), ("control", 0.0)):
        grp = [d for d in chosen if d["dm"] == flag]
        desc[label] = {"n": len(grp), "pip_q25_50_75": quartiles([d["pip"] for d in grp]), "hr_q25_50_75": quartiles([d["hr"] for d in grp]),
                       "rmssd_ms_q25_50_75": quartiles([math.exp(d["log_rmssd"]) for d in grp]),
                       "from_ge75": sum(1 for d in grp if d["dataset"] == "GE75"), "from_cded": sum(1 for d in grp if d["dataset"] == "CDED"),
                       "beta_blocker_users": sum(1 for d in grp if d["beta"].startswith("y"))}
    rho = [float(v) for v in stats.spearmanr([d["pip"] for d in chosen], [d["log_rmssd"] for d in chosen])] if len(chosen) > 3 else None
    return primary, sens, desc, rho, {"s4_subset_n": len(sub)}


def main():
    session = requests.Session()
    out = Path("reports/explore")
    out.mkdir(parents=True, exist_ok=True)

    # ---- stage 1: measurements, blind to group ----
    rows, record_flow, table_paths = [], {}, {}
    for name, cfg in DATASETS.items():
        paths = parse_sha256sums(fetch(cfg["project"], "SHA256SUMS.txt", session).decode("utf-8", errors="replace"))
        table_paths[name] = [p for p in paths if p.lower().endswith(".csv") and "summary" in p.lower()]
        records = sorted(p[:-4] for p in paths if cfg["match"].search(p))
        flow = Counter(records=len(records))
        for p in records:
            m = None
            try:
                status, m = measure(*load_window(cfg["project"], p, session))
            except Exception as err:  # noqa: BLE001 - counted and reported
                status = f"error_{type(err).__name__}"
            flow[status] += 1
            row = {"dataset": name, "id": subject_key(Path(p).name), "status": status}
            if m:
                row.update({f: float(m[f]) for f in FIELDS})
            rows.append(row)
            print(name, Path(p).name, status, flush=True)
        record_flow[name] = dict(flow)
    sha = predictor_hash(rows)
    print("predictor table sha256", sha, flush=True)

    # ---- stage 2: labels ----
    people = {}
    for name, cfg in DATASETS.items():
        people[name] = people_from_tables([read_table(fetch(cfg["project"], t, session).decode("utf-8-sig", errors="replace")) for t in table_paths[name]])
    h71, r71 = read_table(fetch(GE71, "Data_Description/GE-71_Data_Summary_Table.csv", session).decode("utf-8-sig", errors="replace"))
    idc = find_col(h71, ID_PATTERNS)
    ge71_ids = {subject_key(cell(r, idc)) for r in r71} - {None}
    chosen, person_flow, selection = choose_records(rows, people, ge71_ids)
    primary, sens, desc, rho, extra = analyse(chosen)
    passed = bool(primary and is_pass(primary))
    payload = {"study": "DIAB-PIP-001", "plan": "docs/DIAB_PIP_001_PLAN.md", "plan_commit": "d033849",
               "generated_utc": datetime.now(timezone.utc).isoformat(), "predictor_table_sha256": sha,
               "record_flow": record_flow, "person_flow": person_flow, "quality_selection_by_group": selection,
               "primary": primary, "primary_passes_frozen_rule": passed, "sensitivity": sens, "descriptive": desc,
               "spearman_pip_vs_log_rmssd": rho, **extra}
    (out / "DIAB_PIP_001_RESULT.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")

    def row(name, r):
        if not r:
            return f"| {name} | not estimable | — | — | — | — |"
        return (f"| {name} | {r['n_diabetes']} / {r['n_control']} | {r['difference']:+.2f} [{r['ci95'][0]:+.2f}, {r['ci95'][1]:+.2f}] | {r['p']:.3f} | "
                f"{r['bootstrap_ci95'][0]:+.2f} to {r['bootstrap_ci95'][1]:+.2f} | {r['loo_min']:+.2f} to {r['loo_max']:+.2f} |")

    def q(v, fmt="{:.1f}"):
        return "—" if not v else f"{fmt.format(v[1])} [{fmt.format(v[0])}–{fmt.format(v[2])}]"
    verdict = ("**PASS of the frozen rule — recorded as a lead, NOT adjusted for age and sex, not a candidate biomarker.**" if passed
               else "**Null: the frozen rule is not met.**")
    lines = ["# DIAB-PIP-001 — resting heart-rate fragmentation in type 2 diabetes vs controls", "",
             f"Generated UTC: {payload['generated_utc']}  ", "Plan frozen first: `docs/DIAB_PIP_001_PLAN.md` (commit d033849)  ",
             f"Predictor table SHA-256 (written before any group label was parsed): `{sha}`", "",
             "## Result", "", verdict, "",
             "| Model | n diabetes / control | Difference in PIP points [95% CI] | p | Bootstrap 95% CI | Leave-one-out range |", "|---|---:|---:|---:|---:|---:|",
             row("Primary: PIP ~ diabetes + dataset + mean HR + log RMSSD", primary),
             row("S1: without mean HR and log RMSSD", sens["S1_without_hr_and_rmssd"]),
             row("S2: CDED only", sens["S2_cded_only"]),
             row("S3: excluding beta-blocker users", sens["S3_excluding_beta_blocker_users"]),
             row("S4: adding age and sex where available", sens["S4_adding_age_and_sex_where_available"]), "",
             "Sensitivity rows cannot turn a fail into a pass. Age and sex are not in the primary model because CDED does not publish them.", "",
             "## Groups (medians [quartiles], descriptive only)", "", "| Group | n | from CDED / GE-75 | PIP | Heart rate (bpm) | RMSSD (ms) | Beta-blocker users |", "|---|---:|---:|---:|---:|---:|---:|"]
    for label in ("diabetes", "control"):
        d = desc[label]
        lines.append(f"| {label} | {d['n']} | {d['from_cded']} / {d['from_ge75']} | {q(d['pip_q25_50_75'])} | {q(d['hr_q25_50_75'])} | {q(d['rmssd_ms_q25_50_75'])} | {d['beta_blocker_users']} |")
    if primary and primary.get("difference_in_pooled_sd") is not None:
        lines += ["", f"Adjusted difference as a fraction of the pooled SD of PIP: {primary['difference_in_pooled_sd']:+.2f}."]
    if rho:
        lines += [f"Spearman correlation of PIP with log RMSSD: {rho[0]:+.2f}."]
    lines += ["", "## Who was analysed", "", f"- Record-level quality outcomes (blind to group): {record_flow}",
              f"- Person-level flow: {person_flow}", f"- Quality-rule pass/fail by group (selection check): {selection}", "",
              "## Limits", "",
              "- Diabetes is an at-risk label, not confirmed autonomic dysfunction.",
              "- No adjustment for age or sex (not published for CDED). Both groups come from one recruitment age band per study, which narrows but does not remove age confounding.",
              "- Controls come almost entirely from CDED; GE-75 contributes mostly diabetes.",
              "- Fourth outcome-level test in this project; three earlier tests were null.",
              "- A null here is inconclusive for small differences (see the power note in the plan).", ""]
    (out / "DIAB_PIP_001_RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
