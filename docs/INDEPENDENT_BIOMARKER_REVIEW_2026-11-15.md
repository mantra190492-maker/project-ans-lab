# Project ANS — Independent biomarker review, agents 3–7

**Date:** 2026-11-15 (UTC)  
**Reviewer:** Project ANS independent in-chat scientific analysis  
**Source handling:** Primary published papers, original trial abstracts and provider dataset documentation were checked independently. This review is not a systematic review, registered protocol, clinical assessment, regulatory clearance, or outcome-model execution. Findings from Agents 1 and 2 are separately audited in this repository.  
**Budget:** USD 0 incremental cash cost for the analysis and lightweight CI tests; GitHub-hosted minutes/storage limits still apply.

## Executive decision

**Proceed with a reproducible measurement and outcome-prediction program.** Do not build or market an autonomic-age clock or composite Autonomic Resilience Index (ARI) now. Our highest-feasibility test is whether **heart-rate fragmentation (HRF)** improves future-event prediction *beyond* clinical variables, resting heart rate and standard HRV in a clinically appropriate population. The leading long-term differentiation possibility is **dynamic recovery**; BRS remains a **measurement-validation track**.

**Evidence taxonomy**
- **Verified published association**: observed in named clinical study; does not imply causal effect or external transportability.
- **Engineering feasible**: code runs on test data/waveforms; not evidence of biomarker validity.
- **Hypothesis only**: mechanism or untested added value remains speculative.
- **Unusable now**: requisite exposure/outcome or reference labels not accessible/verified.

## Agent 3 — Biomarker discovery scientist

| Rank for Project ANS | Candidate | Measurements / reproducible definition | Most relevant evidence | Constraints / decision |
|---|---|---|---|---|
| 1 | **Heart-rate fragmentation: PIP** | From annotated, correctly timed consecutive *normal-to-normal* intervals, map successive differences to ternary symbols: −1 if ΔNN below −quantization, 0 within the band, +1 above. **PIP** is 100 × fraction of adjacent symbol transitions. Reference paper used ±4 ms at 256 Hz; test ±5 ms at 200 Hz and preregister sensitivity to discretization. | Costa et al. 2018, MESA, 1,963 people, 72 incident CV events; per-SD PIP HR about 1.43 (1.16–1.76) in adjusted model. | **Immediate replication hypothesis**, already published; avoid AF/pacing, ectopy, missing-beat interpolation, differing sample rates and sleep/wake confounding. |
| 2 | **W1 (fluent word fraction)** | Fraction of five-NN-interval windows (four consecutive interval changes) with **exactly one** ternary sign change. Underlying 2018 paper reports competitive prognostic association. | Costa et al. 2018. | Secondary correlated fragmentation feature, **not** an automatic independent biomarker. |
| 3 | **HRR10–20 following active stand** | HR(t=10 s) − HR(t=20 s), aligned to *measured stand onset*; verify 10-second averaging conventions. | McCrory et al. 2016, 4,475 TILDA adults ≥50, 138 deaths, mean follow-up 4.3 yr. | Potentially useful and more dynamic, but exact waveform+outcome cohort unavailable to our project today. |
| 4 | **Spontaneous BRS** | SBP→subsequent RR sequence slope, spectral transfer gain with coherence, and cross-correlation: report method, lag, accepted sequences and agreement, not one uncalibrated composite. | EuroBaVar 2004; Rotterdam dementia association in selected subgroup. | **Hold clinical use** until reference comparison and QC. |
| 5 | **Resting HRV (RMSSD/SDNN)** | Established screened-NN time-domain measurements; 5-min vs Holter 24-h cannot be conflated. | Established literature; baseline for all new experiments. | **Baseline comparator, not innovation**. |

No single marker is universally "better"; this ranking is about *near-term testability under the existing resources*. HRF is not necessarily autonomic-specific: sinus-node and other non-autonomic contributors remain competing explanations.

**Novelty:** HRF was published by Costa et al. in 2017/2018; the 2023 Schumann autonomic age model already used 29 features and yielded r≈0.81 on an 884-person subset of the same Autonomic Aging cohort. A new 2025 cardiovascular autonomic age gap study also exists (PMID 41138205). PpgAge in 213,593 participants uses consumer wrist PPG (PMID 41115881); ECG-age mortality prediction exists at >1.5 million patients. **Our possible differentiator is calibrated, transferable *incremental prognostic information*, NOT repackaged age prediction.**

### Implemented HRF numerical gate

