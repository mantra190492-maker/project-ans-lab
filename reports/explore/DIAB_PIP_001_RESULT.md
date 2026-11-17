# DIAB-PIP-001 — resting heart-rate fragmentation in type 2 diabetes vs controls

Generated UTC: 2026-11-17T07:23:03.371527+00:00  
Plan frozen first: `docs/DIAB_PIP_001_PLAN.md` (commit d033849)  
Predictor table SHA-256 (written before any group label was parsed): `28c31f8b40083b29a09b982a016ccac6e17f71700ba042f8a0a79c771c297946`

## Result

**Null: the frozen rule is not met.**

| Model | n diabetes / control | Difference in PIP points [95% CI] | p | Bootstrap 95% CI | Leave-one-out range |
|---|---:|---:|---:|---:|---:|
| Primary: PIP ~ diabetes + dataset + mean HR + log RMSSD | 65 / 30 | +0.80 [-3.35, +4.95] | 0.703 | -3.72 to +4.83 | +0.02 to +1.65 |
| S1: without mean HR and log RMSSD | 65 / 30 | +0.58 [-3.52, +4.69] | 0.779 | -3.71 to +4.60 | -0.02 to +1.30 |
| S2: CDED only | 26 / 24 | +2.07 [-3.21, +7.36] | 0.434 | -3.12 to +7.22 | +0.84 to +3.35 |
| S3: excluding beta-blocker users | 53 / 27 | +1.37 [-2.92, +5.66] | 0.526 | -2.83 to +5.38 | +0.75 to +2.02 |
| S4: adding age and sex where available | not estimable | — | — | — | — |

Sensitivity rows cannot turn a fail into a pass. Age and sex are not in the primary model because CDED does not publish them.

## Groups (medians [quartiles], descriptive only)

| Group | n | from CDED / GE-75 | PIP | Heart rate (bpm) | RMSSD (ms) | Beta-blocker users |
|---|---:|---:|---:|---:|---:|---:|
| diabetes | 65 | 26 / 39 | 60.3 [52.0–64.8] | 70.3 [62.0–79.2] | 17.6 [11.3–23.7] | 12 |
| control | 30 | 24 / 6 | 59.9 [53.2–64.8] | 62.3 [54.7–68.0] | 18.1 [13.6–34.8] | 3 |

Adjusted difference as a fraction of the pooled SD of PIP: +0.09.
Spearman correlation of PIP with log RMSSD: -0.17.

## Who was analysed

- Record-level quality outcomes (blind to group): {'CDED': {'records': 69, 'ok': 61, 'no_breathing_gap': 5, 'etco2_unstable': 1, 'ecg_qc_fail': 2}, 'GE75': {'records': 52, 'no_breathing_gap': 5, 'ok': 45, 'ecg_qc_fail': 2}}
- Person-level flow: {'unique_people': 111, 'people_with_records_in_both_datasets': 10, 'excluded_also_in_ge71': 2, 'analysed': 95, 'excluded_no_group_label': 1, 'no_record_passed_quality_rules': 13}
- Quality-rule pass/fail by group (selection check): {'control': {'passed': 30, 'failed': 2}, 'diabetes': {'failed': 11, 'passed': 65}}

## Limits

- Diabetes is an at-risk label, not confirmed autonomic dysfunction.
- No adjustment for age or sex (not published for CDED). Both groups come from one recruitment age band per study, which narrows but does not remove age confounding.
- Controls come almost entirely from CDED; GE-75 contributes mostly diabetes.
- Fourth outcome-level test in this project; three earlier tests were null.
- A null here is inconclusive for small differences (see the power note in the plan).

