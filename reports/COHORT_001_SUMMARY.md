# ANS-001 — 20-participant age-stratified waveform feasibility

Generated UTC: 2026-11-15T12:40:12.896111+00:00
Participants selected: 20
Recordings computationally processed: 20
Automatic ECG consistency checks passed: 19
Exploratory BRS values allowed past quality gate: 12

> **Exploratory engineering output. No manual ECG or BP annotation audit, clinical validation, longitudinal outcomes, or established ageing biomarker.**

Five minutes of resting data per participant, beginning one minute after recording start.
Participants selected with a fixed random seed from four age strata; device 0 only.
Sex partially balanced; BMI not matched. This sample is NOT representative.

| Age band | Selected | Processed | Automatic ECG-QC pass | Median screened RMSSD (ms)* |
|---|---:|---:|---:|---:|
| 18-34 | 5 | 5 | 5 | 41.5 |
| 35-49 | 5 | 5 | 5 | 13.8 |
| 50-64 | 5 | 5 | 5 | 20.9 |
| 65+ | 5 | 5 | 4 | 25.2 |

*Descriptive pilot values only; the estimator is not independently validated.

## Individual processing log

| ID | Age group | Sex (coded) | Status | ECG QC | HRV RMSSD | BRS sequence count |
|---|---|---|---|---|---:|---:|
| 0671 | 25-29 | 0 | processed | pass | 75.4 | 0 |
| 0924 | 18-19 | 0 | processed | pass | 53.0 | 1 |
| 0481 | 20-24 | 1 | processed | pass | 41.5 | 9 |
| 0573 | 20-24 | 1 | processed | pass | 37.8 | 0 |
| 1033 | 25-29 | 1 | processed | pass | 35.6 | 5 |
| 1049 | 40-44 | 0 | processed | pass | 7.6 | 7 |
| 0124 | 40-44 | 0 | processed | pass | 33.4 | 21 |
| 0045 | 45-49 | 1 | processed | pass | 8.5 | 44 |
| 0669 | 45-49 | 1 | processed | pass | 56.6 | 4 |
| 0353 | 40-44 | 1 | processed | pass | 13.8 | 20 |
| 0076 | 50-54 | 0 | processed | pass | 16.0 | 12 |
| 0381 | 60-64 | 0 | processed | pass | 38.5 | 9 |
| 0053 | 60-64 | 1 | processed | pass | 38.3 | 2 |
| 1058 | 50-54 | 1 | processed | pass | 17.3 | 6 |
| 0638 | 50-54 | 0 | processed | pass | 20.9 | 5 |
| 0554 | 70-74 | 0 | processed | review_required | 65.9 | 1 |
| 0091 | 70-74 | 0 | processed | pass | 21.7 | 0 |
| 0912 | 85-92 | 1 | processed | pass | 36.7 | 63 |
| 0779 | 85-92 | 1 | processed | pass | 28.6 | 0 |
| 0237 | 70-74 | 1 | processed | pass | 17.0 | 11 |

## Method limitations and interpretation

- Detector agreement is a consistency check between two algorithms, **not ground truth**.
- RR screening does not prove intervals are normal-to-normal; automated HRV is provisional.
- BRS is deliberately withheld when recording quality or sequences are insufficient.
- BP alignment and systolic detection must be verified manually before any BRS use.
- Different age strata can differ in BMI, sex, medications or other unmeasured factors.
- No inferential age association, age prediction or clinical claim is generated at this gate.
- The dataset's original authors already reported HRV-age patterns; replication is not novelty.

Source: https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/
Citation: Schumann & Bär (2021), DOI 10.13026/2hsy-t491.

Raw QC diagnostics and four representative 10-second plots are in the Actions artifact.