See [anslab/heart_rate_fragmentation.py](../anslab/heart_rate_fragmentation.py), [synthetic unit tests](../tests/test_heart_rate_fragmentation.py), and [HRF GitHub workflow](../.github/workflows/hrf-measurement-gate.yml). They ensure:
- up-front declaration that NN labels have been validated as sinus rhythm;
- physiologically plausible intervals and ≥95% clean intervals for software research gate;
- **no connecting pairs across excluded intervals**, and explicit quantization setting;
- PIP, W1 and RMSSD computed with clean, physically contiguous differences only;
- no claim of performance on MUSIC Holters or future outcomes.

**These are software checks only.** A true accuracy benchmark requires expert-labeled ectopic/AF/paced recordings and a frozen annotation/quantization protocol.

Sources:
- Costa 2018 [PMCID PMC6129761](https://pmc.ncbi.nlm.nih.gov/articles/PMC6129761/), DOI 10.3389/fphys.2018.01117.
- Mechanistic counterpoint: [Heart rate fragmentation gives novel insights into non-autonomic mechanisms](https://pmc.ncbi.nlm.nih.gov/articles/PMC7457638/).
- Schumann et al. 2023 [DOI 10.3389/fnagi.2022.899249](https://www.frontiersin.org/journals/aging-neuroscience/articles/10.3389/fnagi.2022.899249/full).
- CAA gap [PMID 41138205](https://pubmed.ncbi.nlm.nih.gov/41138205/).
- PpgAge [PMID 41115881](https://pubmed.ncbi.nlm.nih.gov/41115881/).
- ECG age mortality [Nature Communications 2021](https://www.nature.com/articles/s41467-021-25351-7).

## Agent 4 — Baroreflex measurement validator

The **12 provisional BRS outputs among 20** processed adult recordings are **software-gated estimates**, not validated BRS. The four-record Fantasia comparison tested R-peak detection only.

**Strong counterevidence:** In 97 participants, Lipman et al. (2003) compared five spontaneous BRS estimators to pharmacological modified-Oxford baroreflex gain. Methods correlated in some circumstances but exhibited large limits of agreement and problematic low-gain validity. A higher correlation across spontaneous methods therefore does **not** establish physiological truth.

**EuroBaVar (2004)** compared 21 procedures in 21 people; sequence vs spectral methods varied in lag, thresholds and estimates. A rigid identical numerical cutoff across methods is not defensible.

### Mandatory validation steps

1. Validate R-peaks and arterial systolic peaks separately against annotated/manual ECG and BP events; quantify precision, recall, onset error and physiologically implausible alignment; inspect cross-device calibration and sampling.
2. Freeze causal timing: SBP changes should precede the heart-period response by prespecified beat lags; evaluate lag 0 vs 1 vs 2 and direction. Compare matched beats with a **time-shifted or surrogate BP/RR pairing** to quantify spurious positive sequences.
3. Implement at least **two named BRS estimators** using published definitions (sequence + LF transfer, coherence gating) and add cross-correlation as sensitivity analysis. Avoid presenting spontaneous values as a pharmacological-Oxford reference.
4. Report per-subject missingness, sequence counts, insufficient-quality reasons, split-half/internal consistency and method agreement, with confidence intervals. **Split-half ≠ repeatability across sessions.**
5. Check respiration estimation or measured respiratory channel where available; vary breathing frequency, posture, device and signal duration. Respiration is **not recorded** in Autonomic Aging.
6. Explicitly include participants with low slopes and insufficient sequences in yield denominators; never silently analyze only cases that return numeric estimates.

**Stop:** If surrogate series routinely produce comparable slopes, if reference/alternative estimators disagree severely, or if measures are unstable to minor timing corrections, no clinical BRS modeling.

**No automatic requirement that BRS must decrease monotonically in every sex/device/age bin:** age pattern is a hypothesis, not an analytical-validity reference standard.

Sources:
- Lipman 2003, [PMID 12975383](https://pubmed.ncbi.nlm.nih.gov/12975383/), DOI 10.1161/01.HYP.0000091370.83602.E6.
- EuroBaVar, [PMID 14500269](https://pubmed.ncbi.nlm.nih.gov/14500269/), DOI 10.1152/ajpregu.00709.2002.
- Ma et al. Rotterdam 2025 journal issue, [PMCID PMC11714963](https://pmc.ncbi.nlm.nih.gov/articles/PMC11714963/). Observational BRS–dementia association especially in **non-antihypertensive users**, 1,819 people, median 14.8-year follow-up; interaction hypothesis requires replication.

## Agent 5 — Clinical prediction statistician

The **MUSIC v1.0.1** open chronic-heart-failure data are our current inexpensive clinical-outcome entry point. GitHub's public metadata feasibility report contains **992 patients**; all have coded follow-up and mortality categories; only **587 (59.2%)** have recorded RMSSD/SDNN, leaving **405 (40.8%)** missing. Holter rhythm is recorded for **933** and 176 have percutaneous revascularization alone or combined (not proof of a stent). The 24-hour Holter cohort includes 936 files; full waveform archive is very large, so use small annotated subsets first.

*Critical finding:* Among existing 992 MUSIC records, **94 sudden cardiac deaths, 111 pump-failure deaths and 61 noncardiac deaths** are coded; the initial 266 deaths are NOT the event count in the HRV-complete, sinus-only eligible sample. We must establish censoring from **Exit of the study** codes: 0 survivor, 1 lost, 2 transplanted, 3 death. Cause-of-death 0 is not sufficient for all-cause event status. Avoid post-baseline covariates and retrospectively computed outcome flags: v1.0.1 removed two potentially misleading derived variables.

### Frozen question for first clinical study

> Among adults with chronic heart failure who have sufficiently clean baseline **sinus-rhythm** Holter ECG, does PIP/W1 improve out-of-sample prediction of **all-cause mortality** beyond age, sex, heart failure severity, prior disease, relevant treatment, mean heart rate and standard HRV?

**Model 0:** parsimonious clinical baseline (age, sex code, NYHA, LVEF, diabetes/ischemic history, beta-blocker; other predictors only if sufficient events).

**Model 1:** model 0 + mean HR + log RMSSD (or log SDNN; preselect one).

**Model 2:** model 1 + **PIP** from verified sinus NN, quantization prespecified. W1 is a *secondary* test after multiplicity control.

**Outcomes:** primary all-cause death with proper censoring. Secondary sudden/pump-failure cardiac death requires correctly handling competing risks.

**Statistical design:** patient-level separation and no multiple segments across train/test; appropriate survival-validation splits; nested transformations/imputation within training folds; report complete-case selection bias, events per parameter, calibration, C-index, 95% uncertainty interval for change, and decision-curve utility. Favour pre-specified risk horizon and bootstrap-corrected performance; tiny improvements (e.g., apparent ΔC≈0.005 with uncertainty spanning zero) are **not** a useful result. Never use a significant PIP hazard ratio alone to announce clinical value.

**No modeling has been performed in this review.** The [MUSIC outcome protocol](MUSIC_OUTCOME_MODEL_PROTOCOL_001.md) is a project draft, not an independent registry or published preregistration.

**Failure criteria:** inadequate sinus/NN event count after filtering, large missingness differential, no robust incremental discrimination/calibration, failure to replicate in an independent prospective cohort. At that point, narrow the hypothesis or pivot; do not force an ARI score.

Sources:
- [MUSIC dataset v1.0.1](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/); [coding dictionary](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/subject-info_codes.csv); [baseline variables](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/subject-info_definitions.csv).
- [MUSIC aggregate audit](../reports/MUSIC_METADATA_AUDIT.md).

## Agent 6 — Autonomic recovery / physiologic resilience researcher

Dynamic response is the most plausible **long-term differentiation direction**, but current data access and harmonization are harder than HRF.

| Dynamic measurement | Definitional endpoint | Longitudinal evidence | Feasible dataset / gate |
|---|---|---|---|
| **Active-stand HRR10–20** | HR(10s) − HR(20s) after time-aligned stand onset, with agreed smoothing and epoch convention; contextualize BP nadir/recovery | McCrory et al. 2016: 4,475 TILDA aged ≥50, 138 deaths, ~4.3 yr. Each 1 bpm slower HRR10–20 associated with ~6% greater mortality hazard after adjustment. | TILDA challenge waveform/outcome data not openly available to our GitHub project. MIDUS has challenge summaries but resolution for exact 10–20 s not verified. |
| **Early exercise HRR10** | HR at exercise termination − HR at 10 s after stop; report exercise capacity and active/passive recovery protocol | UK Biobank analysis of **40,727** adults, 536 deaths over median six years; early HRR (10 s) was independently prognostic in that study. | Raw synchronized exercise data and long-term outcomes require cohort access and protocol consistency. Not derivable from resting MUSIC/Autonomic Aging. |
| **Orthostatic BP recovery / cerebral autoregulation** | Baseline SBP, post-stand nadir, SBP deficit at 30/40 s and integral of pressure deficit; derive only from actual timestamped challenge | Mechanistic/functional hypothesis; outcome evidence for exact composite is not established here. | **CDED** open PhysioNet: 69 older diabetic/control participants, 41 with two-year follow-up; **CVES** stroke/control includes stand/tilt ECG/BP. Verify waveform and outcome metadata, then engineering pilot. |

**Controls:** stand onset timing, 5–10 min baseline posture, respiratory pace, standing assistance, beta blockers, diabetic autonomic neuropathy, pregnancy, menopausal status, child development, athletic training and BP device offset.

**Falsification:** if dynamic recovery offers no reliable test–retest measurement or no better held-out prediction than baseline risk + heart rate + conventional HRV, it fails the proposed added-value test. A large within-subject change without meaningful outcome relevance is insufficient.

Sources:
- [McCrory et al. 2016](https://pubmed.ncbi.nlm.nih.gov/27330018/), DOI 10.1161/CIRCRESAHA.116.308577.
- [Exercise HRR10 in UK Biobank](https://pubmed.ncbi.nlm.nih.gov/29622586/), DOI 10.1161/JAHA.117.008341.
- [CDED](https://physionet.org/content/cded/1.0.1/) and [CVES](https://physionet.org/content/cves/1.0.0/).
- [MIDUS 2 biomarker](https://www.icpsr.umich.edu/web/ICPSR/studies/29282).

## Agent 7 — Scientific skeptic and novelty auditor

### Ranked fatal/major objections

1. **Incremental prognosis may be negligible:** adding HRF or BRS could change C-index by almost nothing after conventional clinical risks and heart rate.
2. **Only 587 MUSIC records have traditional HRV**. Sinus rhythm, true NN quality, medication, missing-not-at-random and events may shrink the eligible cohort dramatically.
3. **MESA fragmentation already published:** even a positive result would replicate/transport an existing marker, not establish new IP or biological mechanism.
4. **Another 2023 autonomic age model and 2025 CAA age-gap study used the same source data:** a newly branded age score lacks scientific novelty.
5. **BRS analytical validity unclear:** spontaneous BRS vs pharmacological reference can disagree, especially low gain; 12/20 provisional yield could reflect strict gating, bad alignment, physiology or insufficient recording quality.
6. **Arrhythmia/ectopy corrupt HRV/HRF:** pathological beat patterns can inflate variation; training fitness also changes baseline HR without implying delayed ageing.
7. **Cross-cohort instrumentation:** 256 Hz MESA, 200 Hz MUSIC, 1,000 Hz interpolated BP in Autonomic Aging; identical symbol thresholds are not inherently equivalent.
8. **Dynamic outcomes inaccessible/expensive:** TILDA and Rotterdam longitudinal signal datasets are controlled; available CDED is tiny and suffers follow-up attrition.
9. **Interventions do not establish longevity:** INOVATE-HF randomized 707 found VNS failed composite death/HF endpoint (30.3% vs 25.8%, p=0.37). BeAT-HF 323 found neutral CV death/HF morbidity (rate ratio 0.94, 95% CI 0.57–1.57); symptoms improved. These trials involve advanced heart failure and do **not** falsify every possible healthy-ageing intervention.
10. **Causal evidence weak:** Mensah-Kane et al. 2021 Mendelian randomization found no convincing causal effect of exercise HR recovery on the selected CV outcomes; genetics instruments and populations still limit inference.
11. **Exercise can change a marker without proving survival benefit:** Etayo-Urtasun et al. 15 RCTs in older adults found pooled RMSSD increase (SMD 0.636, CI 0.014–1.258), but neither SDNN nor BRS had statistically significant pooled change. An autonomic shift cannot be equated with a causal longevity benefit.
12. **Special populations lack verified phenotype labels:** pregnancy/postpartum, menopause, true stents, athletes and children cannot share adult healthy-baseline cutoffs. The existing 20-person PhysioNet cohort cannot validate any of these groups.

### Explicit stop / pivot criteria

**Proceed** only when (i) feature calculation is tested on labelled real waveforms, (ii) appropriately eligible patient sample and outcome codes support a reliable analysis, (iii) the added marker yields useful, uncertainty-bounded, calibrated out-of-sample predictive improvement, and (iv) independently replicated.

**Narrow to ECG-only monitoring** if BRS reference comparison/quality is inadequate; **narrow to challenge-response physiology** if fragmentation offers no incremental prognostic value. **Stop claim of a clinically useful biomarker** if independent replication fails or risk-model calibration is unsafe. Do not reinterpret association as causation.

**IP guardrail:** broad existing work includes HRF 2017–2018, autonomic age ML 2023/2025, ECG-age (CODE network, 1,558,415 patients), PpgAge (213,593 participants), and pre-existing wearable HRV patents. This is an initial literature/prior-art review, **not** a professional freedom-to-operate opinion. Novelty may be in the validated clinical workflow/context, not in a renamed index.

Sources:
- [INOVATE-HF PMID 27058909](https://pubmed.ncbi.nlm.nih.gov/27058909/), DOI 10.1016/j.jacc.2016.03.525.
- [BeAT-HF PMID 38606555](https://pubmed.ncbi.nlm.nih.gov/38606555/), DOI 10.1002/ejhf.3232.
- [MR PMID 33679875](https://pubmed.ncbi.nlm.nih.gov/33679875/), DOI 10.3389/fgene.2021.569323.
- [Exercise RCT meta PMID 41264119](https://pubmed.ncbi.nlm.nih.gov/41264119/), DOI 10.1007/s40279-025-02357-5.
- [Autonomic age paper](https://www.frontiersin.org/journals/aging-neuroscience/articles/10.3389/fnagi.2022.899249/full); [CAA gap PMID 41138205](https://pubmed.ncbi.nlm.nih.gov/41138205/).
- [CODE ECG-age study](https://www.nature.com/articles/s41467-021-25351-7); [Apple PpgAge](https://www.nature.com/articles/s41467-025-64275-4).

## Independent review versus external Agents 1 and 2 — adjudication

| Question | Agent 1 | Agent 2 (skeptic PDF) | Independent decision |
|---|---|---|---|
| Main objective | Measurement reproducibility and prediction | Prediction, with skeptical constraints | **AGREE:** no longevity claims |
| Best immediately testable biomarker | HRV/BRS panel; consider dynamic | HRF/PIP and recovery | **HRF/PIP first**, because MUSIC has longitudinal outcomes, with strong rhythm/quantization controls |
| Why not launch age score | Requires clinical validation | Prior art (same data + ECG/wrist clocks) | **AGREE:** 2023/2025 same-dataset autonomic age work makes an age score low novelty |
| BRS benchmark | Aim for 2 estimators r≥0.70 | Require multi-method agreement and surrogates | **Stronger:** do not confuse multi-estimator correlation with truth; require reference comparison and lag checks |
| Best clinical dataset | SHHS, subject to access | MUSIC, MIDUS, SHHS, CDED | **MUSIC first** for cheap accessible outcomes; SHHS later with rights/access verification |
| Dynamic stress recovery | Hypothesis | TILDA, MIDUS and CDED leads | **High-priority parallel**, but no valid longitudinal dynamic test yet |
| Special populations | Separate phenotypes | Separate norms and missing labels | **AGREE:** defer subgroup claims until observed variables exist |
| Reason to stop | Low marginal prediction or QC failure | Missing data, prior art, no causality | **No validated biomarker today**; prioritize transparent null results |

## Decision register: next actual experiments

**Gate 1 — HRF software (already implemented):** run synthetic PIP/W1/quantization/rhythm-quality tests under `ANS-001 HRF Measurement Gate`; successful run only proves software calculations on synthetic inputs.

**Gate 2 — ECG/NN external validity:** on small recorded MUSIC Holter subsets, verify annotation/ectopy/AF/pacing eligibility against manually reviewed signals. Do not commit patient-level data or raw waveforms.

**Gate 3 — MUSIC outcome modeling:** freeze follow-up/censoring and clinical-model covariates *before looking at outcome associations*, quantify exclusion/event-count impact, calculate CI and calibration on held-out patients. No full 90 GB waveforms needed for feasibility.

**Gate 4 — BRS precision and surrogate comparison:** on a small annotated ECG/BP sample, freeze SBP→RR lag, use LF transfer and sequence estimates, inspect silent missingness/respiratory limitations; do not scale all 1,121 recordings as first step.

**Gate 5 — dynamic public data:** inspect CDED/CVES exact waveforms, stand onset markers and baseline/follow-up definitions; feasibility only until outcome data and reliable challenge alignment exist.

**Gate 6 — multi-agent adjudication:** when external Agents 3–7 arrive, append their claim IDs, source verifications, contradictions, and tested repository artifacts to the comparison board. Do **not** modify historical negative results.

### Hard current status

- **Literature library:** 46 *bibliographic* entries; not a systematic validated evidence review.
- **Adult resting feasibility:** 20 records processed; 19 automatic ECG QC passes, 12 provisional BRS outputs; **0 validated BRS biomarkers**.
- **External R-peak check:** four selected Fantasia segments at 150 ms tolerance (F1 1.000; timing medians 4/8/12/8 ms); not sufficient for broad ECG accuracy.
- **MUSIC:** 992 metadata rows; 587 conventional HRV-complete; **0 outcome models fitted**.
- **HRF PIP/W1:** code + unit tests committed; cloud outcome needs verification.
- **Intervention / lifespan:** **no evidence in this project** that changing an autonomic marker prolongs life.
