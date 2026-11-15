# FORMULATION-001 — Detecting deterioration in autonomic nervous system function

**Status:** New **candidate formulation**, November 15 2026. Research only; not clinically validated, not a discovered new biomarker, and no verified patentable novelty.

## Correct research target (replaces inappropriate age/longevity focus)

**Primary research question:** Can changes in standardized physiological response features detect emerging **autonomic nervous system functional impairment**, identify which branches are affected, and track worsening *before or beyond* established autonomic reflex-test abnormalities?

The outcome is **autonomic impairment or progression**. **Chronological age, ageing rate, lifespan and mortality are not the outcome.** Age/sex/stage can be *normative covariates* and confounders; mortality studies (MUSIC/SHHS) are optional external relevance tests, not direct validation against clinical autonomic failure.

### Important prior art and clinical anchor

- A **Composite Autonomic Severity Score (CASS)** already grades generalized autonomic failure from autonomic reflex testing (0–10; cardiovagal 0–3; adrenergic 0–4; sudomotor 0–3): Low et al. 1993, PMID 8392653, https://pubmed.ncbi.nlm.nih.gov/8392653/.
- International clinical testing consensus 2020/2021, PMID 33419664, https://pubmed.ncbi.nlm.nih.gov/33419664/; updated consensus **published September 2026**, PMID 42766240, https://pubmed.ncbi.nlm.nih.gov/42766240/.
- **Cardiovascular ECG/BP alone does not evaluate sudomotor or all organ-specific branches.** Any ECG/BP-only result must be labelled **cardiovagal/adrenergic screening candidate**, never general ANS dysfunction diagnosis.

## Required clinically anchored research domains

| Domain | Candidate observables (existing measures) | Confirmatory clinical comparison |
|---|---|---|
| Cardiovagal parasympathetic | Age-/context-adjusted respiratory sinus arrhythmia during **paced deep breathing**; Valsalva ratio; normal-to-normal RR recovery trajectory; HRV features as baseline | Laboratory deep-breathing and Valsalva cardiovagal abnormalities; CASS cardiovagal subscore |
| Sympathetic adrenergic vasomotor | Beat-to-beat SBP/DBP response during standardized stand/tilt; pressure stabilization/recovery, Valsalva phase II/IV waveform patterns, reproducibility across repeats | Laboratory autonomic reflex screen; orthostatic challenge and Valsalva adrenergic abnormality; CASS adrenergic subscore |
| Sympathetic sudomotor | Standardized stimulus-evoked sweat onset, output, distribution (e.g. QSART); optically inferred sweat proxy **not** assumed equivalent | Clinical QSART/thermoregulatory sweat testing; CASS sudomotor subscore |

**Not all patients have generalized failure.** Distinguish cardiovagal impairment, adrenergic failure, sudomotor dysfunction, and disorders featuring hyperactivity/intolerance without structural or generalized autonomic failure. Add disorder-specific endpoints (e.g., diabetic autonomic neuropathy, neurodegenerative autonomic failure, orthostatic hypotension) rather than treating all as one disease.

## Proposed mathematical candidate: Autonomic Functional Deterioration Vector (AFDV)

### Measurement inputs

