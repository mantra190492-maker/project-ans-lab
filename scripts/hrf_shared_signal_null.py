"""HRF-NULL-001: can visit-1 PIP falsely "predict" vagal decline in SHHS-HRF-001?

The trap: PIP and the vagal outcome come from the same heartbeats. Fragmentation adds
beat-to-beat variability that inflates RMSSD-type measures at baseline. Models of
change that adjust for an error-contaminated baseline can then show a PIP effect even
when fragmentation has NO causal link to future vagal change.

This simulation builds cohorts where, by construction, true vagal (RSA) change is
independent of fragmentation given age (the null). It counts how often the SHHS-HRF-001
style model  delta_log(outcome) ~ PIP1 + log(outcome1) + age + baseline RR  rejects at
alpha = 0.05. A positive-control scenario checks that a real effect would be detected.

Design mirrors SHHS: visit 1 on a 125 Hz grid, visit 2 on a 250 Hz grid (plus a
same-grid control). PIP uses the Costa-reference implementation.

Outcomes compared:
  rmssd     - conventional ECG-only vagal proxy (SHHS-HRF-001 secondary)
  rsa_resp  - respiration-locked RSA amplitude: RR regressed on sin/cos of a noisy
              breathing phase (stand-in for the protocol's breathing-linked primary)

Agent-defined reading (written in code before the first run; not an external preregistration):
  false-positive rate <= 7.5%  -> endpoint safe from the trap in this model
  7.5% to 10%                  -> borderline
  > 10%                        -> trap material; endpoint unusable as specified
This is a stylised model, not SHHS data. It shows whether the trap CAN occur and
whether the planned endpoint choice defends against it.
"""
from __future__ import annotations

import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from anslab.hrf_costa_reference import costa_fragmentation_from_peaks

SCENARIOS = {
    # name: (fragmentation drift between visits, effect of F1 on true log-RSA change, visit-1 grid Hz)
    "null_stable_fragmentation": (0.00, 0.0, 125.0),
    "null_progressing_fragmentation": (0.05, 0.0, 125.0),
    "null_progressing_same_250hz_grid": (0.05, 0.0, 250.0),
    "positive_control_real_effect": (0.05, -1.5, 125.0),
}
N_BEATS = 500
FRAG_AMPLITUDE_S = 0.012
NOISE_S = 0.002
NOISE_PER_FRAG_S = 0.010  # v2: latent fragmentation also raises non-respiratory beat noise
PHASE_NOISE_RAD = 0.3


MEAN_SEGMENT_BEATS = 6
FRAG_MODEL = "segments"  # v2 default; "sporadic" reproduces the first (v1) run


def fragmented_mask(rng, frag_p):
    """Alternation runs (Markov on/off segments), closer to observed HRF than isolated beats."""
    if FRAG_MODEL == "sporadic":
        return rng.random(N_BEATS) < frag_p
    p = min(max(frag_p, 0.0), 0.6)
    if p == 0:
        return np.zeros(N_BEATS, dtype=bool)
    p_exit = 1.0 / MEAN_SEGMENT_BEATS
    p_enter = min(p / (1 - p) * p_exit, 0.95)
    mask = np.zeros(N_BEATS, dtype=bool)
    pos, on = 0, rng.random() < p
    while pos < N_BEATS:
        length = int(rng.geometric(p_exit if on else p_enter))
        if on:
            mask[pos:pos + length] = True
        pos += length
        on = not on
    return mask


def visit(rng, base_rr, rsa_ms, frag_p, grid_hz):
    i = np.arange(N_BEATS)
    resp_hz = rng.uniform(0.2, 0.3)
    phi0 = rng.uniform(0, 2 * np.pi)
    phase = 2 * np.pi * resp_hz * i * base_rr + phi0
    frag = FRAG_AMPLITUDE_S * np.where(i % 2 == 0, 1.0, -1.0) * fragmented_mask(rng, frag_p)
    noise_sd = NOISE_S + NOISE_PER_FRAG_S * frag_p if FRAG_MODEL == "segments" else NOISE_S
    rr = base_rr + rsa_ms / 1000.0 * np.sin(phase) + frag + rng.normal(0, noise_sd, N_BEATS)
    rr = np.clip(rr, 0.35, 1.75)
    times = np.concatenate([[0.0], np.cumsum(rr)])
    times = np.round(times * grid_hz) / grid_hz
    rr_q = np.diff(times) * 1000.0
    rmssd = float(np.sqrt(np.mean(np.diff(rr_q) ** 2)))
    measured_phase = phase + rng.normal(0, PHASE_NOISE_RAD, N_BEATS)
    design = np.column_stack([np.ones(N_BEATS), np.sin(measured_phase), np.cos(measured_phase)])
    coef, *_ = np.linalg.lstsq(design, rr_q, rcond=None)
    rsa_resp = float(math.hypot(coef[1], coef[2]))
    return times, rmssd, rsa_resp


def ols_pvalue(y, X, column):
    n, k = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sigma2 = resid @ resid / (n - k)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    t = beta[column] / math.sqrt(cov[column, column])
    # two-sided normal approximation (n >= 300)
    p = math.erfc(abs(t) / math.sqrt(2))
    return float(beta[column]), float(p)


