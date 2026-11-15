# HYPOTHESIS SHHS-HRF-001 — Prospective cardiac-autonomic change

**Registered in repo:** 2026-11-15. **Status: FROZEN RESEARCH QUESTION, NOT YET OSF-PREREGISTERED.** No access to restricted SHHS or MrOS participant data. Do not call this a validated autonomic dysfunction biomarker.

## Single research question

Does **overnight heart-rate fragmentation**, measured using Costa's reference PIP definition at Sleep Heart Health Study (SHHS) visit 1, predict **within-person deterioration in an independently specified respiration-linked cardiac autonomic proxy** from visit 1 to visit 2, **above and beyond** the earlier physiological measure, age, sex, mean heart rate, conventional HRV and standard clinical covariates?

**What this is NOT:** It cannot establish autonomic neuropathy, degeneration of a specific nerve, Parkinson's disease, clinical generalized ANS failure, or a novel therapeutic intervention. A change in ECG-derived vagal proxy is not equivalent to validated clinical autonomic deterioration. The aim of this experiment is to find evidence worth testing against clinical reference standards.

**Novelty:** Direct exact-study prior art NOT yet exhausted. HRF itself is established; observed age-related declines in vagal indices, fragmented rhythms and orthostatic response prognosis are known.

## Primary data and feasibility gates

- SHHS enrolled **6,441 people** (1995–1998); **3,295 had second polysomnogram** (2001–2003). Neither number is the number of quality-eligible paired ECG signals.
- SHHS1 bipolar ECG was typically **125 Hz**; SHHS2 ECG **250 Hz**. This is a major non-biological confounder, including QRS jitter, ectopic-detection performance and the PIP zero rule. SHHS1 *most* recordings 125 Hz; inspect actual record headers.
- Overnight EEG, airflow, thoracic and abdominal belts, sleep stages and respiratory events may enable **stage-matched respiration-conditioned analysis**. Require actual data dictionary, channel quality and within-subject overlap to prove a usable endpoint.
- MrOS sleep visits (2003–05 and 2009–12): NSRR documents **1,026 repeat PSG sleep measures** among 2,911 baseline participants. Access and comparable ECG signal quality must be verified; **not guaranteed replication**.
- DUA required; **never put controlled SHHS/MrOS EDFs, ECGs, beat annotations, person-level clinical variables, subject ID crosswalk, patient-level output tables or derived individual data into GitHub, GitHub Actions logs/artifacts, public websites or general cloud AI connectors**. Public GitHub stores source code, protocol and only disclosure-approved aggregate summaries. Source controls may also require data-specific restrictions on derived features.

## Locked predictor

1. **Primary candidate:** Costa-original definition of PIP from native R peak timestamps and separately QC-labelled sinus beats, computed in a fixed, preregistered sleep-stage window. Use [reference-equivalent independent Python method](../anslab/hrf_costa_reference.py). Three tiny official public test series reproduce all integer counts, [comparison report](../reports/HRF_DIFFERENTIAL_TEST.md).
2. **Comparator:** Legacy provisional PIP is *not* acceptable as primary; original 4ms deadband/whole-triplet denominator differs from author code, as demonstrated by our [corrected Fantasia pilot](../reports/FANTASIA_HRF_PILOT.md).
3. **QC:** External manual/algorithmic beat validation and arrhythmia exclusions; exclude AF/pacing, frequent ectopy, non-comparable sleep windows, severe signal corruption; do not bridge beat gaps. No numeric thresholds are finalized until a blinded ECG-QC feasibility stage.

## Locked outcome concept; final operational choice blocked until data inspection

A participant-specific **visit-2 decline in respiration-linked cardiac vagal modulation**, measured using a precisely operationalized, breathing-controlled **respiratory sinus arrhythmia (RSA) feature** during comparable stable N2 sleep segments, relative to visit-1 baseline. ECG-only RMSSD decline may be reported only as a **secondary non-independent proxy** and must never be called ANS deterioration. Rationale: using respiration as an external physiological signal may support mechanistic interpretation, but RSA is still not a pharmacological vagal or clinical autonomic reference.

