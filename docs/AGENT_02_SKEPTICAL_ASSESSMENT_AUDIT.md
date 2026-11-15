# Project ANS — Agent 02: skeptical research assessment and integration decision

**Date:** 2026-11-15. **Input:** founder-supplied 19-page PDF, *Project ANS — Skeptical Research Assessment*, Nov 15 2026. This is an external-agent synthesis, not original experimental evidence. The external agent did not inspect our private 46-paper archive, 20-participant waveform data, or the newer Fantasia benchmark.

## Board-level decision

**ACCEPT:** move to validated measurement plus meaningful prospective outcomes, introduce heart-rate fragmentation (HRF) and challenge/recovery endpoints, and explicitly test incremental value over age/HR/HRV/comorbidities. Don't sell "autonomic age" as novelty.

**ACCEPT with constraints:** MUSIC, MIDUS, SHHS and PhysioNet CVES/CDED as *different study designs*, not interchangeable labels. Follow dataset licenses, access agreements and outcomes availability.

**REJECT as unproven:** all spontaneous BRS values are equivalent to pharmacologically assessed baroreflex gain; change in HRV/BRS causes longer lifespan; our 12/20 provisional BRS yield is definitely a "pipeline fault"; any monotonically declining age effect is necessary for a valid estimator; unrecorded pregnancy/stents/menopause/athlete status is negative; a full 1,121-record run proves biological ageing.

## Five findings worth prioritizing

