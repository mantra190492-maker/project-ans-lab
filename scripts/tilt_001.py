"""TILT-001: resting heart-rate fragmentation vs lab-computed heart-rate response to head-up tilt.

Implements docs/TILT_001_PLAN.md. Predictors are extracted and hashed before any outcome
column is parsed. Aggregates only.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from scipy import stats

from anslab.physio_qc import detect_ecg_rpeaks
from scripts.cded_inventory import parse_sha256sums
from scripts.ge71_analysis import ENV_HZ, WINDOW_S, fit_marker, hrv_metrics, is_candidate, number, refine_peaks, subject_key, window_qc
from scripts.ge71_prepare import envelope
from scripts.vr_core import template_quality

PROJECT = "cerebral-vasoreg-diabetes/1.0.0/"
BASES = ("https://physionet-open.s3.amazonaws.com/" + PROJECT, "https://physionet.org/files/" + PROJECT)
SUMMARY = "Data_Description/GE-71_Data_Summary_Table.csv"
MIN_TEMPLATE = 0.90
UA = {"User-Agent": "ProjectANS-Lab/0.8"}


def fetch_bytes(path, session, tries=3):
    last = None
    for attempt in range(tries):
        for base in BASES:
            try:
                r = session.get(base + path.replace(" ", "%20"), headers=UA, timeout=120)
                r.raise_for_status()
                return r.content
            except requests.RequestException as err:
                last = err
        time.sleep(8 * (attempt + 1))
    raise last


def load_window(path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            (Path(tmp) / (name + ext)).write_bytes(fetch_bytes(path + ext, session))
        header = wfdb.rdheader(str(Path(tmp) / name))
        fs = float(header.fs)
        if header.sig_len < WINDOW_S[1] * fs:
            raise ValueError("record shorter than rest window")
        names = [n.lower() for n in header.sig_name]
        rec = wfdb.rdrecord(str(Path(tmp) / name), sampfrom=int(WINDOW_S[0] * fs), sampto=int(WINDOW_S[1] * fs),
                            channels=[names.index("ecg"), names.index("co2")])
        return rec.p_signal[:, 0], rec.p_signal[:, 1], fs


def predictors_for(ecg, co2, fs):
    status = window_qc(envelope(co2, fs, ENV_HZ))
    if status != "ok":
        return status, None
    ecg = np.nan_to_num(ecg - np.nanmedian(ecg))
    ecg = ecg / (np.percentile(np.abs(ecg), 99) + 1e-12)
    p1, _, _ = detect_ecg_rpeaks(ecg, fs)
    peaks = refine_peaks(ecg, p1, fs)
    if template_quality(ecg, peaks, fs) < MIN_TEMPLATE:
        return "beat_shape_inconsistent", None
    m = hrv_metrics(peaks / fs)
    return m["status"], (m if m["status"] == "ok" else None)


def main():
    session = requests.Session()
    out = Path("reports/explore")
    out.mkdir(parents=True, exist_ok=True)
    paths = parse_sha256sums(fetch_bytes("SHA256SUMS.txt", session).decode("utf-8", errors="replace"))
    day2 = sorted(p[:-4] for p in paths if "head-up-tilt_day2" in p.lower() and p.lower().endswith(".hea"))
    pred, flow = {}, {"day2_records": len(day2)}
    for p in day2:
        try:
            status, m = predictors_for(*load_window(p, session))
            if m:
                pred[subject_key(Path(p).name)] = m
        except Exception as err:  # noqa: BLE001 - counted and reported
            status = f"error_{type(err).__name__}"
        flow[status] = flow.get(status, 0) + 1
        print(Path(p).name, status, flush=True)
    keys = sorted(pred)
    fields = ["pip", "hard_rate", "hr", "log_rmssd", "dc"]
    sha = hashlib.sha256("\n".join(",".join([k] + [f"{pred[k][f]:.6f}" for f in fields]) for k in keys).encode()).hexdigest()

    table = list(csv.reader(io.StringIO(fetch_bytes(SUMMARY, session).decode("utf-8-sig", errors="replace"))))
    header = [h.strip() for h in table[0]]
    col = {c: header.index(c) for c in ("SUBJECT NUMBER", "Gender", "Age", "Group", "HR TILT BASELINE", "TILT AVE")}
    people = {subject_key(r[col["SUBJECT NUMBER"]]): r for r in table[1:] if len(r) > max(col.values()) and subject_key(r[col["SUBJECT NUMBER"]])}
    sexes = sorted({r[col["Gender"]].strip().lower() for r in people.values() if r[col["Gender"]].strip()})
    flow["in_summary_table"] = sum(k in people for k in keys)
    data = []
    for k in keys:
        r = people.get(k)
        if r is None:
            continue
        base, tilt, age = number(r[col["HR TILT BASELINE"]]), number(r[col["TILT AVE"]]), number(r[col["Age"]])
        sex, group = r[col["Gender"]].strip().lower(), r[col["Group"]].strip().lower()
        if None in (base, tilt, age) or sex not in sexes or len(sexes) != 2 or not group:
            flow["missing_outcome_or_covariate"] = flow.get("missing_outcome_or_covariate", 0) + 1
            continue
        data.append({**pred[k], "dhr": tilt - base, "age": age, "sex": float(sexes.index(sex)), "dm": 0.0 if "control" in group else 1.0})
    flow["analysed"] = len(data)
    arr = lambda f: np.array([d[f] for d in data], dtype=float)  # noqa: E731
    y = arr("dhr")
    covs = [arr("age"), arr("sex"), arr("dm"), arr("hr"), arr("log_rmssd")]
    primary = fit_marker(y, arr("pip"), covs)
    candidate = is_candidate(primary)
    dc_ok = np.isfinite(arr("dc"))
    bench = {"deceleration_capacity_benchmark": fit_marker(y[dc_ok], arr("dc")[dc_ok], [c[dc_ok] for c in covs]) if dc_ok.sum() > 12 else None,
             "hard_inflection_rate_sensitivity": fit_marker(y, arr("hard_rate"), covs)}
    sp = lambda a, b: [float(v) for v in stats.spearmanr(a, b)]  # noqa: E731
    corr = {"pip_vs_tilt_hr_change": sp(arr("pip"), y), "resting_hr_vs_tilt_hr_change": sp(arr("hr"), y),
            "log_rmssd_vs_tilt_hr_change": sp(arr("log_rmssd"), y), "age_vs_tilt_hr_change": sp(arr("age"), y),
            "pip_vs_log_rmssd": sp(arr("pip"), arr("log_rmssd"))}
    payload = {"study": "TILT-001", "plan": "docs/TILT_001_PLAN.md", "generated_utc": datetime.now(timezone.utc).isoformat(),
               "predictor_table_sha256": sha, "flow": flow, "primary": primary, "candidate_signal": candidate,
               "benchmarks_and_sensitivity": bench, "spearman": corr,
               "n_control": int((arr("dm") == 0).sum()), "n_diabetes": int((arr("dm") == 1).sum())}
    (out / "TILT_001_RESULT.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")

    def row(name, r):
        if not r:
            return f"| {name} | — | — | — | — | — |"
        return (f"| {name} | {r['n']} | {r['beta_per_sd']:+.2f} [{r['ci95'][0]:+.2f}, {r['ci95'][1]:+.2f}] | {r['p']:.3f} | "
                f"{r['bootstrap_ci95'][0]:+.2f} to {r['bootstrap_ci95'][1]:+.2f} | {r['r2_base']:.2f} → {r['r2_full']:.2f} |")
    lines = ["# TILT-001 — resting heart-rate fragmentation vs heart-rate response to tilt", "",
             f"Generated UTC: {payload['generated_utc']}  ", "Plan frozen first: `docs/TILT_001_PLAN.md`  ",
             f"Predictor table SHA-256 (before outcomes were parsed): `{sha}`", "",
             f"**Decision under the frozen rule: {'CANDIDATE SIGNAL' if candidate else 'NO CANDIDATE (null or inconclusive)'}**", "",
             f"Analysed: {len(data)} people ({payload['n_diabetes']} diabetes, {payload['n_control']} control).", "", "```", json.dumps(flow, indent=1), "```", "",
             "| Marker (adjusted for age, sex, diabetes, resting HR, log RMSSD) | n | β in bpm per SD [95% CI] | p | Bootstrap 95% CI | R² base → full |",
             "|---|---:|---|---:|---|---|", row("**PIP (primary)**", primary),
             row("Deceleration capacity (benchmark)", bench["deceleration_capacity_benchmark"]),
             row("Hard-inflection rate (sensitivity)", bench["hard_inflection_rate_sensitivity"]), "",
             f"Leave-one-out range of the primary coefficient: {primary['leave_one_out_range'][0]:+.2f} to {primary['leave_one_out_range'][1]:+.2f}", "",
             "## Simple rank correlations (ρ, p)", ""]
    lines += [f"- {k.replace('_', ' ')}: ρ = {v[0]:+.2f}, p = {v[1]:.3f}" for k, v in corr.items()]
    lines += ["", "## Limits", "", "- One small dataset; second test of the same marker in the same people.",
              "- Tilt heart-rate change is one half of the orthostatic response; pressure data were not used here.",
              "- Cross-sectional association, not prediction of decline."]
    (out / "TILT_001_RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"flow": flow, "primary": primary, "candidate": candidate}, indent=1))


if __name__ == "__main__":
    main()