Before opening visit-2 outcomes, verify that respiratory phase and amplitude can actually be reconstructed from SHHS airflow or thoracic/abdominal 10 Hz channels, and that N2 stages, apnoeas and arousals are matched or adjusted. If not feasible, **declare the chosen endpoint invalid, stop the study, and write a documented preregistered amendment before examining any visit-2 change data. Do not substitute raw RMSSD after seeing outcomes.**

## Guardrails against false discovery

1. **Sampling harmonization:** Process both visit waveforms at their native sample grids for QRS detection. Recompute/round visit-2 peak times onto a prespecified **125 Hz grid** (8 ms) *as an additional sensitivity* and compare with native 250 Hz analyses. This cannot recover SHHS1 precision or eliminate all different-device bias. Include within-cohort same-visit simulation of quantization effects.
2. **Participant matching:** Same anonymous participant across visits with individually verified ECG, sleep stages and respiratory measurements. Handle missing visit-2 data and selective attrition (survivorship and missing not at random).
3. **Outcome/predictor separation:** Extract visit-1 predictor blind to visit-2 values. Lock QC, sleep windows, respiratory feature, reference formula, exclusions and thresholds before linkage.
4. **Baseline adjustment:** Include visit-1 RSA estimate to guard against regression to the mean. Also age, sex, baseline mean HR, conventional SDNN/RMSSD or HF-HRV as appropriate, baseline AHI/oxygenation, BMI, diabetes, hypertension, beta blockers/other relevant medications, and sleep-stage mixture, subject to measured variable availability and sample-size feasibility.
5. **Nonlinear and direction checks:** Predefine baseline severity adjustment, statistical effect estimate, calibration, out-of-sample performance and CIs; negative controls test time-grid artifacts and sham outcomes. Compare **baseline model vs baseline+PIP**. Do not fish over many cutoffs or markers.
6. **Interpretation:** If only ECG RSA decline is predicted, result is *prediction of change in a cardiac vagal proxy*, not proof of future clinical autonomic neuropathy. Clinical validation remains G3 blocked.
7. **Replication:** MrOS only if an independent sleep ECG+respiratory proxy and consistent longitudinal follow-up are both available under appropriate data permissions.

## Explicit rejection gates

- **No eligible paired ECG + breathing cohort, no robust native sampling correction, or no stable respiration-conditioned endpoint:** STOP the SHHS experiment (data feasibility failure).
- **Any apparent PIP association is fully attributable to sample resolution, sleep-state or rhythm confounds:** REJECT.
- **PIP does not improve held-out prediction over clinical + baseline RSA/HRV:** REJECT additional predictive usefulness, report the null.
- **Results cannot be validated against independently assessed clinical ANS dysfunction:** DO NOT promote to a clinically validated deterioration marker even if proxy forecasting works.

## Exact sequence

1. **DONE:** Costa official source executed on three public test series, and independent PIP/PNNSS/PNNLS integer-count outputs all matched ([numerical report](../reports/HRF_DIFFERENTIAL_TEST.md)).
2. **DONE:** Recomputed three publicly annotated Fantasia records with reference-style PIP side-by-side vs older algorithm. Fourth excluded for NN rhythm QC. This is *not* validation of the SHHS predictor.
3. **USER/RESEARCH INSTITUTION:** Seek NSRR SHHS/MrOS authorization and a compliant analysis environment. The assistant does not have authenticated approval and cannot accept a DUA for the user.
4. **PENDING:** Confirm paired waveforms, annotations, respiration, stage matching, subject exclusions, data-use constraints, and prior art. Only then freeze a full OSF preregistration **before looking at visit-2 outcomes**.
5. **PENDING:** Fit the preregistered analysis locally in the authorized environment; aggregate audit results without restricted values, replicate as feasible.

## Sources

- [SHHS NSRR overview](https://sleepdata.org/datasets/shhs) and [sampling frequencies / study methods](https://sleepdata.org/datasets/shhs/pages/full-description.md).
- [MrOS NSRR overview](https://sleepdata.org/datasets/mros/pages/dataset-introduction.md).
- [Costa's HRF author source, 2024, DOI 10.13026/0mzj-gn98](https://physionet.org/content/heart-rate-fragmentation-code/1.0.0/).
- [Original Costa HRF paper 2017](https://doi.org/10.3389/fphys.2017.00255).
