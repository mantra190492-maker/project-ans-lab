# Project ANS — Independent Agent 01: evidence audit

**Review date:** 2026-11-15. **Source:** external LLM research submission supplied by founder. Source assertions were not accepted automatically; checks below use linked primary papers and dataset landing pages.

## Verdict
**Useful directional evidence; FAIL source-integrity as received.** Retain verifiable original sources and corrected citations; never copy the external agent's summary wholesale as established evidence.

## Independently checked corrections

1. **Framingham mortality:** Tsuji et al., *Circulation* **1994**, PMID **8044959**, DOI **10.1161/01.CIR.90.2.878**. Agent listed this as 1996. Different Tsuji et al. **1996** event paper: PMID **8941112**, DOI **10.1161/01.CIR.94.11.2850**.
2. **ATRAMI 1998:** La Rovere et al., *Lancet* 1998, PMID **9482439**, DOI **10.1016/S0140-6736(97)11144-8**. The agent's citation `[3]` linked to an unrelated cognitive study PDF; therefore citation mapping in agent output is unreliable.
3. **Post-MI BRS 2007:** De Ferrari et al., *JACC* 2007, PMID **18068036**, DOI **10.1016/j.jacc.2007.08.043**. Earlier ATRAMI reported no significant predictive power in preserved LVEF / older subgroups, but the *new* 244-person, mean-five-year follow-up analysis found depressed BRS predictive even with LVEF >35%, including >65 years. Avoid conflating results. Also BRS thresholds and methods differ across studies; not automatically transferable to spontaneous BRS software.
4. **Cognitive cohort 2024:** First author **Jandackova**, not Huang. Whitehall II, **2,702** participants; DOI **10.1016/j.ijchp.2024.100518**, PMID **39639946**. Low RMSSD/HF-HRV associations with a decade of cognitive change were **small observational effects** (0.07 and 0.06 standardized units). No causality.
5. **MESA cognition 2020:** First author **Schaich**, not Fung; PMID **32200711**, DOI **10.1161/JAHA.119.013827**. **3,018** participants; 10-second HRV analyses. Associations attenuated after controlling for resting HR, and longitudinal HRV changes were not associated with cognitive performance. Important negative control for our project.
6. **Exercise RCT meta-analysis:** Etayo-Urtasun et al., *Sports Medicine* published online 2025, 2026 journal issue, PMID **41264119**, DOI **10.1007/s40279-025-02357-5**; 15 RCTs. RMSSD increased (SMD 0.636, 95% CI 0.014–1.258) but **no significant pooled effects on SDNN or BRS**. Large heterogeneity; HRV shifts are not longevity outcomes.
7. **Diabetes BRS 2010:** Okada et al., *Circ J*, PMID **20453396**, DOI **10.1253/circj.CJ-09-0960**; 210 patients enrolled, 184 followed; **phenylephrine BRS** and observed cardiovascular events. Do not assume threshold or mechanism equivalent to our *spontaneous* BRS estimates.
8. **Autonomic Aging dataset:** The dataset and original study report **1,121** screened healthy adult recordings, NOT 1,104. Our production sample is 20. DOI **10.13026/2hsy-t491**.
9. **PTB-XL:** Agent linked outdated v1.0.1. The current latest source page is **v1.0.3**. Records are roughly 10 seconds, so it is **not** a primary validation resource for five-minute HRV or cardiac BRS.

## Sources

- Framingham mortality https://pubmed.ncbi.nlm.nih.gov/8044959/
- Framingham 1996 cardiac events https://pubmed.ncbi.nlm.nih.gov/8941112/
- ATRAMI https://pubmed.ncbi.nlm.nih.gov/9482439/
- De Ferrari 2007 https://pubmed.ncbi.nlm.nih.gov/18068036/
- Jandackova/Whitehall II https://pubmed.ncbi.nlm.nih.gov/39639946/
- Schaich/MESA https://pmc.ncbi.nlm.nih.gov/articles/PMC7428623/
- Exercise RCT meta-analysis https://pmc.ncbi.nlm.nih.gov/articles/PMC12982300/
- Okada/diabetes https://pubmed.ncbi.nlm.nih.gov/20453396/
- Autonomic Aging https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/
- Fantasia https://physionet.org/content/fantasia/1.0.0/
- SHHS/NSRR https://sleepdata.org/datasets/shhs
- PTB-XL v1.0.3 https://physionet.org/content/ptb-xl/1.0.3/

## Accepted hypotheses (not validated by Project ANS)

1. **Primary engineering:** Do automatic ECG QRS detections agree with a PhysioNet corpus of **manually reviewed beat annotations**? Test precision/recall/F1 and timing error on Fantasia; then audit BP alignment separately. This fixes a genuine gap in our current 20-person pilot.
2. **Primary clinical prediction after analytic validation:** Can standardized resting HRV predict future cognitive or cardiovascular outcomes **beyond** age, resting heart rate, BMI, sex, disease, drugs, sleep and fitness where documented? Candidate SHHS/NSRR: adjudicated CVD events and mortality and polysomnography with ECG. **Data use/availability must be verified before building any linked cohort.**
3. **Secondary cardiovascular:** Does validated BRS improve risk prediction beyond standard factors in post-MI/cardiac cohorts? Existing literature is strong but population-specific, so novelty requires *incremental* validity under modern care and new external cohorts.
4. **Separate research populations:** Pregnancy/postpartum, menopause, coronary stent history, children and athletes need truly observed phenotypes. Fantasia and Autonomic Aging do not fill these categories.

## Do NOT do

- Do not attempt a 1,121-person full scan before independent ECG-QRS quality checks and BRS method comparison. Scale only after explicit gates.
- Do not equate a correlation of two BRS estimators with reference correctness or test–retest reliability.
- Do not infer future health or longevity from age prediction.
- Do not infer pregnancy, menopause, heart stents or athletic status from sex, age, BMI or heart rate.
- Do not claim manipulating HRV causes improved survival.

## Immediate decisions

**ACCEPT** need for Fantasia annotated ECG benchmarking, longitudinal outcome cohort search and prespecified baseline models.  
**REJECT/REPAIR** inaccurate paper authors/year/source mapping, wrong dataset size, blanket BRS threshold transfer, outdated PTB-XL and premature claims of intervention significance.  
**HOLD** clinical, causality and longevity claims.

Next result required: annotation-level QRS performance against Fantasia before further scaling.
