"""GE71-ANS-001: resting heart-rate fragmentation vs lab-computed Valsalva ratio.

Implements docs/GE71_ANS_001_PLAN.md exactly. Order is enforced in code:
predictors are extracted, written and hashed BEFORE any outcome column is parsed.
Outputs aggregates only (no participant-level rows).
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from scipy import stats
from scipy.signal import butter, sosfiltfilt

from anslab.hrf_costa_reference import costa_fragmentation_from_peaks
from anslab.physio_qc import detect_ecg_rpeaks, detector_agreement
from scripts.cded_inventory import UA, parse_sha256sums
from scripts.dataset_structure import get_text
from scripts.ge71_prepare import BASE, MISSING, SUMMARY, envelope

WINDOW_S = (30, 270)
ENV_HZ = 10
MIN_INTERVALS = 150
MIN_USABLE = 0.80
ECTOPY_TOL = 0.20
N_BOOT = int(__import__("os").environ.get("ANS_BOOT", "4000"))


# ---------- blind window QC (CO2 only) ----------
def window_qc(co2_env, hz=ENV_HZ):
    x = np.asarray(co2_env, dtype=float)
    if len(x) < (WINDOW_S[1] - WINDOW_S[0]) * hz * 0.98 or not np.all(np.isfinite(x)):
        return "too_short"
    win = 10 * hz
    rng = np.array([np.ptp(x[i:i + win]) for i in range(0, len(x) - win + 1, hz)])
    typical = float(np.percentile(rng, 75))
    if typical <= 0 or typical < 1e-9:
        return "no_capnogram"
    if np.any(rng < 0.2 * typical):
        return "no_breathing_gap"
    block = 20 * hz
    peaks = np.array([x[i:i + block].max() for i in range(0, len(x) - block + 1, block)])
    if peaks.min() < 0.8 * np.median(peaks):
        return "etco2_unstable"
    return "ok"


# ---------- beats ----------
def refine_peaks(ecg, peaks, fs, half_ms=40):
    x = sosfiltfilt(butter(2, [1, 40], btype="bandpass", fs=fs, output="sos"), np.asarray(ecg, dtype=float))
    sign = 1.0 if np.median(x[peaks]) >= 0 else -1.0
    half = int(round(half_ms * fs / 1000))
    out = []
    for p in peaks:
        lo, hi = max(0, p - half), min(len(x), p + half + 1)
        out.append(lo + int(np.argmax(sign * x[lo:hi])))
    out = np.array(sorted(set(out)))
    keep = [0]
    for i in range(1, len(out)):
        if out[i] - out[keep[-1]] >= 0.25 * fs:
            keep.append(i)
        elif sign * x[out[i]] > sign * x[out[keep[-1]]]:
            keep[-1] = i
    return out[keep]


def beat_labels(times, tol=ECTOPY_TOL, half_window=5):
    rr = np.diff(np.asarray(times, dtype=float))
    labels = [1] * len(times)
    for i, v in enumerate(rr):
        lo, hi = max(0, i - half_window), min(len(rr), i + half_window + 1)
        ref = float(np.median(rr[lo:hi]))
        if abs(v - ref) > tol * ref:
            labels[i + 1] = 3
    return labels


def deceleration_capacity(rr_ms, valid):
    rr = np.asarray(rr_ms, dtype=float)
    ok = np.asarray(valid, dtype=bool)
    acc = []
    for i in range(2, len(rr) - 1):
        if not (ok[i - 2] and ok[i - 1] and ok[i] and ok[i + 1]):
            continue
        if rr[i] > rr[i - 1] and rr[i] / rr[i - 1] <= 1.05:
            acc.append((rr[i] + rr[i + 1] - rr[i - 1] - rr[i - 2]) / 4.0)
    return float(np.mean(acc)) if len(acc) >= 30 else float("nan")


def grid_half_up(times, hz=250.0):
    return [math.floor(t * hz + 0.5) / hz for t in times]


def hrv_metrics(times_s):
    labels = beat_labels(times_s)
    rr = np.diff(np.asarray(times_s, dtype=float))
    lab = np.asarray(labels)
    valid = (lab[:-1] == 1) & (lab[1:] == 1) & (rr > 0.3) & (rr < 1.8)
    if len(rr) < MIN_INTERVALS or valid.mean() < MIN_USABLE:
        return {"status": "ecg_qc_fail", "n_intervals": int(len(rr)), "usable": float(valid.mean()) if len(rr) else 0.0}
    pair = valid[:-1] & valid[1:]
    d = np.diff(rr)[pair] * 1000
    costa = costa_fragmentation_from_peaks(grid_half_up(times_s), labels, sampling_hz=250.0)
    native = costa_fragmentation_from_peaks(list(times_s), labels, sampling_hz=1000.0)
    w = native["n_valid_three_interval_windows"]
    return {"status": "ok", "n_intervals": int(len(rr)), "usable": float(valid.mean()),
            "pip": costa["pip_percent"], "hard_rate": 100.0 * native["n_hard_inflections"] / w if w else float("nan"),
            "hr": 60.0 / float(rr[valid].mean()), "log_rmssd": math.log(float(np.sqrt(np.mean(d ** 2)))),
            "dc": deceleration_capacity(rr * 1000, valid)}


# ---------- statistics ----------
def zscore(v):
    v = np.asarray(v, dtype=float)
    return (v - v.mean()) / v.std(ddof=0)


def ols(y, X):
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df = n - k
    cov = (resid @ resid / df) * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), df)
    r2 = 1 - (resid @ resid) / float(((y - y.mean()) ** 2).sum())
    return beta, se, t, p, df, r2


def fit_marker(y, marker, covs, seed=20261115):
    """Marker coefficient in y ~ marker + covs (all standardised), with bootstrap and leave-one-out."""
    cols = [zscore(marker)] + [zscore(c) for c in covs]
    X = np.column_stack([np.ones(len(y))] + cols)
    beta, se, t, p, df, r2 = ols(y, X)
    base = ols(y, np.column_stack([np.ones(len(y))] + cols[1:]))[5] if covs else 0.0
    tcrit = stats.t.ppf(0.975, df)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(y), len(y))
        Xb, yb = X[idx], y[idx]
        if np.linalg.matrix_rank(Xb) < X.shape[1]:
            continue
        boots.append(np.linalg.lstsq(Xb, yb, rcond=None)[0][1])
    loo = []
    for i in range(len(y)):
        m = np.ones(len(y), dtype=bool)
        m[i] = False
        loo.append(np.linalg.lstsq(X[m], y[m], rcond=None)[0][1])
    return {"n": int(len(y)), "beta_per_sd": float(beta[1]), "ci95": [float(beta[1] - tcrit * se[1]), float(beta[1] + tcrit * se[1])],
            "p": float(p[1]), "partial_r2": float(t[1] ** 2 / (t[1] ** 2 + df)), "r2_base": float(base), "r2_full": float(r2),
            "bootstrap_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "leave_one_out_range": [float(min(loo)), float(max(loo))]}


def is_candidate(res):
    return bool(res["p"] < 0.05 and res["beta_per_sd"] < 0 and res["bootstrap_ci95"][1] < 0
                and res["leave_one_out_range"][1] < 0)


# ---------- data ----------
def subject_key(text):
    m = re.search(r"(\d{1,5})", text or "")
    return f"s{int(m.group(1)):04d}" if m else None


def number(text):
    t = (text or "").strip()
    if t.upper() in MISSING:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def load_window(path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            for _ in range(4):
                r = session.get(BASE + path + ext, headers=UA, timeout=300)
                if r.status_code == 200:
                    break
            r.raise_for_status()
            (Path(tmp) / (name + ext)).write_bytes(r.content)
        header = wfdb.rdheader(str(Path(tmp) / name))
        fs = float(header.fs)
        if header.sig_len < WINDOW_S[1] * fs:
            raise ValueError("record shorter than rest window")
        names = [n.lower() for n in header.sig_name]
        rec = wfdb.rdrecord(str(Path(tmp) / name), sampfrom=int(WINDOW_S[0] * fs), sampto=int(WINDOW_S[1] * fs),
                            channels=[names.index("ecg"), names.index("co2")])
        return rec.p_signal[:, 0], rec.p_signal[:, 1], fs


def extract_predictors(session):
    paths = parse_sha256sums(get_text(BASE + "SHA256SUMS.txt", session))
    day2 = sorted(p[:-4] for p in paths if "head-up-tilt_day2" in p.lower() and p.lower().endswith(".hea"))
    rows, flow = {}, {"day2_records": len(day2)}
    for p in day2:
        key = subject_key(Path(p).name)
        try:
            ecg, co2, fs = load_window(p, session)
            status = window_qc(envelope(co2, fs, ENV_HZ))
            if status == "ok":
                ecg = ecg - np.median(ecg)                      # unit-free scaling; thresholds are relative
                ecg = ecg / (np.percentile(np.abs(ecg), 99) + 1e-12)
                p1, p2, _ = detect_ecg_rpeaks(ecg, fs)
                if detector_agreement(p1, p2, fs) < 0.90:
                    status = "detector_disagreement"
                else:
                    m = hrv_metrics(refine_peaks(ecg, p1, fs) / fs)
                    status = m["status"]
                    if status == "ok":
                        rows[key] = m
        except Exception as err:  # noqa: BLE001 - counted and reported
            status = f"error_{type(err).__name__}"
        flow[status] = flow.get(status, 0) + 1
        print(Path(p).name, status, flush=True)
    return rows, flow


def main():
    session = requests.Session()
    out = Path("reports/explore")
    out.mkdir(parents=True, exist_ok=True)
    qc = Path("qc")
    qc.mkdir(exist_ok=True)

    # 1) predictors first, hashed before any outcome is parsed
    pred, flow = extract_predictors(session)
    keys = sorted(pred)
    fields = ["pip", "hard_rate", "hr", "log_rmssd", "dc"]
    blob = "\n".join(",".join([k] + [f"{pred[k][f]:.6f}" for f in fields]) for k in keys)
    predictor_sha = hashlib.sha256(blob.encode()).hexdigest()

    # 2) outcomes and covariates
    table = list(csv.reader(io.StringIO(get_text(BASE + SUMMARY, session))))
    header = [h.strip() for h in table[0]]
    col = {name: header.index(name) for name in ("SUBJECT NUMBER", "Gender", "Age", "Group", "VM RATIO", "VMRatio2", "Neuropathy")}
    people = {}
    for r in table[1:]:
        k = subject_key(r[col["SUBJECT NUMBER"]]) if len(r) > col["SUBJECT NUMBER"] else None
        if k:
            people[k] = r
    genders = sorted({people[k][col["Gender"]].strip().lower() for k in people if people[k][col["Gender"]].strip()})
    groups = {}
    data = []
    flow["in_summary_table"] = sum(k in people for k in keys)
    for k in keys:
        if k not in people:
            continue
        r = people[k]
        vr, age = number(r[col["VM RATIO"]]), number(r[col["Age"]])
        g = r[col["Group"]].strip().lower()
        sex = r[col["Gender"]].strip().lower()
        if vr is None or vr < 0.9 or age is None or sex not in genders or len(genders) != 2:
            flow["missing_outcome_or_covariate"] = flow.get("missing_outcome_or_covariate", 0) + 1
            continue
        groups[g] = groups.get(g, 0) + 1
        vr2 = number(r[col["VMRatio2"]])
        data.append({**pred[k], "vr": vr, "vr2": vr2 if vr2 and vr2 >= 0.9 else None, "age": age,
                     "sex": float(genders.index(sex)), "dm": 0.0 if "control" in g else 1.0,
                     "neuro": r[col["Neuropathy"]].strip().lower()})
    flow["analysed"] = len(data)
    arr = lambda f: np.array([d[f] for d in data], dtype=float)  # noqa: E731
    y = arr("vr")
    covs = [arr("age"), arr("sex"), arr("dm"), arr("hr"), arr("log_rmssd")]
    primary = fit_marker(y, arr("pip"), covs)
    candidate = is_candidate(primary)
    dc_ok = np.isfinite(arr("dc"))
    bench = {
        "deceleration_capacity_benchmark": fit_marker(y[dc_ok], arr("dc")[dc_ok], [c[dc_ok] for c in covs]) if dc_ok.sum() > 12 else None,
        "hard_inflection_rate_sensitivity": fit_marker(y, arr("hard_rate"), covs),
        "pip_unadjusted_for_hr_rmssd": fit_marker(y, arr("pip"), covs[:3]),
    }
    has2 = np.array([d["vr2"] is not None for d in data])
    if has2.sum() > 12:
        y2 = np.array([d["vr2"] for d in data if d["vr2"] is not None])
        bench["pip_vs_VMRatio2_sensitivity"] = fit_marker(y2, arr("pip")[has2], [c[has2] for c in covs])
    sp = lambda a, b: [float(v) for v in stats.spearmanr(a, b)]  # noqa: E731
    corr = {"pip_vs_vr": sp(arr("pip"), y), "hr_vs_vr": sp(arr("hr"), y), "log_rmssd_vs_vr": sp(arr("log_rmssd"), y),
            "age_vs_vr": sp(arr("age"), y), "pip_vs_log_rmssd": sp(arr("pip"), arr("log_rmssd")),
            "pip_vs_age": sp(arr("pip"), arr("age")), "dc_vs_vr": sp(arr("dc")[dc_ok], y[dc_ok])}
    med = lambda v: [float(np.percentile(v, q)) for q in (25, 50, 75)]  # noqa: E731
    dm = arr("dm") == 1
    desc = {"vr_all": med(y), "pip_all": med(arr("pip")), "age_all": med(arr("age")),
            "pip_control": med(arr("pip")[~dm]) if (~dm).sum() > 3 else None, "pip_diabetes": med(arr("pip")[dm]) if dm.sum() > 3 else None,
            "vr_control": med(y[~dm]) if (~dm).sum() > 3 else None, "vr_diabetes": med(y[dm]) if dm.sum() > 3 else None,
            "n_control": int((~dm).sum()), "n_diabetes": int(dm.sum()), "group_labels": groups, "gender_labels": genders,
            "neuropathy_counts": {v: sum(d["neuro"] == v for d in data) for v in sorted({d["neuro"] for d in data})}}

    payload = {"study": "GE71-ANS-001", "plan": "docs/GE71_ANS_001_PLAN.md", "generated_utc": datetime.now(timezone.utc).isoformat(),
               "predictor_table_sha256": predictor_sha, "flow": flow, "primary": primary, "candidate_signal": candidate,
               "benchmarks_and_sensitivity": bench, "spearman": corr, "descriptive_quartiles": desc}
    (out / "GE71_ANS_001_RESULT.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")

    def row(name, r):
        if not r:
            return f"| {name} | — | — | — | — | — |"
        return (f"| {name} | {r['n']} | {r['beta_per_sd']:+.3f} [{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}] | {r['p']:.3f} | "
                f"{r['bootstrap_ci95'][0]:+.3f} to {r['bootstrap_ci95'][1]:+.3f} | {r['r2_base']:.2f} → {r['r2_full']:.2f} |")
    lines = ["# GE71-ANS-001 — resting heart-rate fragmentation vs lab-computed Valsalva ratio", "",
             f"Generated UTC: {payload['generated_utc']}  ", "Plan frozen before data were read: `docs/GE71_ANS_001_PLAN.md`  ",
             f"Predictor table SHA-256 (written before outcomes were parsed): `{predictor_sha}`", "",
             f"**Decision under the frozen rule: {'CANDIDATE SIGNAL' if candidate else 'NO CANDIDATE (null or inconclusive)'}**", "",
             "## Who was analysed", "", "```", json.dumps(flow, indent=1), "```", "",
             f"Groups: {groups}; sex labels: {genders}; neuropathy: {desc['neuropathy_counts']}", "",
             "## Models (outcome: Valsalva ratio; coefficient per 1 SD of the marker)", "",
             "| Marker (adjusted for age, sex, diabetes, mean HR, log RMSSD) | n | β [95% CI] | p | Bootstrap 95% CI | R² base → full |",
             "|---|---:|---|---:|---|---|",
             row("**PIP (primary)**", primary),
             row("Deceleration capacity (benchmark)", bench["deceleration_capacity_benchmark"]),
             row("Hard-inflection rate (sensitivity)", bench["hard_inflection_rate_sensitivity"]),
             row("PIP, adjusted for age, sex, diabetes only", bench["pip_unadjusted_for_hr_rmssd"]),
             row("PIP vs VMRatio2 (sensitivity)", bench.get("pip_vs_VMRatio2_sensitivity")), "",
             f"Leave-one-out range of the primary coefficient: {primary['leave_one_out_range'][0]:+.3f} to {primary['leave_one_out_range'][1]:+.3f}", "",
             "## Simple rank correlations (ρ, p)", ""]
    lines += [f"- {k.replace('_', ' ')}: ρ = {v[0]:+.2f}, p = {v[1]:.3f}" for k, v in corr.items()]
    lines += ["", "## Quartiles (25th, median, 75th)", "", "```", json.dumps({k: v for k, v in desc.items() if k.startswith(('vr', 'pip', 'age', 'n_'))}, indent=1), "```", "",
              "## Limits", "", "- One small dataset from one lab; a single pre-specified test. Not a validated biomarker.",
              "- Valsalva ratio is one cardiovagal reflex test, not a full autonomic battery.",
              "- 4-minute resting window; fragmentation was developed on much longer recordings.",
              "- Cross-sectional: association with current reflex function, not prediction of future decline."]
    (out / "GE71_ANS_001_RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for flag, color, label in ((False, "tab:blue", "control"), (True, "tab:red", "diabetes")):
        m = dm == flag
        ax[0].scatter(arr("pip")[m], y[m], c=color, label=label, s=28)
        ax[1].scatter(arr("log_rmssd")[m], y[m], c=color, label=label, s=28)
    ax[0].set_xlabel("resting PIP (%)"); ax[0].set_ylabel("Valsalva ratio (lab-computed)"); ax[0].legend()
    ax[1].set_xlabel("log RMSSD"); ax[1].set_ylabel("Valsalva ratio")
    fig.suptitle(f"GE71-ANS-001, n={len(y)} (anonymous points)")
    fig.tight_layout()
    fig.savefig(qc / "ge71_ans_001_scatter.png", dpi=80)
    print(json.dumps({"flow": flow, "primary": primary, "candidate": candidate}, indent=1))


if __name__ == "__main__":
    main()
