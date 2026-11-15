"""FUSION-001: do two lab-scored autonomic domains together separate diabetes from controls better than one?

Implements wearable/experiments/FUSION_001_PLAN.md. Reads only the GE-71 summary table
(open, CC BY 4.0). Outputs aggregates only. Clinic-grade inputs, at-risk label: this is
an upper-bound check of the layered idea, not autonomic-dysfunction detection.
"""
from __future__ import annotations

import csv
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from scipy import stats

URL = "https://physionet.org/files/cerebral-vasoreg-diabetes/1.0.0/Data_Description/GE-71_Data_Summary_Table.csv"
COLS = ("VM RATIO", "SBP TILT BASELINE1", "TILT AVE1", "HR TILT BASELINE", "TILT AVE", "Age", "Gender", "Group")
MISSING = {"", "NA", "NAN", "N/A", ".", "-", "NONE", "NULL"}
RIDGE = 1.0
N_BOOT = 2000
GAIN_RULE = 0.05


def fetch(url=URL, tries=5):
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "ProjectANS-Lab/0.7"})
            r.raise_for_status()
            return r.content.decode("utf-8-sig", errors="replace")
        except requests.RequestException as err:
            last = err
            time.sleep(10 * (attempt + 1))
    raise last


def num(text):
    t = (text or "").strip()
    if t.upper() in MISSING:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def auc(y, score):
    y = np.asarray(y, dtype=int)
    r = stats.rankdata(score)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def fit_logistic(X, y, ridge=RIDGE, iters=50):
    """Ridge logistic regression by Newton steps; intercept unpenalised."""
    Xb = np.column_stack([np.ones(len(X)), X])
    beta = np.zeros(Xb.shape[1])
    pen = np.eye(Xb.shape[1]) * ridge
    pen[0, 0] = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(Xb @ beta, -30, 30)))
        grad = Xb.T @ (y - p) - pen @ beta
        hess = Xb.T @ (Xb * (p * (1 - p))[:, None]) + pen
        step = np.linalg.solve(hess, grad)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    return beta


def loo_predictions(X, y):
    """Out-of-fold linear scores; scaling is fitted on the training fold only."""
    X = np.asarray(X, dtype=float)
    out = np.zeros(len(y))
    for i in range(len(y)):
        m = np.ones(len(y), dtype=bool)
        m[i] = False
        mu, sd = X[m].mean(axis=0), X[m].std(axis=0)
        sd[sd == 0] = 1.0
        beta = fit_logistic((X[m] - mu) / sd, y[m])
        out[i] = beta[0] + ((X[i] - mu) / sd) @ beta[1:]
    return out


def partial_spearman(a, b, c):
    ra, rb, rc = (stats.rankdata(v) for v in (a, b, c))
    res = lambda u: u - np.polyval(np.polyfit(rc, u, 1), rc)  # noqa: E731
    return float(np.corrcoef(res(ra), res(rb))[0, 1])


def analyse(vr, dsbp, dhr, age, sex, y, seed=20261115):
    base = np.column_stack([age, sex])
    models = {"M0_age_sex": base, "M1_plus_cardiovagal": np.column_stack([base, vr]),
              "M2_plus_adrenergic": np.column_stack([base, dsbp]), "M3_plus_both": np.column_stack([base, vr, dsbp]),
              "S_plus_both_and_tilt_hr": np.column_stack([base, vr, dsbp, dhr])}
    preds = {k: loo_predictions(X, y) for k, X in models.items()}
    aucs = {k: auc(y, p) for k, p in preds.items()}
    best_single = max(("M1_plus_cardiovagal", "M2_plus_adrenergic"), key=lambda k: aucs[k])
    gain = aucs["M3_plus_both"] - aucs[best_single]
    rng = np.random.default_rng(seed)
    diffs, m3 = [], []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].min() == y[idx].max():
            continue
        a3 = auc(y[idx], preds["M3_plus_both"][idx])
        m3.append(a3)
        diffs.append(a3 - max(auc(y[idx], preds["M1_plus_cardiovagal"][idx]), auc(y[idx], preds["M2_plus_adrenergic"][idx])))
    ci = [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]
    rho, p = stats.spearmanr(vr, dsbp)
    return {"n": int(len(y)), "n_diabetes": int(y.sum()), "n_control": int((1 - y).sum()), "loo_auc": aucs,
            "auc_m3_bootstrap_ci95": [float(np.percentile(m3, 2.5)), float(np.percentile(m3, 97.5))],
            "best_single_domain_model": best_single, "fusion_gain_auc": float(gain), "fusion_gain_bootstrap_ci95": ci,
            "fusion_adds": bool(gain >= GAIN_RULE and ci[0] > 0),
            "domain_correlation": {"spearman": float(rho), "p": float(p), "age_adjusted_partial": partial_spearman(vr, dsbp, age)},
            "single_measure_auc_unadjusted": {"valsalva_ratio_low": auc(y, -vr), "tilt_sbp_fall": auc(y, -dsbp), "tilt_hr_rise_low": auc(y, -dhr)}}