For subject i, visit v and domain d, extract a fixed vector of quality-qualified features \`F_(i,v,d)=[f_1,...,f_p]\` from **the same validated standardized stimuli** at multiple sessions. Example:
- d = cardiovagal: E:I/deep-breathing HR oscillation amplitude, Valsalva ratio (if clinically supervised), recovery amplitude (with posture controlled).
- d = adrenergic: orthostatic SBP nadir, BP deficit integrated 10–120 s, 60–120 s BP recovery relative to *standing steady state*, phase II/IV BP if VM data available.
- d = sudomotor: site- and temperature-standardized sweat output/latency, if QSART available.

Features have preregistered physiology-specific **impairment orientation** s_j ∈ {-1,+1}, chosen from prior reference/test standards, **never optimized from clinical labels in the test set**. Some features (U-shaped/unpredictable patterns) cannot be assigned a monotonic sign; for those use a two-sided 'deviation' flag and do not call it deterioration.

### Fixed personal baseline and standardized change

Use **m≥3 independently repeated clinically stable baseline sessions** (a provisional design value; obtain empirically justified test–retest requirements). Estimate:
- \`mu_(i,d,j) = median_baseline f_(i,v,d,j)\`
- \`sigma_(i,d,j) = max(MAD-based baseline scale, assay-specific minimum detectable change)\` from an *independent test–retest calibration cohort*. Do not let a near-zero personal SD inflate the marker.

For a later test visit:
\`\`\`
q_(i,v,d,j) = s_j * ( f_(i,v,d,j) - mu_(i,d,j) ) / sigma_(i,d,j)
\`\`\`
Positive q = change toward **prespecified impairment direction** (if physiologically directional); negative q may represent improvement or an alternative deviation, not a diagnosis.

Define a **domain-specific deterioration candidate**:
\`\`\`
D_(i,v,d) = sum_j(w_(d,j) * max(0, q_(i,v,d,j))) / sum_j w_(d,j)
\`\`\`
Initially equal pre-specified weights within each domain, with a **sensitivity analysis using the individual raw features**. Do not optimize weights on the test outcomes.

Define a separate **quality/coverage mask** \`M_(i,v,d)\` indicating which domain has usable sensors and standardized measurements. **Never set an unmeasured domain to zero**.

The candidate biomarker is the **vector**, not an averaged total:
\`\`\`
AFDV_(i,v) = [ D_(i,v,cardiovagal),
               D_(i,v,adrenergic),
               D_(i,v,sudomotor) ]
\`\`\`
If the project has only ECG+BP, the valid reported output is **[cardiovagal candidate, adrenergic candidate, sudomotor NOT MEASURED]**.

### Persistent change / confirmation

A single shifted response can be caused by hydration, meds, sleep, fever, menstrual or pregnancy state, exercise, temperature, technique, neuropathy, and device characteristics. Thus **AFDV is an anomaly/impairment hypothesis, not diagnosis**.

Candidate persistent change requires deviation exceeding an externally established **reliable-change threshold** on **two separated, adequate-quality tests** with stable controlled conditions. This threshold must be estimated independently rather than chosen by observing clinical labels. Clinical deterioration ultimately requires agreement with autonomic reflex screen, CASS subscores, diagnostic disease criteria, symptom/functional progression and physician adjudication. An increased AFDV with improved exercise fitness or medication change may NOT signify deterioration.

## Study design — decisive validations

### Experiment 1: engineering (small open data, no claims)

Use PRCP (10 people, repeat stand/tilt with ECG+BP), plus CDED/CVES for physiology. Validate sensor timing, noise/motion, tilt-onset alignment, repeatability and missingness. Four Fantasia ECG records cannot validate this entire formulation.

**Success:** Known benign repeat tests rarely exceed the empirical threshold. **Failure:** Measurement is unstable under small timing/hydration/device variations.

### Experiment 2: concurrent clinical reference

Recruit/access labelled clinical autonomic testing with standardized **deep breathing, Valsalva, tilt/stand and QSART** and specialist interpretation. Compare AFDV branches against CASS 3 subscores, healthy/control and specific autonomic disorder groups. Blind feature computation to case labels. Report sensitivity and specificity, AUROC/precision-recall, PPV at the study's prevalence, calibration, and confidence intervals; avoid post-hoc cutoffs and within-person data leakage.

**Target:** Show useful performance above single established measurements and age/sex/medication controls, **not merely correlation with CASS**. Treat use as a screening or monitoring application pending validation.

### Experiment 3: longitudinal true deterioration

With repeated tests at a preregistered time horizon (e.g., 6–24 months depending on specific disorder), determine whether change in AFDV **precedes or predicts independent worsening** in adjudicated CASS subscores or autonomic clinical status, beyond baseline CASS, heart rate, conventional HRV, medication, illness, and device changes. **External replication required.** Data availability is unverified; at <$50/month this test likely needs a research/clinic partner.

**Kill criteria:** (i) test–retest change larger than disease change; (ii) the feature signal disappears with confounder adjustment; (iii) no independent clinically relevant incremental accuracy or reproducibility; (iv) performance fails across a second cohort.

## Novelty and development boundaries

- **Existing tests and CASS are the competitors and clinical reference**, not "age clocks." A three-domain vector or personalized normalization is **not necessarily novel**.
- To claim invention, isolate and formally search the **exact new signal relationship, dynamic feature, uncertainty-aware response, early-detection endpoint, or measurement method**; confirm no previous use in literature/patents; replicate clinically.
- **MUSIC death prediction = secondary association experiment**, not the principal validation of autonomic deterioration. Reorient Project ANS discovery metrics and the evidence board accordingly.
- The proposed AFDV does **not** measure all aspects of autonomic physiology even with three domains, and no one number can diagnose every autonomic disorder.

## Sources

- Low et al., 1993, CASS: https://pubmed.ncbi.nlm.nih.gov/8392653/
- Consensus electrodiagnostic autonomic assessment, 2021, PMID 33419664: https://pubmed.ncbi.nlm.nih.gov/33419664/
- 2026 autonomic testing best practices, PMID 42766240: https://pubmed.ncbi.nlm.nih.gov/42766240/
- Quantitative autonomic testing methodology, PMID 21788940: https://pubmed.ncbi.nlm.nih.gov/21788940/