1. **MUSIC v1.0.1**: [PhysioNet](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/), DOI **10.13026/z3m7-rf58**. **992** chronic heart-failure participants, **936** Holter records, baseline clinical + medication + mortality outcome data; 90.2 GB uncompressed in total. The public **subject-info.csv** (roughly 301 KB) explicitly includes fields for age, sex, BMI, prior MI, **prior revascularization**, cardiac rhythm, beta blockers, existing RMSSD/SDNN, follow-up period and cause of death. The [official categorical dictionary](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/subject-info_codes.csv) defines prior revascularization **0 none, 1 percutaneous, 2 surgical, 3 both**. **Percutaneous is NOT proof of coronary stent implantation**. Not a healthy population. This is the leading LOW-COST data-inventory target and a possible exploratory CVD prognosis benchmark.
2. **MIDUS 2 Biomarker / mortality**: [ICPSR 29282](https://www.icpsr.umich.edu/web/ICPSR/studies/29282), plus [ICPSR 37237](https://www.icpsr.umich.edu/web/NACDA/studies/37237). Study descriptions include heart-rate variability, beat-to-beat BP, respiration and a cognitive and orthostatic challenge. Mortality file reports **2,822 known decedents through 2025** (updated Aug 13 2026). **Important: this mortality file is a decedent dataset; it cannot serve as a full denominator for survival analysis without a linked core roster, survivor/censoring status and verified observation times.** Exact challenge-stage variable names, raw signals and reproductive labels remain **UNVERIFIED**; inspect codebooks first.
3. **SHHS**: [NSRR](https://sleepdata.org/datasets/shhs) overnight PSG ECG and cardiovascular endpoints, 5,804 adults with available recordings (6,441 initially enrolled); second PSG in 3,295. Access via review/DUA; waveform archive ~356 GB, unaffordable to download wholesale. Test access and a small approved subset **before** analysis. HRV/HRF possible; **no verified continuous beat-to-beat BP** for BRS.
4. **Novak CDED**: [PhysioNet](https://physionet.org/content/cded/1.0.1/), DOI **10.13026/00bm-0x81**. **69** diabetes/control participants aged 55–75 with challenge ECG, BP, respiration, balance, cognition; **41** completed two-year follow-up. Small, incomplete, but **counterexample to the PDF's categorical claim that no open beat-to-beat BP with any outcome follow-up exists**. Whether the exact follow-up variables are accessible in released files remains to be checked. Separate [CVES stroke/control](https://physionet.org/content/cves/1.0.0/) has **60 stroke vs 60 controls**, sit-to-stand/head-up tilt and ECG/BP/cerebral waveforms; chiefly cross-sectional, suitable for engineering challenge metrics, not longevity.
5. **Heart-rate fragmentation (HRF)**: Costa et al. 2018 [doi:10.3389/fphys.2018.01117](https://pmc.ncbi.nlm.nih.gov/articles/PMC6129761/), a prospective MESA analysis of **1,963** PSG heart-rate series with **72** incident CVD events, found association of fragmentation with events after adjustment while conventional HRV did not. **This is prior art, not a novel biomarker.** Prespecify HRF PIP algorithm, protect against ectopy/noise, and evaluate replication in an outcome cohort; do NOT compute PIP directly from uncorrected R-peaks.

## High-impact negative/qualified findings to preserve

- [Ma et al., Rotterdam, PMID 39670317](https://pubmed.ncbi.nlm.nih.gov/39670317/), published **online Dec 2024**, journal issue **Feb 2025**; baseline BRS and dementia/survival association over median 14.8 years in **1,819** older adults. Association was seen in those **not taking antihypertensive drugs**, not demonstrably general across users; the subgroup finding needs replication. Medication should be a **stratification/interaction** concern, not only a regression covariate.
- [Lipman et al., PMID 12975383](https://pubmed.ncbi.nlm.nih.gov/12975383/) compared 5 spontaneous BRS indices to a pharmacologic reference in 97 volunteers and found clinically concerning disagreement, particularly low-gain individuals. Correlation between 2 spontaneous methods is NOT equivalent to calibration against true gain.
- [McCrory et al., TILDA, PMID 27330018](https://pubmed.ncbi.nlm.nih.gov/27330018/), 4,475 participants: HR recovery following active stand associated with 4.3-year mortality risk; **time-resolved 10–20-second stand response** not reproducible from generic resting ECG or coarse aggregate challenge periods.
- Intervention trials in severe HF and null genetics **do not prove** all ANS regulation is biologically noncausal or interventions in otherwise healthy ageing cannot work. They argue against jumping from marker improvement to longevity benefits.

## Confounder and transportability priorities

Age, resting HR, BMI, sex/reproductive status *when measured*, device, respiration, ectopy/AF, BP, diabetes, medications (especially beta blockers/antihypertensives), smoking, sleep apnoea, fitness, baseline disease, measurement posture. Do not infer stent implantation from percutaneous revascularization or pregnancy/menopause from sex/age.

## Concrete work program

**Gate A (now):** Fetch and parse **only** MUSIC `subject-info.csv`, with codes/definitions. Audit missingness for prior revascularization, AF/rhythm, RMSSD, SDNN, beta blockers, follow-up and cause of death. Report aggregate counts and avoid committing person-level records. No physiological model fitting or associations until data scope, censoring and leakage prevention are specified.

**Gate B:** Review MIDUS 2 and 2025 mortality **codebooks** for exact participant join key M2ID, events *and survivor roster/censoring*, and timings of stand and stress indices; flag if recovery cannot be resolved at 10–20 seconds.

**Gate C:** Validate ECG/BP features and a BRS reference/alternative estimator on external annotated waveforms. The four-record Fantasia benchmark established narrow ECG beat-detection feasibility but **not BP/BRS analytical validity**.

**Gate D:** Preregister pre-specified outcome models: clinical baseline (including disease severity, medication, heart rate and standard HRV) vs adding PIP/fragmentation, adjusted HRV, then BRS if validated waveform+BP data exist. Report calibration, C-index, discrimination confidence intervals, missingness, subject-level holdout, survival censoring. No prospective outcome claim from cross-sectional ages.

**Gate E:** Make special-population branches independent (pregnancy/postpartum, menopause, pediatric, athlete, CAD/PCI) until observed annotations exist. No single "autonomic age" scale for all groups.

## Source-integrity caveats

The external PDF has useful leads and legitimate sources, but some labels are too absolute: no open BP+follow-up data; BRS yield "definitely" a fault; negative direct-neuromodulation trials imply no causality in healthy ageing; monotonic age pattern required for valid BRS. These statements must be qualified as above.

The full 1,121-record waveform run costs compute/download and should be **gated by method validity** rather than automatic mass ingestion. The current private GitHub project has already demonstrated a 20-person engineering pilot, 19 preliminary ECG QC passes and 12 software-gated provisional BRS values: none is a clinically validated BRS reference.
