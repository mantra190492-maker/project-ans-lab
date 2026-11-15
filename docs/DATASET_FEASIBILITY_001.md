# ANS-001 Dataset Feasibility 001

## Candidate: PhysioNet Autonomic Aging v1.0.0
Source: https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/
DOI: 10.13026/2hsy-t491
License: Open Data Commons Open Database License v1.0

The published dataset description reports simultaneous ECG and continuous non-invasive blood pressure at rest for 1,121 healthy volunteers, with age bins and basic demographic metadata. Raw recordings total approximately 5.9 GB uncompressed. The database is openly accessible.

## Suitability
- **Feasible:** resting HRV; beat-to-beat blood pressure and exploratory cardiac baroreflex sensitivity; age-bin associations.
- **Not feasible from this dataset alone:** direct sympathetic tone/MSNA, orthostatic recovery dynamics, longitudinal frailty progression, mortality prediction, or claims about biological age.
- **Critical confounding:** recording device, age binning, BMI, sex, signal quality and recording length.
- **Scientific novelty warning:** this dataset has already been used for autonomic-age machine learning; merely predicting age is not novel.

## Next analysis gate
1. Download metadata and a small, prespecified set of recordings only.
2. Verify ECG/BP alignment, sample rates, channel calibration, and participant-level identifiers.
3. Extract baseline HRV and a prespecified BRS estimate with quality flags.
4. Compare incremental age-bin association only, with subject-level splits and uncertainty.
5. Seek a separate longitudinal cohort before making deterioration or longevity claims.

## Provenance
Dataset: Schumann & Bär (2021), PhysioNet, DOI 10.13026/2hsy-t491.
Data descriptor: Schumann & Bär (2022), Scientific Data, DOI 10.1038/s41597-022-01202-y.

Status: feasibility established from public documentation; raw-signal experiment not executed.
