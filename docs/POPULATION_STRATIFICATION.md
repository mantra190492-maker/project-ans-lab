# ANS-001 — Population and physiology stratification protocol

**Decision:** Core healthy-adult physiology and five separate external-validity branches. No pooling into a single biological-age score before population-specific validation.

## Why the 20-person pilot cannot answer the founder's questions

The open [PhysioNet Autonomic Aging dataset](https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/) records resting ECG and continuous BP from 1,121 screened healthy adult volunteers. It provides anonymized **age group, recorded sex code, BMI, device and recording length**, but not gestational state, menopausal stage, coronary interventions, athletic training history or pediatric developmental milestones. The original paper excluded health conditions and medications that might influence cardiovascular function: [Schumann & Bär 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8943176/). This is a selection restriction, **not** patient-level confirmation that every unrecorded condition is absent.

Never label an unmeasured condition as "no", "healthy control for that condition", or impute it from chronological age or sex code. A female-coded record does not disclose pregnancy, menopause, cycle phase, hormone therapy, or gender identity. Do not treat a high HRV as evidence of longevity or a low HRV as accelerated ageing.

## Research branches and design gates

| Branch | Required ground-truth annotation | Analysis gate | Boundary |
|---|---|---|---|
| Pregnancy and postpartum | Pregnant yes/no, trimester or gestational week, postpartum interval, obstetric complications, posture, cardioactive medication | Repeated standardized HRV and beat-to-beat BP/BRS with pregnancy-specific controls; never compare to age-only adult reference without stratification | ANS-001 PhysioNet metadata cannot support this subgroup |
| Reproductive ageing | Premenopause, perimenopause, postmenopause, surgical menopause, cycle phase when relevant, hormone therapy, symptoms | Distinguish menopausal transition from chronological age; compare with age-matched participants and account for hormone treatment | Do not infer menopause from age bands or recorded sex |
| Coronary disease / PCI / stents | Coronary diagnosis, MI history, intervention date/type, arrhythmia, ejection fraction where available, beta blockers and other drugs, rehabilitation | Analyze a clinical cardiovascular cohort separately; control disease severity and medications; only make clinical claims with outcome validation | "Stent" indicates a treatment history, not a gender, and does not itself establish a specific autonomic effect |
| Pediatrics | Age in months/years, developmental/pubertal stage where appropriate, size, congenital disease and measurement protocol | Developmental reference ranges by age and protocol; pediatric-specific research/ethics and independent validation | **No participants below 18** in current dataset |
| Athletic training | Verified sport and training history, weekly volume/intensity, recent workload/recovery, fitness, HR, respiration/posture | Stratify by training status and type; compare within age/sex and standardized resting conditions | Do not infer athletic status from resting bradycardia or HRV |

## Additional cross-cutting design controls

- Sex characteristics and gender identity must be conceptually separate from pregnancy capability, menopausal status and clinical history. Use only recorded variables; do not invent identities.
- Standardize **recording duration, body position, respiration, time of day, device, signal quality**. Investigate **BMI, blood pressure, antihypertensive medication, arrhythmia, exercise capacity, chronic illness, diabetes, sleep, and nicotine/caffeine** where data exist.
- Preserve missingness explicitly: `unknown_not_measured`, `not_applicable`, or a verified observed state, **never** silent negative imputation.
- For the current healthy-adult cohort, stratification is limited to **age bands, reported sex code, BMI and device**. Do not publish findings for unobserved subgroup variables.
- Distinguish (a) physiological variance, (b) confounding/measurement error, and (c) **prospective health outcomes**. Cross-sectional prediction of age is not prediction of longevity.
- Do not pool unrelated pediatric, obstetric, cardiovascular-disease and athlete cohorts to train a single reference score. First demonstrate within-cohort validity; then test transportability/calibration.

## Evidence motivating these branches (not evidence the ANS pipeline has validated them)

- Pregnancy progression and BRS/HRV: [PMID 31981003](https://pubmed.ncbi.nlm.nih.gov/31981003/); [PMID 37072002](https://pubmed.ncbi.nlm.nih.gov/37072002/); pregnancy-to-postpartum [PMID 29782509](https://pubmed.ncbi.nlm.nih.gov/29782509/).
- Menopausal stage and autonomic state, with major confounding: [PMID 38064358](https://pubmed.ncbi.nlm.nih.gov/38064358/); systematic review [PMID 42121335](https://pubmed.ncbi.nlm.nih.gov/42121335/).
- Athlete HRV and methodological caveats: [PMID 35853460](https://pubmed.ncbi.nlm.nih.gov/35853460/).
- Pediatric reference requirements: [PMID 41806014](https://pubmed.ncbi.nlm.nih.gov/41806014/).
- Intervention-related autonomic research in ischemic heart disease: [PMID 25029473](https://pubmed.ncbi.nlm.nih.gov/25029473/). This does **not** isolate the effect of chronic stent history on longevity.

## Execution order under low budget

1. **Now:** add machine-readable population-coverage audit to every adult PhysioNet cohort report; test missingness behavior. Preserve the 20-participant results without reinterpreting them.
2. **Next:** perform sensitivity analysis for BMI and recorded sex, sex-stratified exploratory descriptions if adequate sample counts; retain signal-quality exclusions.
3. **Parallel literature searches:** prospectively inventory open data for maternal/pregnancy, menopausal transition, coronary/PCI, pediatric and athlete groups. Score each dataset for *directly observed clinical state* and available ECG/BP/age/time/outcomes, not merely keyword overlap.
4. **Later:** separate prospective validation cohorts and ethics/legal checks when required. Do not announce clinical applications before replication and outcomes.

## Gate status (2026-11-15)

- 20/20 adult resting recordings computationally processed; 19 pass automated ECG QC; 12 exploratory BRS output values; **0 validated biomarkers**.
- Pregnancy: **not measured**; menopause: **not measured**; coronary stent history: **not measured**; athletic training: **not measured**; pediatric population: **absent**.
- Scientific interpretation outside the screened adult population: **HOLD**.
