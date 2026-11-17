"""ANS-DISC-002: HRV/BRS complementarity and quality-gate selection on real ECG/BP pilot summaries.

Uses the pre-existing public PhysioNet autonomic-aging cohort summary, not raw ECG
or patient-level clinical data. Outputs ONLY aggregate statistical diagnostics.
This is a falsification/feasibility test, NOT validation of a biomarker.

Run from repo root:
    python -m scripts.biomarker_complementarity_pilot
    python -m pytest -q tests/test_biomarker_complementarity_pilot.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, rankdata, spearmanr

DEFAULT_INPUT = Path("reports/physionet_cohort.json")
DEFAULT_REPORT = Path("reports/BIOMARKER_COMPLEMENTARITY_002.json")
SEED = 20261115
BOOTSTRAP_SAMPLES = 10000
PERMUTATION_SAMPLES = 20000


def _rho(x, y):
    with np.errstate(invalid="ignore"):
        val = spearmanr(x, y).statistic
    return float(val)


def _rank_partial_rho(x, y, z):
    """Descriptive partial rank correlation; not a causal adjusted effect."""
    a = np.asarray(rankdata(x), dtype=float)
    b = np.asarray(rankdata(y), dtype=float)
    c = np.asarray(rankdata(z), dtype=float)
    cc = np.column_stack((np.ones(len(c)), c))
    rx = a - cc @ np.linalg.lstsq(cc, a, rcond=None)[0]
    ry = b - cc @ np.linalg.lstsq(cc, b, rcond=None)[0]
    if np.std(rx) <= 0 or np.std(ry) <= 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def _permutation_p(x, y, observed, rng, n=PERMUTATION_SAMPLES):
    """Two-sided label permutation; no asymptotic small-sample p-value assumption."""
    ranks_x = rankdata(x)
    ranks_y = rankdata(y)
    rx = (ranks_x - ranks_x.mean()) / np.linalg.norm(ranks_x - ranks_x.mean())
    ry = (ranks_y - ranks_y.mean()) / np.linalg.norm(ranks_y - ranks_y.mean())
    extreme = 0
    for _ in range(n):
        perm = rng.permutation(ry)
        extreme += int(abs(float(np.dot(rx, perm))) >= abs(observed) - 1e-12)
    return (extreme + 1) / (n + 1)


def _bootstrap_ci(x, y, rng, n=BOOTSTRAP_SAMPLES):
    """Participant-level paired percentile bootstrap, tie-aware rank correlation."""
    samples = []
    for _ in range(n):
        take = rng.integers(0, len(x), size=len(x))
        xx, yy = x[take], y[take]
        if len(np.unique(xx)) < 3 or len(np.unique(yy)) < 3:
            continue
        v = _rho(xx, yy)
        if np.isfinite(v):
            samples.append(v)
    if len(samples) < int(n * .95):
        raise ValueError("Insufficient valid bootstrap resamples")
    return [float(v) for v in np.quantile(samples, [.025, .975])], len(samples)


def run_analysis(payload: dict, *, bootstrap_samples: int = BOOTSTRAP_SAMPLES,
                 permutation_samples: int = PERMUTATION_SAMPLES) -> dict:
    if payload.get("dataset") != "PhysioNet Autonomic Aging 1.0.0":
        raise ValueError("Unexpected dataset; do not reinterpret another cohort")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) < 15:
        raise ValueError("At least 15 original source records required")
    ids = [r.get("record") for r in records]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("Unique recording identifiers required")

    passed = [r for r in records if r.get("automatic_ecg_qc") == "pass"
              and np.isfinite(float(r.get("rmssd_ms") or 0)) and float(r.get("rmssd_ms") or 0) > 0]
    observed = [r for r in passed if r.get("brs_status") == "unvalidated_exploratory"
                and r.get("brs_ms_per_mmHg_exploratory") is not None]
    withheld = [r for r in passed if r.get("brs_ms_per_mmHg_exploratory") is None]
    if len(observed) + len(withheld) != len(passed):
        raise ValueError("Unexpected BRS status; cannot silently drop nonmissing records")
    if len(observed) < 8 or len(withheld) < 2:
        raise ValueError("Insufficient paired or withheld data for exploratory audit")
    x = np.asarray([r["rmssd_ms"] for r in observed], dtype=float)
    y = np.asarray([r["brs_ms_per_mmHg_exploratory"] for r in observed], dtype=float)
    hr = np.asarray([r["heart_rate_bpm"] for r in observed], dtype=float)
    miss = np.asarray([r["rmssd_ms"] for r in withheld], dtype=float)
    if not all(np.isfinite(v).all() for v in (x,y,hr,miss)):
        raise ValueError("Nonfinite physiological feature")
    rho = _rho(x, y)
    if not np.isfinite(rho):
        raise ValueError("Correlation undefined on constant or invalid measurements")
    rng_perm = np.random.default_rng(SEED)
    rng_boot = np.random.default_rng(SEED + 1)
    p = _permutation_p(x, y, rho, rng_perm, permutation_samples)
    ci, valid = _bootstrap_ci(x, y, rng_boot, bootstrap_samples)
    loo = [_rho(np.delete(x,i), np.delete(y,i)) for i in range(len(x))]
    mw = mannwhitneyu(x, miss, alternative="two-sided", method="exact")
    return {
        "experiment": "ANS-DISC-002",
        "source": "reports/physionet_cohort.json (existing public aggregate features)",
        "dataset": payload["dataset"],
        "persons_total": len(records),
        "ecg_qc_pass": len(passed),
        "ecg_qc_excluded": len(records)-len(passed),
        "provisional_brs_available": len(observed),
        "brs_withheld_after_ecg_qc": len(withheld),
        "brs_coverage_after_ecg_qc": len(observed)/len(passed),
        "rmssd_brs_spearman_rho": rho,
        "rmssd_brs_permutation_p_two_sided": float(p),
        "permutations": permutation_samples,
        "rmssd_brs_bootstrap_95pct_ci": ci,
        "bootstrap_samples_valid": valid,
        "leave_one_out_rho_range": [float(min(loo)),float(max(loo))],
        "heart_rate_brs_spearman_rho": _rho(hr, y),
        "rmssd_heart_rate_spearman_rho": _rho(x, hr),
        "rmssd_brs_partial_rank_rho_adjusting_heart_rate_descriptive": _rank_partial_rho(x,y,hr),
        "rmssd_median_with_brs_ms": float(np.median(x)),
        "rmssd_median_without_brs_ms": float(np.median(miss)),
        "rmssd_observed_vs_withheld_mann_whitney_exact_p": float(mw.pvalue),
        "qc_excluded_may_not_be_used_for_hrv_association": True,
        "clinical_labels_present": False,
        "brs_independently_validated": False,
        "test_status": "exploratory_evidence_of_correlated_signals_and_nonrandom_BRS_availability",
        "interpretation_limits": [
            "Only 20 convenience-selected resting healthy subjects; 12 exploratory BRS pairs, not independent clinical BRS truth.",
            "Both RMSSD and sequence-method BRS depend partly on the same ECG beat timing; high correlation cannot establish independent physiology or added accuracy.",
            "Availability reflects prior software QC and sequence-finding criteria; selection bias and algorithmic coupling may explain results.",
            "Exact Mann-Whitney and permutation p-values are unadjusted exploratory tests; small sample, no preregistration, no disease or longitudinal labels.",
            "No clinical sensitivity, specificity, early detection or new ANS biomarker can be calculated.",
        ],
    }


def main():
    raw = DEFAULT_INPUT.read_bytes()
    analysis = run_analysis(json.loads(raw))
    analysis["input_sha256"] = hashlib.sha256(raw).hexdigest()
    DEFAULT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_REPORT.write_text(json.dumps(analysis, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    main()
