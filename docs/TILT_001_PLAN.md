# TILT-001 — does resting heart-rate fragmentation track a blunted heart-rate response to tilt?

**Frozen 2026-11-15 before any person-level link between fragmentation and tilt response was computed.** Last item in the open-data queue (`docs/RESEARCH_LEDGER.md`).

**Disclosure:** from FUSION-001 the group quartiles of the tilt heart-rate change are already known (median 12 bpm in controls, 9 bpm in diabetes). No relation between any resting ECG marker and the tilt response has been seen. This is the second test of PIP in the same GE-71 participants, and the third outcome-level test overall.

## Single primary question

Is higher resting fragmentation associated with a **smaller heart-rate rise on head-up tilt**, beyond age, sex, diabetes, resting heart rate and RMSSD?

## Locked measurements

- **Outcome:** lab-computed tilt heart-rate change = `TILT AVE` − `HR TILT BASELINE` (bpm) from the GE-71 summary table. A blunted rise is the heart-rate half of the neurogenic pattern on orthostatic testing.
- **Predictor:** Costa-reference PIP on the 250 Hz grid from seconds 30–270 of the Day-2 record, exactly as in GE71-ANS-001.
- **Quality control (all outcome-blind):** same CO2 check and beat rules as GE71-ANS-001, except the two-detector agreement check is replaced by beat-shape consistency (≥ 90% of beats correlate ≥ 0.8 with the median beat). Reason: the old check discarded 15 of 57 records.
- **Comparators and covariates:** mean heart rate and log RMSSD from the same window; age, sex, diabetes.
- **Benchmark (reported, not a second hypothesis):** deceleration capacity. **Sensitivity:** hard-inflection rate.

## Analysis and decision rule

- OLS: tilt heart-rate change ~ PIP + age + sex + diabetes + mean HR + log RMSSD (standardised predictors). One two-sided test, α = 0.05, expected sign negative.
- **Candidate signal** only if p < 0.05 with a negative coefficient, the participant-bootstrap 95% CI (4,000 resamples) excludes 0, and the sign holds in every leave-one-out fit.
- About 40 people: only a partial correlation near 0.4 or larger is detectable. A null is inconclusive, not proof of no effect.
- Nothing else is tested on this dataset under this plan. After this test the open-data queue is exhausted.
