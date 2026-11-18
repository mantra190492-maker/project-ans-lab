# DIAB-PIP-001 — is resting heart-rate fragmentation higher in type 2 diabetes than in controls?

**Frozen 2026-11-17 before any ECG from these records was read and before any ECG-derived value was compared between groups.** Last item in the open-data queue (`docs/RESEARCH_LEDGER.md`).

## Disclosures

- **Where the idea came from.** A post hoc look at GE-71 (27 people, GE71-ANS-001) showed median PIP 69 in diabetes vs 61 in controls. That difference was never tested and is hypothesis-generating only. Everyone whose ID appears in the GE-71 table is excluded here, so this test does not reuse those people.
- **What the label is.** Type 2 diabetes is an *at-risk* label. It is not confirmed autonomic dysfunction. A positive result would say "fragmentation is higher in a group at risk", not "fragmentation detects autonomic deterioration".
- **What is already known about these records (structure only, `reports/explore/DIAB_PREP.md`, `DIAB_PREP2.md`).** Record counts, group counts, table column names, CO2 traces of the first 15 minutes. No ECG and no blood pressure has been read.
- **Fourth outcome-level test in this project.** Three earlier tests were null.

## Deviation from what the ledger promised, and why

The ledger said the model would adjust for age and sex. **It cannot.** CDED's published summary tables contain no age or sex column (the data dictionary lists them; the tables do not), and the WFDB headers carry no comments. Age and sex exist for GE-75 only, and GE-75 has 6 controls among its 52 lab records.

Consequences, fixed now:

1. Age and sex are **not** in the primary model. Each study recruited both groups from one age band (CDED 55–75, GE-75 50–85, per their PhysioNet descriptions), which narrows age confounding but does not remove it; sex is uncontrolled.
2. **A passing test is therefore not a candidate biomarker.** It is recorded as *"a lead, not adjusted for age and sex"* that needs an age- and sex-adjusted replication in other data before anything is claimed.
3. A null is recorded as a null.

## Single primary question

Among older adults (CDED 55–75, GE-75 50–85), is resting PIP higher in type 2 diabetes than in controls, beyond dataset, mean heart rate and RMSSD?

## Locked data

- **Records.** CDED visit-2 lab records (`cded/1.0.1`, 69 records) and GE-75 head-up-tilt lab records (`cerebral-perfusion-diabetes/1.0.1`, 52 records). Both 500 Hz, same lab, same protocol.
- **One record per person.** An ID present in both datasets is the same person (height agrees within 3 cm in 10 of 11 shared IDs; group agrees in 11 of 11). For such a person the GE-75 record is used if it passes the quality rules below, otherwise the CDED record.
- **Excluded before analysis.** Any ID in the GE-71 summary table; any record with no group label in its dataset's table.
- **Group.** `Group` column: `DM` = diabetes, `CONTROL` = control.

## Locked measurements

- **Window.** Seconds 30–270 of the record (supine, start of protocol), the same fixed window as GE71-ANS-001 and TILT-001. No searching for a later window.
- **Outcome.** Costa-reference PIP on the 250 Hz grid, computed exactly as in GE71-ANS-001 (`scripts/ge71_analysis.hrv_metrics`).
- **Covariates from the same window.** Mean heart rate, log RMSSD.
- **Quality rules, all blind to group.**
  - CO2 only: `window_qc` must return `ok` (capnogram present, no breathing gap, stable end-tidal level), and the typical breath-to-breath CO2 swing must be physiologic (75th percentile of 10-second ranges between 10 and 80 units); otherwise the record is dropped.
  - ECG: beat-shape consistency ≥ 0.90, at least 150 intervals, at least 80% usable intervals (same as TILT-001).
- **Blinding.** All ECG-derived values and all quality decisions are computed and their SHA-256 written **before** any group label is parsed.

## Analysis and decision rule

- OLS: PIP ~ diabetes (1/0) + dataset (GE-75 vs CDED) + mean HR + log RMSSD. The diabetes coefficient is the adjusted difference in PIP points.
- One two-sided test, α = 0.05. Expected sign: diabetes higher.
- **Pass** only if all hold: p < 0.05 with a positive coefficient; the participant-bootstrap 95% CI (4,000 resamples, resampled within group) excludes 0; the coefficient is positive in every leave-one-out fit.
- **Power, stated before the data.** If about 60% of records pass quality control (as in GE-71), roughly 45 diabetes and 18 controls remain. That detects only a large difference (about 0.8 SD) with 80% power. A null is inconclusive for smaller differences.

## Sensitivity analyses (reported; none can turn a fail into a pass)

- S1: without mean HR and log RMSSD.
- S2: CDED only (the only dataset with a real control group).
- S3: excluding beta-blocker users (`BETA BLOCKERS` = Y).
- S4: adding age and sex in the subset where both exist, **only if** at least 10 people per group remain; otherwise reported as not estimable.

## Reported descriptively (not tests)

Group medians and quartiles of PIP, heart rate and RMSSD; quality-control pass counts by dataset and by group (selection check); Spearman correlation of PIP with log RMSSD.

## What happens next

Nothing else is tested on these datasets under this plan. After this test the open-data queue is closed, whatever the result. Reports contain aggregates only.