def load(text):
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip() for h in rows[0]]
    ix = {c: header.index(c) for c in COLS}
    data, flow = [], {"table_rows": len(rows) - 1}
    sexes = sorted({r[ix["Gender"]].strip().lower() for r in rows[1:] if len(r) > ix["Gender"] and r[ix["Gender"]].strip()})
    for r in rows[1:]:
        if len(r) <= max(ix.values()):
            continue
        v = {c: num(r[ix[c]]) for c in COLS[:6]}
        sex, group = r[ix["Gender"]].strip().lower(), r[ix["Group"]].strip().lower()
        if any(v[c] is None for c in COLS[:6]) or v["VM RATIO"] < 0.9 or sex not in sexes or not group or len(sexes) != 2:
            flow["missing_any_required"] = flow.get("missing_any_required", 0) + 1
            continue
        data.append((v["VM RATIO"], v["TILT AVE1"] - v["SBP TILT BASELINE1"], v["TILT AVE"] - v["HR TILT BASELINE"],
                     v["Age"], float(sexes.index(sex)), 0.0 if "control" in group else 1.0, v["SBP TILT BASELINE1"], v["HR TILT BASELINE"]))
    a = np.array(data, dtype=float)
    flow["analysed"] = len(a)
    if not (80 <= np.median(a[:, 6]) <= 200 and 40 <= np.median(a[:, 7]) <= 120):
        raise ValueError("Tilt columns do not look like systolic pressure and heart rate; column mapping must be checked")
    return a, flow


def main():
    a, flow = load(fetch())
    vr, dsbp, dhr, age, sex, y = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5].astype(int)
    res = analyse(vr, dsbp, dhr, age, sex, y)
    q = lambda v: [round(float(np.percentile(v, p)), 2) for p in (25, 50, 75)]  # noqa: E731
    desc = {"valsalva_ratio": {"control": q(vr[y == 0]), "diabetes": q(vr[y == 1])},
            "tilt_sbp_change_mmHg": {"control": q(dsbp[y == 0]), "diabetes": q(dsbp[y == 1])},
            "tilt_hr_change_bpm": {"control": q(dhr[y == 0]), "diabetes": q(dhr[y == 1])},
            "age": {"control": q(age[y == 0]), "diabetes": q(age[y == 1])}}
    payload = {"study": "FUSION-001", "plan": "wearable/experiments/FUSION_001_PLAN.md",
               "generated_utc": datetime.now(timezone.utc).isoformat(), "flow": flow, "result": res, "quartiles_25_50_75": desc}
    L = res["loo_auc"]
    lines = ["# FUSION-001 — do two autonomic domains together beat one?", "",
             f"Generated UTC: {payload['generated_utc']}  ", "Plan frozen before values were read: `wearable/experiments/FUSION_001_PLAN.md`", "",
             f"**Decision under the frozen rule: {'FUSION ADDS' if res['fusion_adds'] else 'NO DEMONSTRATED GAIN FROM FUSION'}**", "",
             f"People analysed: {res['n']} ({res['n_diabetes']} diabetes, {res['n_control']} control). Inputs are lab-scored clinic tests, not watch signals. "
             "Label is diabetes status, an at-risk label, not confirmed autonomic dysfunction.", "",
             "| Model (leave-one-out AUC for diabetes vs control) | AUC |", "|---|---:|",
             f"| M0: age + sex | {L['M0_age_sex']:.2f} |", f"| M1: + cardiovagal (Valsalva ratio) | {L['M1_plus_cardiovagal']:.2f} |",
             f"| M2: + adrenergic (tilt systolic change) | {L['M2_plus_adrenergic']:.2f} |",
             f"| **M3: + both domains** | **{L['M3_plus_both']:.2f}** (bootstrap 95% CI {res['auc_m3_bootstrap_ci95'][0]:.2f} to {res['auc_m3_bootstrap_ci95'][1]:.2f}) |",
             f"| Secondary: both + tilt heart-rate change | {L['S_plus_both_and_tilt_hr']:.2f} |", "",
             f"Fusion gain over the better single-domain model ({res['best_single_domain_model']}): {res['fusion_gain_auc']:+.2f} "
             f"(bootstrap 95% CI {res['fusion_gain_bootstrap_ci95'][0]:+.2f} to {res['fusion_gain_bootstrap_ci95'][1]:+.2f}; rule: ≥ +0.05 and CI above 0).", "",
             f"Are the two domains independent? Spearman ρ = {res['domain_correlation']['spearman']:+.2f} (p = {res['domain_correlation']['p']:.2f}); "
             f"age-adjusted {res['domain_correlation']['age_adjusted_partial']:+.2f}.", "",
             "Single measures alone (unadjusted AUC): " + ", ".join(f"{k.replace('_', ' ')} {v:.2f}" for k, v in res["single_measure_auc_unadjusted"].items()) + ".", "",
             "## Quartiles (25th, median, 75th)", "", "```", json.dumps(desc, indent=1), "```", "",
             "## Limits", "", "- One small table from one lab; AUC here is uncertain by roughly ±0.15.",
             "- Two of three domains only: no sweat (sudomotor) test exists in the open data.",
             "- Diabetes status is not autonomic dysfunction. A clinic cohort with a full reflex battery is needed for that."]
    for folder in (Path("wearable/reports"), Path("reports/explore")):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "FUSION_001.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
        (folder / "FUSION_001.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:22]))


if __name__ == "__main__":
    main()
