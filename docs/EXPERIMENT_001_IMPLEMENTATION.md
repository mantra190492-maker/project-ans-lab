# ANS-001: Raw-signal experiment implementation status

## Implemented
- Deterministic time-domain HRV features (mean heart rate, SDNN, RMSSD) from **pre-cleaned NN intervals**.
- Exploratory three-beat cardiac baroreflex sequence estimator from aligned beat-level systolic BP and next-beat RR.
- Explicit missing-result handling when too few sequences exist.
- Unit tests with synthetic inputs.

## Not yet implemented or verified
- Download of PhysioNet waveform files.
- ECG R-peak detection and artifact correction.
- BP beat detection and ECG/BP alignment validation.
- Dataset-specific record mapping and participant-level train/test split.
- Model comparison and statistical inference on real participant data.
- Independent replication, prospective outcomes, or longevity predictions.

## Interpretation safeguards
The sequence estimator is an exploratory software prototype. It is **not** clinically validated. Consecutive overlapping sequences are not independent; counts must not be interpreted as independent participants. Sampling, timing and filtering must be verified before real-data use. HRV cannot measure sympathetic nerve activity directly.

## Stop/go
Do not fit age prediction or report a biomarker until ECG/BP alignment, signal quality, subject metadata, and data splits have been audited.
