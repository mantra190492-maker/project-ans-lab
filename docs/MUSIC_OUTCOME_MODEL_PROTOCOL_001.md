# ANS-001 — MUSIC cardiac-outcome prediction protocol (DRAFT; no model fitted)

**Created:** 2026-11-15  
**Source:** [MUSIC v1.0.1, PhysioNet](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/), DOI 10.13026/z3m7-rf58.  
**Quality gate:** `reports/MUSIC_METADATA_AUDIT.md`, 992 participants, original source clinical CSV only.  
**Note:** This protocol is an exploratory analysis plan, not preregistered at OSF or any independent registry. **No outcome modeling has been run.**

## Why this cohort

The first ANS experiment used 20 cross-sectional healthy adults and cannot answer the predictive research question. MUSIC has baseline autonomic/ECG measures, heart-failure severity, therapy, 992 participant follow-up records, and adjudicated death categories. The available study data support a **chronic-heart-failure prognosis** question, NOT healthy ageing, pregnancy, menopause, stent-specific benefit, or longevity.

## Baseline and missingness gate (before viewing associations)

1. Source variables as documented in `subject-info.csv` and categorical `subject-info_codes.csv`:
   - Baseline age, sex code, BMI, NYHA class, LVEF, prior MI, HF etiology, prior revascularization (0 none / 1 percutaneous / 2 surgery / 3 both), beta blockers/other therapies, Holter rhythm, baseline SDNN/RMSSD, mean RR.
   - Follow-up period (days); exit codes (0 survivor / 1 lost / 2 transplant / 3 death) and cause-of-death (0 survivor / 1 noncardiac / 3 sudden cardiac / 6–7 pump failure). **Verify apparent mismatches and interpretation with definitions before calculating any event time or censoring.**
2. Existing aggregate audit: **992 participants**, **587** with nonmissing SDNN and RMSSD, **405** missing. **936** with Holter availability, and **933** recorded Holter rhythm. No assumption that Holter availability implies usable sinus rhythm.
3. Report missingness patterns by age, sex, NYHA/LVEF, rhythm, revascularization, beta-blocker and event coding **without outcome-driven feature selection**; suppress small cells in public outputs.
4. If sample representation is poor or censoring cannot be defined, publish **no prediction result**.

## Outcomes

- **Primary feasibility endpoint:** all-cause death if follow-up period + exit codes + mortality codes support complete non-decedent censoring and correct transplant handling.
- **Secondary:** cardiac death, sudden cardiac death and pump-failure death, **only** with well-defined cause-specific censoring or competing-risks methods. Model other death types as competing events, not always ordinary censoring.
- Follow-up is historical (~2003–2008); prior clinical treatment and risk scores limit generalizability to modern care.

## Baseline models and experimental comparison

After data validation and predefined eligibility:

- **Model 0:** age, sex code, NYHA, LVEF, diabetes, ischemic disease/prior MI, BP, beta-blocker, other medication covariates as sample size permits, plus relevant prior revascularization.
- **Model 1:** Model 0 + resting mean RR/heart rate and traditional HRV (log RMSSD or log SDNN; do not use too many correlated variables for limited events).
- **Model 2 candidate:** Model 1 + PIP/heart-rate fragmentation from quality-controlled Holter normal-to-normal intervals (prospectively specified); comparison to Model 1 tests incremental value.
- Test interactions or performance by rhythm (sinus vs AF/paced), prior revascularization and medication only if adequately powered. **Percutaneous revascularization does not establish coronary stent implantation**. Do not interpret interaction as intervention efficacy.
- Explicitly note heart-rate fragmentation is **prior art** from Costa et al. (2018 MESA) and other work. This would be replication / transportability, not marker invention.

## Data-quality and statistical requirements

