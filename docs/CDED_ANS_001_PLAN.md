# CDED-ANS-001 — Does a passive overnight ECG marker track clinic-confirmed autonomic decline?

**Status:** stage 1 (structure inventory) ready to run; stage 2 frozen below and runs only after stage 1 passes its gate. Written 2026-11-15 **before any CDED participant value was viewed.**

**Data:** PhysioNet CDED v1.0.1 (DOI 10.13026/00bm-0x81), open, CC BY 4.0. Adults aged 55–75 with and without type 2 diabetes. Baseline and 2-year lab protocols (Valsalva, supine rest, tilt) with ECG and continuous BP; baseline 24-hour ECG at 1000 Hz. 41 completed the 2-year visit.

**Why this matters for the goal:** this is the only open dataset found with standard autonomic reflex tests repeated two years apart in the highest-risk group (diabetes), plus a high-resolution passive ECG. The 1000 Hz ECG also removes the 125 Hz problem that blocked SHHS.

## Questions (no others will be tested)

1. **Cross-sectional (primary, n ≈ 60–69):** at baseline, is overnight heart-rate fragmentation associated with worse cardiovagal reflex function on the Valsalva test, beyond age, sex, diabetes status, mean heart rate and RMSSD?
2. **Longitudinal (pilot, n ≈ 35–41):** does baseline fragmentation predict the 2-year change in Valsalva ratio, adjusting for the baseline Valsalva ratio?

## Locked measurements

- **Predictor:** Costa-reference PIP (`anslab/hrf_costa_reference.py`) from the baseline 24-h ECG, 01:00–05:00 clock time (if clock time is unavailable: the 4 consecutive hours with the lowest mean heart rate). R peaks detected at native 1000 Hz; beats ending an interval >30% from the local median are labelled non-sinus. Exclude recordings with <75% usable sinus beats in the window (MESA rule). **Sensitivity only:** hard-inflection rate.
- **Comparators from the same window:** mean heart rate, log RMSSD.
- **Primary outcome:** Valsalva ratio = longest RR within 30 s after release ÷ shortest RR during strain, from the lab ECG, computed by code that never reads the predictor file.
- **Secondary outcomes:** tilt heart-rate rise (mean HR minutes 1–3 minus supine baseline) and systolic BP fall at 3 minutes. Neurogenic-pattern flag if SBP falls ≥20 mmHg with ΔHR/ΔSBP < 0.5.
- Covariates: age, sex, diabetes, beta-blocker use if recorded. Nothing else; the sample is too small.

## Analysis and decision rule (fixed now)

- Q1: linear regression of Valsalva ratio on PIP + covariates + comparators. **Positive finding** only if all hold: higher PIP goes with lower Valsalva ratio; the 95% CI for PIP excludes zero; PIP adds ≥5% explained variance over the comparator model.
- Q2: change in Valsalva ratio regressed on PIP + baseline Valsalva ratio + age + diabetes. Report the effect with its 95% CI only. With ~40 people this is a pilot signal, never a claim.
- A null result is reported in full. No extra markers, windows or cutoffs are tried after outcomes are seen.

## Order of operations

1. Run `scripts/cded_inventory.py` (structure only).
2. Gate: Valsalva and tilt segments locatable; ECG and BP present at both visits; ≥35 people with both visits and a baseline 24-h ECG. If any fail, stop and document.
3. Extract and freeze the predictor file (hash recorded) **before** computing any outcome.
4. Extract outcomes blind to the predictor; then run the two pre-specified models.

## What a positive result would and would not mean

- **Would:** a cheap, passive overnight ECG feature tracks clinic-confirmed cardiovagal function in older adults with diabetes, and possibly its decline. That is direct, if small, evidence toward early detection.
- **Would not:** a validated biomarker. It needs replication in a larger cohort with repeated reflex tests (e.g., DCCT/EDIC through an academic partner) before any detection claim.
