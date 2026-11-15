# EXPERIMENT 002 — Autonomic dysfunction detection: measurement validity gate

**Date frozen:** 2026-11-15. **Status:** First-stage engineering protocol; not registered or clinically validated.

## Research target (not chronological age)

We need to detect early **autonomic nervous system (ANS) functional impairment** and track reproducible worsening, not estimate lifespan or biological age. Clinical autonomic function is assessed in multiple **distinct domains**: cardiovagal, adrenergic, and sudomotor. ECG + continuous BP can support only **candidate cardiovascular responses**; a whole-system diagnosis requires additional clinically interpreted reflex tests and sweat testing.

**Reference comparator:** Standardized laboratory autonomic reflex testing / CASS domain subscores, appropriate patient diagnosis and physician adjudication; confirmed by the 2026 American Autonomic Society best-practices consensus https://link.springer.com/article/10.1007/s10286-026-01238-9 .

## Step 1 — Source-data feasibility on PRCP

**PRCP source:** https://physionet.org/content/prcp/1.0.0/ ; DOI 10.13026/C2PC7R, 10 screened healthy subjects. Public recordings supply ECG, continuous arterial pressure, and posture changes (slow tilt, rapid tilt, active stand). Each record has `.hea`, `.dat`, and annotations `.anI`, `.wabp`, `.wqrs`.

1. **Before waveform interpretation:** Inventory source record headers, sampling rates, waveform names, annotation-code counts, aux labels and beat/ABP annotations. Avoid assuming `.anI` encoding or posture onset semantics without confirmation. Preserve technical failure reasons.
2. Identify one record with reliable **repeated comparable challenges**, and verify exact motion-event timing by inspection against the actual ECG/BP waveform and source documentation. Not all tilts/stands have interchangeable dose.
3. Predefine baseline duration, zero reference, postural challenge type, 10–20s HR response, 30–60s and 60–120s SBP recovery, motion exclusions, and uncertainty. Do not invent response units or infer heart rate from sparse beats across a missed event.
4. Quantify **within-person repeat challenge agreement** (absolute difference / reliability with appropriate confidence intervals), and **negative controls** (misaligned onset; mismatched subject or shuffling pressure times).
5. Report **quality/exclusion rate** and parameter sensitivity, with every source-record failure retained. Ten people are insufficient to set healthy population norms or clinical diagnosis thresholds.

**Go for engineering only:** At least two independently labeled comparable challenge instances per selected record and interpretable ECG/ABP timing with repeatable feature definitions. **Stop and inspect:** No unambiguous posture-event label, mismatched sensors, implausible cardiac/pressure timing, or drift larger than response. **Nothing here demonstrates deterioration.**

## Step 2 — Disease-positive cross-sectional evidence

Screen open **CDED** (older diabetes/control) and **CVES** (stroke/control) for applicable stand/tilt signals and documented clinical phenotype; do NOT presume diabetic or stroke status equals autonomic dysfunction. Seek an **actual clinical autonomic test-labeled cohort**, ideally with CASS cardiovagal/adrenergic/sudomotor subscores, lab protocol, medications and diagnostic confirmation.

A valid first clinical endpoint is **sensitivity/specificity and calibration for independently adjudicated cardiovagal or adrenergic impairment**, beyond a standard single-domain feature and basic clinical covariates. A model trained on participant diagnosis cannot use the same diagnosis or components of its reference as leaked predictors. Blind all features before opening clinical labels.

## Step 3 — Repeated-visit deterioration

The proposed [AFDV formulation](FORMULATION_001_AUTONOMIC_FUNCTION_DETERIORATION.md) uses **repeat standardized measures relative to a person's stable baseline**, not a universal age score. A worsening signal must exceed **measurement noise / minimum detectable change** in separated sessions and agree with **clinically confirmed deterioration**, not just shift after illness, dehydration, medication, sport or posture changes. Missing sudomotor data remain 'not measured,' never zero.

**Current availability:** No in-repository cohort has verified repeated longitudinal **clinical autonomic reflex/CASS deterioration**. We will need a licensed research dataset or clinical research partner. This is the decisive access dependency; no algorithm can replace missing ground truth.

## Decision rules

- **CONTINUE engineering** if waveform alignment, event labels and within-subject repeatability are sound.
- **CONTINUE clinical development** only if a properly labeled disease-positive and disease-negative dataset supports supervised validation without leakage and an independent test cohort.
- **KILL the claim of early deterioration detection** if the proposed change does not exceed within-subject measurement noise or fails against adjudicated clinical deterioration.
- **Never claim originality** until exact method/feature/endpoint prior art has been examined. The AFDV vector currently is an unvalidated research hypothesis.

## Cost

PRCP full download is ~54 MB and available freely; initial annotation inventory is much smaller. Use GitHub Actions in small bounded jobs, no patient-level waveform files committed to the repository.
