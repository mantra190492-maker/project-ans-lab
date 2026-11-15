# ANS-001 — First real PhysioNet pilot: independent result review

**Status:** 3/3 recordings computationally processed; **0 clinically or scientifically validated biomarkers**.

## Provenance
- Source: PhysioNet Autonomic Aging v1.0.0, DOI 10.13026/2hsy-t491.
- Execution: `ANS-001 Real PhysioNet Pilot #1`, commit `3f35ec9` (2026-11-15).
- Raw output: `physionet_pilot.json` from GitHub Actions artifact `ans-001-physionet-pilot`, supplied for review by project founder.
- SHA-256 of the original JSON file: `bf84156b764384cc8a2b31c1fc82ea99143f095572491be58de072a6b0500649`.
- Measurements are **software outputs, not established physiology**; raw ECG/BP traces not manually audited.

## Measured outputs

| Variable | Record 0001 | Record 0002 | Record 0003 |
|---|---:|---:|---:|
| Duration (seconds) | 900.4 | 1938.3 | 1801.1 |
| Sampling frequency (Hz) | 1000 | 1000 | 1000 |
| ECG R-peaks found | 1061 | 2148 | 2776 |
| Heart rate (bpm) | 70.723 | 66.481 | 92.490 |
| SDNN (ms) | 64.127 | 72.173 | 5.981 |
| RMSSD (ms) | 69.442 | 72.603 | 5.516 |
| Systolic BP beats paired | 1060 | 1998 | 2775 |
| Matched BP beat percentage* | 100.0 | 93.1 | 100.0 |
| Mean sequence BRS (ms/mmHg) | 40.130 | 15.284 | **null** |
| BRS sequences found | 11 | 6 | 0 |

*Paired BP beats / (R-peaks - 1), derived from the experiment output.

## Participant metadata (official PhysioNet subject-info.csv)

| Record | Age-group code | Age range | Sex | BMI | Device category |
|---|---:|---|---|---:|---:|
| 0001 | 2 | 20–24 years | Female | 23 | 0 |
| 0002 | 2 | 20–24 years | Female | 24 | 0 |
| 0003 | 7 | 45–49 years | Female | 28 | 0 |

Source: https://www.physionet.org/content/autonomic-aging-cardiovascular/1.0.0/subject-info.csv. Device code 0 = TFM (CNSystems). These are coded, generalized age ranges, not exact ages. The older participant's different HRV is **a within-sample observation only**, not an estimated age effect. 

## Quality and interpretation

1. All three runs returned `processed`, indicating the signal-processing script completed without record-specific errors.
2. Record 0003's SDNN/RMSSD are much lower than 0001 and 0002. **No interpretation about age, disease, or longevity is justified**, although official age bins have now been verified, signal QA and confounder control have not been completed.
3. Three recordings are too few for population inference.
4. The algorithm's `plausible_rr_fraction=1.0` means 100% passed simple 0.4–1.5s interval bounds; **it does not validate beat detection or rule out artifacts**.
5. BRS sample counts are sparse (11, 6, 0): results may be highly method-dependent. Null in 0003 is **not** proof of absent baroreflex.
6. ECG/BP synchronization, BP calibration, beat detector performance, corrected NN definition, and HRV stationarity require validation.
7. The dataset is cross-sectional, acquired at rest. It cannot establish prospective disease risk, ageing rate, sympathetic nerve activity, or longevity.

## Next experiment gate

- **DONE:** Link PhysioNet `subject-info.csv` age-group, sex, BMI, and recording device for 0001–0003; do not infer age from record ID.
- Independent R-peak detector cross-check, RR artifact counts, and 60–120 second ECG/BP alignment visualization per record.
- Analyze contiguous clean segments of standardized length with documented exclusions.
- BRS must have prespecified sequence criteria and reliability/bootstrapped uncertainty; reject/mark null when insufficient.
- Only then scale a stratified age-bin pilot and compare added value of BRS vs HRV with participant-level splits.

**Decision:** PASS engineering feasibility; HOLD scientific interpretation and cohort scaling until quality controls pass.
