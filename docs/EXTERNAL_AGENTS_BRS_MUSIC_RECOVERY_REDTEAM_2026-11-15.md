# Project ANS — External agents: BRS, MUSIC, dynamic recovery and red-team adjudication

**Review date:** 2026-11-15. **Input:** four founder-supplied PDFs: `2 BRS validation.pdf` (10 pp), `3 MUSIC protocol.pdf` (9 pp), `4 Dynamic resilience.pdf` (9 pp), `5 Red team.pdf` (7 pp). PDFs are not checked into this repo. The separate **biomarker-discovery** agent submission is **not in this four-file batch**.

**Standard:** Source-derived proposals are separate from independently verified public sources. Do not import unverified conclusions as scientific facts. No external model has been validated against survival outcomes by Project ANS.

## Executive result — four reports, one decision

**Proceed as methods + independent replication, NOT invention of an original ageing biomarker.** The strongest near-term work is a MUSIC **method-comparable, clinical-risk-adjusted, reproducible heart-rate fragmentation (PIP) replication** with **deceleration capacity (DC)** as a stronger additional reference feature. In parallel establish validity of the BRS measurement against open PRCP/EuroBaVar and assess whether MIDUS *public variables* support dynamic-response mortality analysis. No composite "Autonomic Resilience Index" or new product claim is justified.

The 2025 Hernández et al. 12-year TILDA study and 2017/2018 fragmentation prior art invalidate claims that physiological stand-trajectory prognosis or HRF are newly invented.

## Track A: BRS validator, supplied PDF '2 BRS validation.pdf'

**ACCEPT:**
- Label any initial result **"spontaneous cardiovagal SBP–RR coupling index"** with method, lag, qualifying count, failure rate and calibration limits. Do not infer pharmacologic maximum baroreflex gain.
- Validate heartbeat/BP peak pairing **independently** of Fantasia ECG beat annotation success.
- Separate missing-data or finger-cuff recalibration gaps; never splice across gaps; standardize beat and pressure flags.
- Compare sequence vs LF transfer-function estimator with explicit time lag and **false-positive surrogates** (time-reverse BP, circular-shift BP, cross-person pairing). Include amplitude/variance-ratio covariates and respiration sensitivity.
- Verify **PRCP** (10 participants, ECG and arterial pressure during stand/tilt) for time-aligned, repeated-challenge engineering and **EuroBaVar** (21 persons × two positions) for numerical method comparison. BaroKit has MATLAB/R source + EuroBaVar methods.

