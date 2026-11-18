# HRF-NULL-001 — Can visit-1 PIP falsely predict vagal decline?

Generated UTC: 2026-11-15T17:14:57.258776+00:00

Simulated cohorts: 200 per scenario × 300 people × 500 beats per visit. True vagal change is independent of fragmentation in every null scenario.

Model per cohort: Δlog(outcome) ~ PIP1 + log(outcome at visit 1) + age + baseline RR; test PIP at α = 0.05. A clean endpoint should reject about 5% of the time under the null.

| Scenario | Outcome | Rejection rate | Reading |
|---|---|---:|---|
| null_stable_fragmentation | rmssd | 100.0% ± 0.0 | trap material |
| null_stable_fragmentation | rsa_resp | 3.0% ± 1.2 | safe |
| null_stable_fragmentation | rmssd_oracle_true_fragmentation | 17.5% ± 2.7 | trap material |
| null_stable_fragmentation | rsa_resp_oracle_true_fragmentation | 4.5% ± 1.5 | safe |
| null_progressing_fragmentation | rmssd | 98.0% ± 1.0 | trap material |
| null_progressing_fragmentation | rsa_resp | 8.0% ± 1.9 | borderline |
| null_progressing_fragmentation | rmssd_oracle_true_fragmentation | 19.5% ± 2.8 | trap material |
| null_progressing_fragmentation | rsa_resp_oracle_true_fragmentation | 6.0% ± 1.7 | safe |
| null_progressing_same_250hz_grid | rmssd | 100.0% ± 0.0 | trap material |
| null_progressing_same_250hz_grid | rsa_resp | 4.0% ± 1.4 | safe |
| null_progressing_same_250hz_grid | rmssd_oracle_true_fragmentation | 16.0% ± 2.6 | trap material |
| null_progressing_same_250hz_grid | rsa_resp_oracle_true_fragmentation | 8.5% ± 2.0 | borderline |
| positive_control_real_effect | rmssd | 100.0% ± 0.0 | power (real effect present) |
| positive_control_real_effect | rsa_resp | 36.0% ± 3.4 | power (real effect present) |
| positive_control_real_effect | rmssd_oracle_true_fragmentation | 100.0% ± 0.0 | power (real effect present) |
| positive_control_real_effect | rsa_resp_oracle_true_fragmentation | 100.0% ± 0.0 | power (real effect present) |

Agent-defined reading (set in code before the first run; not an external preregistration): ≤7.5% safe; 7.5–10% borderline; >10% trap material. Rates are type-I error in THIS generative model only, not a real-world SHHS rate.

## Limits

- Stylised model: fragmentation is simulated as runs of beat-to-beat alternation plus extra non-respiratory beat noise; real HRF is more varied.
- In this model, measured PIP tracks low respiratory vagal amplitude (r ≈ −0.7) far more than latent fragmentation (r ≈ 0.26). That is why RMSSD-change models produce false positives and why the PIP positive control has limited power.
- Version history: a first run (v1: isolated alternating beats, effect −0.8) gave the same pattern — RMSSD 99.5–100% false positives, breathing-locked RSA 4.5–8.0%, positive-control power 8%. v2 (this report) made fragmentation drive PIP more strongly and raised the effect to −1.5.
- The respiration-locked estimator uses a simulated breathing phase with noise; SHHS belts may be worse.
- Effect sizes and noise levels are assumptions, not SHHS estimates. Treat as a design check, not evidence.
