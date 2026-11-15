# ANS-001 — Experiment 01: Baroreflex, sympathetic regulation, and ageing

## Primary question
Does cardiac baroreflex sensitivity add independently reproducible information about age-related physiological regulation beyond resting HRV and established covariates?

## Secondary exploratory question
Where direct muscle sympathetic nerve activity (MSNA) is available, do sympathetic activity measures add incremental information beyond HRV and baroreflex sensitivity?

## Prerequisites
- Dataset inventory: licensing, age distribution, cohort size, ECG, beat-to-beat BP, respiratory signals, MSNA if available, medications, posture, functional outcomes and follow-up.
- Document signal sampling frequency, recording duration, challenge protocols, exclusion rules and missingness.
- Do not treat LF/HF ratio or HRV alone as a direct measure of sympathetic tone.

## Analysis plan
1. Define outcome before modeling: cross-sectional age association is not a longevity outcome.
2. Validate ECG R-peaks, systolic BP series, ectopy handling, stationarity and synchronized timestamps.
3. Estimate spontaneous cardiac BRS with sensitivity analysis across sequence and spectral approaches, reporting units ms/mmHg and method assumptions.
4. Fit prespecified baseline models with chronological age, HRV and available confounders.
5. Compare incremental information from BRS using subject-level holdouts, bootstrap confidence intervals and calibration where appropriate.
6. If longitudinal outcomes exist, evaluate prediction of functional decline or cardiovascular events, with leakage-safe splits.
7. Conduct external-cohort replication and negative controls if data permit.

## Stop/go criteria
No diagnostic, biological-age, or longevity claims from cross-sectional correlations. If suitable simultaneous ECG/BP data are unavailable, publish a feasibility limitation and do not manufacture results.

## Status
Protocol drafted. Dataset access, cloud execution and results not yet verified.