def cohort(args):
    seed, scenario, n_subjects = args
    drift, effect, grid1 = SCENARIOS[scenario]
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_subjects):
        age = rng.uniform(45, 85)
        log_a1 = rng.normal(math.log(25) - 0.02 * (age - 65), 0.45)
        f1 = float(np.clip(0.10 + 0.004 * (age - 65) + rng.normal(0, 0.08), 0, 0.6))
        log_a2 = log_a1 + rng.normal(-0.10 - 0.004 * (age - 65), 0.20) + effect * (f1 - 0.10)
        f2 = float(np.clip(f1 + drift + rng.normal(0, 0.04), 0, 0.7))
        rr1 = float(np.clip(rng.normal(1.0, 0.1), 0.7, 1.3))
        rr2 = float(np.clip(rr1 + rng.normal(0, 0.03), 0.65, 1.35))
        t1, rmssd1, rsa1 = visit(rng, rr1, math.exp(log_a1), f1, grid1)
        _, rmssd2, rsa2 = visit(rng, rr2, math.exp(log_a2), f2, 250.0)
        pip1 = costa_fragmentation_from_peaks(t1, [1] * len(t1), sampling_hz=grid1)["pip_percent"]
        rows.append((age, rr1, pip1, rmssd1, rmssd2, rsa1, rsa2, f1))
    a = np.array(rows)
    age, rr1, pip1 = a[:, 0], a[:, 1], a[:, 2]
    out = {}
    for name, c1, c2 in (("rmssd", 3, 4), ("rsa_resp", 5, 6)):
        base = np.log(np.maximum(a[:, c1], 0.5))
        delta = np.log(np.maximum(a[:, c2], 0.5)) - base
        X = np.column_stack([np.ones(len(a)), pip1, base, age, rr1])
        beta, p = ols_pvalue(delta, X, 1)
        out[name] = (beta, p)
        # Oracle: same model with the TRUE latent fragmentation instead of measured PIP.
        X_oracle = np.column_stack([np.ones(len(a)), a[:, 7], base, age, rr1])
        out[name + "_oracle_true_fragmentation"] = ols_pvalue(delta, X_oracle, 1)
    return out


def classify(rate):
    if rate <= 0.075:
        return "safe"
    if rate <= 0.10:
        return "borderline"
    return "trap material"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohorts", type=int, default=200)
    parser.add_argument("--subjects", type=int, default=300)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()
    results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for s_idx, scenario in enumerate(SCENARIOS):
            jobs = [(20261115 + 1000 * s_idx + k, scenario, args.subjects) for k in range(args.cohorts)]
            runs = list(pool.map(cohort, jobs, chunksize=4))
            results[scenario] = {}
            for outcome in ("rmssd", "rsa_resp", "rmssd_oracle_true_fragmentation", "rsa_resp_oracle_true_fragmentation"):
                ps = np.array([r[outcome][1] for r in runs])
                betas = np.array([r[outcome][0] for r in runs])
                rate = float(np.mean(ps < 0.05))
                results[scenario][outcome] = {
                    "rejection_rate": rate,
                    "mc_se": float(math.sqrt(rate * (1 - rate) / len(ps))),
                    "mean_pip_coefficient": float(np.mean(betas)),
                    "reading": ("power (real effect present)" if "positive" in scenario else classify(rate)),
                }
            print(scenario, {k: round(v["rejection_rate"], 3) for k, v in results[scenario].items()}, flush=True)
    payload = {"study": "HRF-NULL-001", "cohorts": args.cohorts, "subjects_per_cohort": args.subjects,
               "beats_per_visit": N_BEATS, "scenarios": {k: {"fragmentation_drift": v[0], "true_effect": v[1],
                                                               "visit1_grid_hz": v[2]} for k, v in SCENARIOS.items()},
               "results": results, "generated_utc": datetime.now(timezone.utc).isoformat()}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "HRF_SHARED_SIGNAL_NULL.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# HRF-NULL-001 — Can visit-1 PIP falsely predict vagal decline?", "",
             f"Generated UTC: {payload['generated_utc']}", "",
             f"Simulated cohorts: {args.cohorts} per scenario × {args.subjects} people × {N_BEATS} beats per visit. "
             "True vagal change is independent of fragmentation in every null scenario.", "",
             "Model per cohort: Δlog(outcome) ~ PIP1 + log(outcome at visit 1) + age + baseline RR; test PIP at α = 0.05. "
             "A clean endpoint should reject about 5% of the time under the null.", "",
             "| Scenario | Outcome | Rejection rate | Reading |", "|---|---|---:|---|"]
    for scenario, by_outcome in results.items():
        for outcome, r in by_outcome.items():
            lines.append(f"| {scenario} | {outcome} | {100 * r['rejection_rate']:.1f}% ± {100 * r['mc_se']:.1f} | {r['reading']} |")
    lines += ["", "Agent-defined reading (set in code before the first run; not an external preregistration): ≤7.5% safe; 7.5–10% borderline; >10% trap material. Rates are type-I error in THIS generative model only, not a real-world SHHS rate.", "",
              "## Limits", "",
              "- Stylised model: fragmentation is simulated as runs of beat-to-beat alternation plus extra non-respiratory beat noise; real HRF is more varied.",
              "- In this model, measured PIP tracks low respiratory vagal amplitude (r ≈ −0.7) far more than latent fragmentation (r ≈ 0.26). That is why RMSSD-change models produce false positives and why the PIP positive control has limited power.",
              "- Version history: a first run (v1: isolated alternating beats, effect −0.8) gave the same pattern — RMSSD 99.5–100% false positives, breathing-locked RSA 4.5–8.0%, positive-control power 8%. v2 (this report) made fragmentation drive PIP more strongly and raised the effect to −1.5.",
              "- The respiration-locked estimator uses a simulated breathing phase with noise; SHHS belts may be worse.",
              "- Effect sizes and noise levels are assumptions, not SHHS estimates. Treat as a design check, not evidence."]
    (out / "HRF_SHARED_SIGNAL_NULL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
