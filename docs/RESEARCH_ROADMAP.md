# Project ANS — Research Roadmap

## Mission
Study autonomic nervous system regulation and ageing, with the long-term aim of evidence-based longevity technology.

## Primary program: ANS-001
Hypothesis: dynamic autonomic response and recovery metrics may contain information about age-related physiological resilience beyond resting HRV, age, and conventional covariates.

Candidate measurements: HRV under standardized conditions, orthostatic HR/BP responses, baroreflex sensitivity, respiratory coupling, recovery time constants. Evaluate confounding by medications, fitness, sleep, measurement conditions, comorbidity and device differences.

### Stage gates
1. Identify legally accessible datasets with age, suitable signals, and longitudinal or functional outcomes.
2. Preregister baseline and incremental models; enforce subject-level train/test separation.
3. Quantify calibration, uncertainty, missingness, subgroup performance and external validation.
4. Reject hypotheses that do not replicate. Never infer clinical utility from cross-sectional age prediction alone.

## Secondary program: ANS-003
Adult-onset neuromuscular disease differentiation remains an exploratory branch. Do not treat muscular dystrophy as synonymous with autoimmune or autonomic disease.

## Current implementation
- Automated PubMed literature scouting and persistent publication archive.
- PhysioNet Autonomic Aging: 20 adult ECG/BP records computationally processed across four age strata; 19 passed preliminary ECG consistency screening; 12 yielded provisional BRS values. This is engineering feasibility, **not** scientific measurement validation or a longevity biomarker.
- Population gap analysis and future cohorts: [Population Stratification Protocol](POPULATION_STRATIFICATION.md). Pregnant, postpartum, menopausal, coronary-stent, athletic and pediatric outcomes **cannot** be derived from unobserved PhysioNet phenotypes. Adult dataset has no participants below 18.
- Next gates: verify beat annotations, breathing/posture/device covariates, age/sex/BMI sensitivity, external data for named populations, prospective outcomes, independent replication.
- Still not an autonomous scientist, validated biomarker system, or longevity product.
