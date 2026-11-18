# GE71-ANS-001 — Does resting heart-rate fragmentation track a clinic-measured cardiovagal reflex?

**Frozen 2026-11-15, before any ECG, blood-pressure or outcome value from this dataset was read.** Only file structure, column names, and CO2/marker channels have been inspected (see `reports/explore/`).

**Data:** PhysioNet "Cerebral Vasoregulation in Diabetes" v1.0.0 (GE-71), DOI 10.13026/m40k-4758, open, CC BY 4.0. Adults 55–75 with and without type 2 diabetes. The dataset's own summary table holds **lab-computed Valsalva ratios** (`VM RATIO`, 46 people) — a standard cardiovagal reflex test scored by the original investigators, independent of this project's code.

**Why this replaces CDED as the first clinical-reference test:** CDED has no reference values in its tables, no usable overnight ECG, and its visit-8 respiratory channels look corrupted. GE-71 gives the reference test directly.

## Single primary question

In people with a usable Day-2 resting ECG and a recorded Valsalva ratio: is higher resting heart-rate fragmentation associated with a **lower Valsalva ratio**, beyond age, sex, diabetes status, mean heart rate and RMSSD?

## Locked measurements

- **Rest window:** seconds 30–270 of the Day-2 lab record (protocol starts with quiet supine rest; the first Valsalva follows at ~5 min). CO2-only quality check: no no-breathing gap ≥10 s and no 20-s block whose peak CO2 is <80% of the window median (hyperventilation). Failing records are excluded and counted. (A first, more complex gap-based rule misplaced windows in several records on CO2-only review and is dropped.)
- **Beats:** repo R-peak detector at native 1000 Hz, then each peak moved to the dominant-polarity maximum within ±40 ms. Beats ending an interval >20% from the local 11-beat median are labelled non-sinus. Include a record only with ≥150 intervals and ≥80% usable.
- **Primary predictor:** Costa-reference PIP (`anslab/hrf_costa_reference.py`) with peak times rounded half-up to the 250 Hz grid used by the reference software.
- **Comparators (same window):** mean heart rate, log RMSSD.
- **Benchmark (reported, not a second hypothesis):** deceleration capacity. **Sensitivity only:** hard-inflection rate at 1000 Hz; `VMRatio2`.
- **Outcome:** `VM RATIO` from the summary table; values <0.9 treated as invalid. Outcome columns are read only after the predictor table is written and hashed.
- **Covariates:** `Age`, `Gender`, diabetes (Group ≠ control).

## Analysis and decision rule

- OLS: VM RATIO ~ PIP + age + sex + diabetes + mean HR + log RMSSD (predictors standardised). One two-sided test, α = 0.05, expected sign negative.
- Robustness, both required: participant bootstrap 95% CI (4,000 resamples) excludes 0; sign unchanged in every leave-one-out fit.
- **Candidate signal** only if all three hold. Anything else is reported as null or inconclusive. With ~40 people only a partial correlation of about 0.4 or larger is detectable; a null does not rule out a smaller effect.
- No other markers, windows, outcomes or cut-offs are tested on this dataset under this plan. A candidate must then be replicated in a different dataset before it is called a possibility for early detection.

## Reporting

Aggregates only (counts, coefficients, CIs, group medians) and an anonymous scatter plot. No participant-level rows are committed.

*Implementation note added before the first run:* the ECG is centred and scaled to unit amplitude before peak detection (the detector's thresholds are relative, so this changes no beat times).