**CORRECTIONS / GATES:**
- The reported **12/20** BRS yields (or 12/19 among ECG-QC passes) is a **withheld estimate**, not proven pipeline failure or low biological BRS. Zero pharmacologically validated BRS numbers.
- The report's "90% yield" threshold, linear age slope, posture change in ≥90% and 10-sec post-recalibration discard are **proposed targets/heuristics**, NOT standard required physiological truths.
- One dataset's BP waveform was originally sampled at 100 Hz, interpolated to 1 kHz; cannot treat interpolated pressure peaks as 1-ms independent temporal resolution. Verify original sample/header mapping and actual BP intervals before applying a fixed SBP pairing window.
- **Do not automatically implement lag-0 SBP(i) → RR(i) as the biologically correct response**: pulse transit, device, RR naming conventions and beat indexing must be validated against waveforms and reference code. Compare lag 0, 1, 2 prospectively.
- **EuroBaVar download URL** exists in public indexing, but the PDF's address has not been proven retrievable on our GitHub runner. Do not claim local benchmark success.
- The latest [BaroKit GitHub repository](https://github.com/drmanish007/Barokit) contains **MATLAB and R** reference implementations; it also includes **synthetic example data**, not an independently curated clinical pharmacologic ground truth. A peer-reviewed paper exists in 2026: [Goyal et al.](https://www.nature.com/articles/s41371-026-01140-x).
- Wessel et al. 2020 [PMID 33071732](https://pubmed.ncbi.nlm.nih.gov/33071732/) demonstrated that xBRS can be nearly equivalent to **heart-period/BP variability ratio** and can fail a time-reversal causal direction test. A positive xBRS does not prove a reflex mechanism.

**Next BRS gate:** download *small* PRCP annotation/header example and manually compare pressure/ECG alignment, then benchmark EuroBaVar with source availability and numerical reference method. No bulk 1,121-run yet.

## Track B: MUSIC clinical protocol, supplied PDF '3 MUSIC protocol.pdf'

**ACCEPT as valuable upgrades to prior draft:**
- Include **deceleration capacity** as **Model 2**, then test incremental HRF/PIP as Model 3; evaluate whether PIP has value after an established advanced autonomic marker, not just SDNN/RMSSD.
- Keep **all-cause death** and cause-specific cardiac death **distinct**. Avoid classifying non-cardiac deaths, transplantation and lost follow-up as interchangeable events/censors.
- Correct 4-yr risk prediction using properly defined follow-up and hazard/competing-event models; explicit tests for arrhythmia, ectopy, heart rate, medications, disease severity and sampling resolution.
- **One patient per split**, include feature extraction and imputation in training-validation folds; calibration and optimism-corrected discrimination; no clinical conclusion solely from significant HR.
- Baseline event-budget reality: In earlier MUSIC **607 eligible HRT patients**, 129 died, 52 sudden; these counts do **not** imply the same events exist in our **587 HRV-complete eligible** group.
- Explicit comparison with existing MUSIC risk model (clinical variables/NT-proBNP etc.) and not just a weak demographic-only baseline.

**REJECT as unverified/unsafe:**
- PDF says beta blockers unconfirmed. **Our already executed public source CSV audit verified `Betablockers (yes=1)` present for 992/992**; agent had not inspected actual CSV. Correct before copying protocol.
- PDF says 107 cardiac deaths in a prior subset (requires source link/sample definition). **Do not use 107 as actual analytic-event count** until an eligibility-specific verified cross-tab is performed.
- The source page reports **94 sudden / 111 pump-failure deaths**, whereas the paper reports **90 sudden / 123 pump-failure**. Investigate version/denominator/definition instead of selecting the favourable one. Our aggregate source CSV has **94 coded sudden, 100+11=111 pump-failure, 61 noncardiac**. Its **726 cause-of-death code-zero rows** include some not-dead outcomes: **NOT 726 verified survivors**.
- **Transplant as primary "cardiac death" is category error**. If clinical importance justifies including transplant, prespecify a separate **composite cardiac death or transplant**, *distinct* from death alone. All-cause death excludes transplant as an event and can censor at transplant subject to estimand/assumptions; transplant is a competing/related clinical event and may entail informative censoring. Cannot insist transplant must always count as a death.
- The report's power grid (0.75 at ~100 events under idealized hazard assumptions) does **not prove** sufficient precision for 10+ parameters, nonlinear splines and multiple imputation. Verify complete-case events and apply risk-model sample-size design before fitting.
- The PDF's `PIP ≤0` formula on raw unquantized ΔNN is **not automatically numerically equivalent** to published MESA **ternary ΔNN** with **±4 ms at 256 Hz**; our algorithm uses 4/8 ms sensitivity. Freeze exact method and match reference on synthetic and annotated waveforms *before* survival modeling.
- A 99% ectopic classification sensitivity & PPV threshold is **agent's proposed gate**, not accomplished performance in MUSIC. MUSIC does not provide beat annotations; manual review needs documented adjudication; do not claim automatic multi-lead detection suffices.

**Next clinical gate:** audit time-to-event and failure reasons **only in counts**, verify original study definitions, then compare parsimonious M0/M1/M2/M3; DO NOT download all 90 GB or run survival model until sample/endpoint/feature validation passes.

## Track C: dynamic resilience, supplied PDF '4 Dynamic resilience.pdf'

**ACCEPT:**
- [Panaite et al. 2015](https://pubmed.ncbi.nlm.nih.gov/25829236/) is a **37-study (N=125,386)** longitudinal meta-analysis, summary r=0.17; it is **not** evidence that a particular stand HRR equation is independently validated. Heterogeneous outcomes/protocols and high heterogeneity.
- **PRCP** is a verified open ECG+ABP stand/tilt dataset for signal-level engineering, not mortality prediction.
- Three candidate measurements: (i) time-resolved stand HR recovery, (ii) orthostatic SBP return-to-baseline, (iii) exercise recovery as established benchmark. Peak amplitude, absence of physiological response and overshoot must be tracked to prevent false "fast recovery" readings.
- MIDUS Biomarker has challenge-task periods and a linked mortality resource; investigate **exact public variable/time resolution, accessible censoring and linked denominator** prior to modeling.
- Separate pregnant, menopausal, pediatric, athletic and medicated cohorts; no healthy-adult score transferred without clinical validation.

**ERROR:** PDF repeatedly calls **12-year active-stand prognosis a "preprint"**. Hernández et al., [PMID 41390547](https://pubmed.ncbi.nlm.nih.gov/41390547/), published **Dec 13 2025** (`Communications Medicine`, 2026 issue), analyzed **4,336** stand responses and associations with 12-year mortality/CVD. Their **functional trajectories** are close prior art to any 'novel integrated stand-recovery index'. The original dataset is controlled, not open in our project.

**HOLD:** The PDF's MIDUS **217 deaths / 1,255 participants** is taken from an analysis-specific cohort and **not yet verified as the exact public study population with accessible dynamic challenge features and censoring**. No legitimate prospective model until codebook/joins/rights are established. A single chest-strap self-study does not establish repeatability across patients or clinical validation.

## Track D: independent red team, supplied PDF '5 Red team.pdf'

**ACCEPT:** A weighted sum HRV+BRS+PIP+recovery is **not inherently novel**. Existing prior art includes autonomic-age clocks, HRF risk methods, full stand-response CVD/mortality models, post-MI [Polyscore](https://pubmed.ncbi.nlm.nih.gov/?term=Polyscore+postinfarction+baroreflex) and consumer readiness/recovery scores. Even an incremental replication is not necessarily a marketable diagnostic.

**CRITICAL prior art:** [US20200375480A1](https://patents.google.com/patent/US20200375480A1/en), titled *Non-Invasive Cardiovascular Risk Assessment Using Heart Rate Variability Fragmentation*, priority **2017-03-24**, inventors **Costa and Goldberger**, assignee **Beth Israel Deaconess Medical Center**. Google Patents marks *that application* **abandoned**, which is not a binding professional legal opinion and says nothing about related families, jurisdictions or future applications. Commercial freedom-to-operate requires legal counsel.

**CAUSALITY:** INOVATE-HF/BeAT-HF and MR analyses undermine facile autonomic intervention-as-longevity claims. But severe HF null interventions and genetic proxy studies do **not** prove *all possible* autonomic mechanisms noncausal in every population; keep scope qualified.

**FALSIFICATION:** Predefine a credible base model; hold out an independent cohort; require calibrated incremental discrimination/decision benefit. A simple p<0.05 and ΔC≥0.01 are planning criteria, not proof of a new clinically useful biomarker, and event counts and uncertainty may invalidate the design.

## Revised experimental decision — protect the original invention mission

1. **Engineering track:** Validate our ECG/NN/PIP and BRS methods openly with annotated and reference recordings (Fantasia, PRCP, EuroBaVar as available); compare BRS against surrogate nulls. This does NOT claim novelty.
2. **Clinical benchmark track:** MUSIC PIP versus **clinical + resting HR + standard HRV + deceleration capacity**, treating transplant as its own clinical event; avoid outcome leakage and overfitting. Replication is **not** a new biomarker.
3. **Discovery track:** Before building any "ARI," run formal prior-art claim charts for **within-person repeated multi-system recovery trajectory / physiological loss-of-resilience** beyond published 12-year stand-functional PCA, HRF, deceleration capacity, and earlier autonomic composites. Requires serial signals + independently adjudicated future outcomes; may be **untestable at <$50/mo**.
4. **Data-access gate:** MIDUS codebook audit before survival claims. If no person-level repeated challenge timestamps and censored outcome roster, stop the proposed time-resolved challenge prognostic experiment on that dataset.
5. **Go/no-go:** only promote an original marker if there is a **demonstrated genuine method/claim gap** and an independently reproduced clinically useful result. Otherwise publish rigorous null replication or release methods software, without branded biomarker claims.

## External sources verified during this review

- [PRCP PhysioNet](https://physionet.org/content/prcp/1.0.0/) and [DOI 10.13026/C2PC7R](https://doi.org/10.13026/C2PC7R)
- [BaroKit open source](https://github.com/drmanish007/Barokit) and [BaroKit paper](https://www.nature.com/articles/s41371-026-01140-x)
- [EuroBaVar download listing](https://www.eurobavar.altervista.org/Eurobavar/download.html) (**direct Github-run download not yet established**)
- [Costa 2017 PIP original](https://pmc.ncbi.nlm.nih.gov/articles/PMC5422439/)
- [Costa 2018 MESA formula](https://pmc.ncbi.nlm.nih.gov/articles/PMC6129761/)
- [Wessel xBRS causality / variability ratio, PMID 33071732](https://pubmed.ncbi.nlm.nih.gov/33071732/)
- [MUSIC v1.0.1](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/)
- [Cygankiewicz HRT MUSIC subset, PMID 18675217](https://pubmed.ncbi.nlm.nih.gov/18675217/)
- [Panaite 2015 recovery meta, PMID 25829236](https://pubmed.ncbi.nlm.nih.gov/25829236/)
- [Hernández et al. 2025/26 stand trajectories, PMID 41390547](https://pubmed.ncbi.nlm.nih.gov/41390547/)
- [Google Patents US20200375480A1](https://patents.google.com/patent/US20200375480A1/en)
