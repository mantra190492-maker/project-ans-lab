# ANS-001 — Cohort 001 scientific audit and decision

**Date:** 2026-11-15  
**Scope:** Independently assess the cloud-generated 20-participant engineering feasibility report, not infer physiological ageing.

## Confirmed engineering findings

- **20/20** PhysioNet ECG and BP recordings were processed for a standardized five-minute window.
- **19/20** passed algorithmic ECG checks; **12/20** yielded exploratory BRS numbers under the present software gate.
- Four age strata (five people each), same **device category 0**, with partial sex balance.
- Outputs and provenance: [per-participant JSON](../reports/physionet_cohort.json), [CSV](../reports/physionet_cohort.csv), [summary](../reports/COHORT_001_SUMMARY.md).

## Specific quality flags

1. **Record 0554 (age 70–74):** only **52.6%** of RR intervals survived the automated consistency screen and only **78.1%** of detected ECG beats paired with a BP systolic peak. Its displayed RMSSD **65.9 ms must NOT be used for any age-group comparison**. Two QRS detection methods still had ~98.9% agreement, demonstrating that detector agreement alone is insufficient.
2. **Records 0671 and 0924:** ECG check passed, but BP peak matching reached only **67.6%** and **60.8%**, respectively; withholding their BRS was appropriate.
3. **BRS:** 12 records had values passing provisional software criteria. None have independent ECG/BP alignment, manually adjudicated peak counts, or external-method validation. Thus **0 validated BRS estimates**.
4. Some participants show unusually low automated RMSSD, for example 1049: 7.6 ms and 0045: 8.5 ms. These could reflect real physiology or processing/recording conditions; no health inference is justified.

## Descriptive pilot HRV, NOT an inferential result

| Age stratum | Automatic ECG-QC pass | Median screened RMSSD (ms) |
|---|---:|---:|
| 18–34 | 5 of 5 | 41.5 |
| 35–49 | 5 of 5 | 13.8 |
| 50–64 | 5 of 5 | 20.9 |
| 65+ | 4 of 5 | 25.2 |

The medians **do not decrease monotonically** with age. This non-representative, tiny sample cannot establish or refute an age association, and the reported group medians should not be compared with clinical normative ranges.

## Mandatory scientific gates before a larger analysis

- Manual review of several ECG/BP snippets across age strata, especially 0554 and records with low BP beat matching; correct detected beats and document missed/false picks.
- Test ECG/BP beat alignment and validate BRS against a reference implementation or annotated recordings; verify filter/window choices.
- Check stationarity and effect of the RR artifact-screening thresholds using sensitivity analyses.
- Preregister an age-bin comparison and adjusted controls (sex, BMI, device, heart rate), with participant-level separation and appropriate uncertainty.
- Replicate on an independent dataset before proposing an ageing biomarker.
- For the **ultimate longevity aim**, obtain longitudinal health outcomes. This PhysioNet cohort is resting and cross-sectional.

## Decision

**Engineering feasibility — PASS.**
**Automatic preliminary ECG screening — 19 of 20 passed.**
**Scientific measurement validation — HOLD.**
**Ageing biomarker and longitudinal claims — NOT ESTABLISHED.**

Reference: Schumann A, Bär K. PhysioNet Autonomic Aging dataset v1.0.0 (2021), DOI 10.13026/2hsy-t491. The original 2022 Scientific Data description already reported age-related HRV associations; repeating them would not constitute novelty.