1. Independently validate R-peak detection and arrhythmia handling on actual MUSIC segments before deriving HRF. Four Fantasia reference recordings are *insufficient* for MUSIC arrhythmia population.
2. Prespecify RR artifact/ectopy exclusion, minimum usable sinus rhythm, fragmentation sign/zero-change handling, time windows, breathing and circadian confounding. AF and pacing cannot automatically use normal sinus PIP.
3. Person-level train/validation/test design, event-based assessment, bootstrapped internal validation; no participant appearing in multiple folds, no outcome leakage from post-baseline variables.
4. Report event counts, deaths and censoring, concordance (C-index), calibration at prespecified horizons, confidence intervals, decision utility, and performance relative to **existing** MUSIC risk scores.
5. Use no unvalidated causal interpretation of BRS or HRF; ECG-only MUSIC lacks beat-to-beat pressure for BRS.

## Stop/go

**GO:** Metadata and censoring verified, representation checked, pre-analysis plan frozen, ECG and NN artifact screening validated; then run a SMALL and controlled ECG/HRF pilot.

**HOLD:** Full 90 GB waveform download, cardiac or longevity risk product, stent-specific outcomes, causal claims, or broad healthy-adult extrapolation.

**KILL/HYPOTHESIS NARROW:** Added ECG marker provides no externally replicable incremental prognostic information after clinical risk factors + heart rate + standard HRV.

## Links

- [MUSIC public dataset](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/)
- [Official categorical coding](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/subject-info_codes.csv)
- [Agent 02 evidence audit](AGENT_02_SKEPTICAL_ASSESSMENT_AUDIT.md)
- [First aggregate metadata audit](../reports/MUSIC_METADATA_AUDIT.md)

## 2026-11-15 multi-agent protocol safety addendum (no model fitted)

The uploaded external *MUSIC prediction protocol* (9 pages) strengthens the baseline comparator but must not be copied verbatim. See [four-agent adjudication](EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md).

1. **Clinical endpoints are not interchangeable.** Primary prospective model design remains **all-cause death**, with transplantation treated using a prespecified clinically justified estimand (e.g., transplant as censor/competing event plus sensitivity analyses). A separate **cardiac-death-or-transplant** composite may be scientifically interesting but must never be titled simply "cardiac death." Cardiac death by cause and 4-year cardiac-event risk require proper competing-event handling.
2. **Source count accuracy:** `Cause of death` code `0` is NOT adequate to prove survival among all 992 patients; cross-tab with the raw `Exit of the study` field. The [MUSIC aggregate audit](../reports/MUSIC_METADATA_AUDIT.md) includes this cross-tab after the November 15 correction. Blank exit codes must remain visible; do not silently assume `0`.
3. **Covariates:** Actual `subject-info.csv` **does include `Betablockers (yes=1)` and other drug columns**, contrary to the external agent's unresolved speculation; an institutional 2003–2004 treatment cohort may still lack time-varying exposure information.
4. **Stronger comparison:** Freeze M0 clinical severity + demographics + therapy, M1 + mean heart rate and conventional HRV, **M2 + validated deceleration capacity**, **M3 + reference-faithful PIP**. The incremental comparison **M3 vs M2** is the strongest relevant test. Avoid overfitting if the eligible event count is too small for all parameters.
5. **Definition consistency:** Costa 2018 mapped NN changes to -1 / 0 / +1 using approximately 4 ms ECG resolution at 256 Hz, then counted ternary transitions. A raw unquantized `ΔNN(i)×ΔNN(i+1)≤0` test is not automatically equivalent at a different sampling rate. Include published-method agreement tests and 4/5/8 ms sensitivity *before* opening outcomes.
6. **Risk of optimism:** The 607-person MUSIC sinus-rhythm heart-rate turbulence analysis (129 deaths, 52 sudden) is **not** the same population as 587 participants with available standard HRV, nor the final rhythm/QC-qualified HRF sample. Require a pre-outcome count audit and subject-level exclusion log.
7. **Research claim:** Success would be *independent incremental prediction/transportability of existing HRF methods*, not discovery of a never-used autonomic biomarker. Future invention work requires the [novelty-reset gate](NOVELTY_RESET_2026-11-15.md).

**No prospective survival model is yet validated or preregistered in an independent research registry.**
