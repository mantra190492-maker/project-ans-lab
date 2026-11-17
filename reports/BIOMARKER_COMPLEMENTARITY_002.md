# ANS-DISC-002 — Real-data test of HRV/BRS complementarity and selection bias

**Source:** Existing Project ANS public [PhysioNet Autonomic Aging](https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/) pilot-derived features in [reports/physionet_cohort.json](physionet_cohort.json). **Not a new clinical dataset.** Pre-existing sample is 20 convenience-selected resting healthy adults from 1,121 publicly described study participants. No independent BRS reference or clinical dysautonomia labels.

## Decision-driving results

| Exploratory test | Observed result | Honest meaning |
|---|---:|---|
| Automated ECG quality | 19 of 20 pass | One flagged record excluded from associations |
| Exploratory BRS availability among ECG-QC pass | 12 of 19 (63.2%) | Combined BRS feature absent for 36.8% of this small pilot |
| RMSSD vs exploratory BRS | Spearman rho **+0.776** (n=12) | Strong rank association; simple fusion may add less independent information than assumed |
| Permutation test | Two-sided p **0.0045** (20,000 seeded shuffles) | Association under pilot sampling, not diagnostic accuracy |
| Participant-bootstrap CI for rho | **[+0.376, +0.957]** (10,000 replicates) | Wide uncertainty, but high dependence plausible |
| Leave-one-out Spearman rho | **+0.736 to +0.836** | Not driven by one included record |
| RMSSD median with vs without BRS | **19.1 vs 38.3 ms** (12 vs 7) | Complete-case sample differs from excluded participants |
| Exact Mann–Whitney comparison of RMSSD groups | Exploratory p **0.017** | Selection effect merits investigation; post-hoc, uncorrected |
| Partial rank correlation adjusted for mean HR | **+0.693** (n=12) | Descriptive sensitivity only, no reliable adjusted causal inference |

## Falsification result

**Do not assume RMSSD + sequence-method BRS supplies two independent confirmations of ANS deterioration.** They covary strongly in this public resting ECG/BP pilot, and missing BRS estimates are associated with higher RMSSD. Fitting a fusion model only on the 12 complete cases could induce selection bias.

This does **not** prove clinical redundancy. The provisional BRS algorithm and RMSSD share R-wave timing. Sequence-selection rules, heart rate, BP beat matching and sample selection may explain the association. No healthy-vs-EDS classification, clinical sensitivity/specificity, autonomic deterioration, novel biomarker or added value can be established.

## Next falsifiable experiment

1. Visually audit ECG/BP beat alignment, verify sequence BRS against an independent implementation and investigate why some ECG-clean recordings yield no BRS estimate.
2. Replicate using more public same-person ECG/BP signals before attempting fusion; measure missingness and dependence.
3. Seek **independent-domain measurements** recorded on the *same participants* and independently assessed ANS outcomes before any accuracy claims.

**Code:** [scripts/biomarker_complementarity_pilot.py](../scripts/biomarker_complementarity_pilot.py); [tests/test_biomarker_complementarity_pilot.py](../tests/test_biomarker_complementarity_pilot.py).

**Statistical status:** Exploratory post-hoc analyses of a small, nonrepresentative healthy convenience sample. No multiple-comparison correction, clinical labels or independent BRS truth. Results are reanalysis of **real cohort-derived summary measurements**, not simulated clinical findings. Numerical values first reproduced locally from the matching publicly committed cohort's aggregate feature values; rerunning the script on the complete repository JSON will generate its full-file SHA and analysis output.
