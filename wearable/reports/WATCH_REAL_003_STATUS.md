# WATCH-REAL-003 — Real paired wrist/chest experiment

**State when authored:** Original WESAD raw recordings have not yet been successfully loaded for this experiment. No genuine wrist-to-chest quantitative finding is established merely by this report's existence.

The [runner](../experiments/wesad_real_003.py) and [six regression tests](../tests/test_wesad_real_003.py) are implemented. The [GitHub workflow](../../.github/workflows/wearable-wesad-real-003.yml) attempts two original WESAD subjects by HTTP range, avoiding a full ~2.5GB download. Failure to reach the archive means **data-access blocked**, not sensor analysis failure.

## Predeclared comparison

- Source: WESAD scientific non-commercial research data (Schmidt et al., ICMI 2018, DOI 10.1145/3242969.3242985).
- Same people: 700 Hz chest ECG and real 64 Hz wrist BVP, in 180-second contiguous baseline/stress windows after transition skip.
- Anti-alias-resample identical wrist BVP from 64 Hz to 25 Hz and measure pulse-beat agreement degradation relative to automated chest ECG.
- Calibrate ECG-to-pulse delay from first 60 seconds only. Calculate precision/recall/F1 over seconds 60–177 only, no evaluation-time lag optimization.
- Output only anonymous aggregate summaries; no WESAD pickles, patient-level traces, or subject-specific findings in public GitHub.
- ECG R peaks are algorithmic, not independently manually verified.
- WESAD stress labels cannot assess clinical ANS disease, hEDS, neuropathy or novelty.

After authentic successful execution, the aggregate-only result is uploaded as a GitHub Actions artifact named watch-real-003-aggregate-only. Raw data are never committed.

**Use terms:** [WESAD original source](https://ubi29.informatik.uni-siegen.de/usi/data_wesad.html) permits scientific non-commercial use with attribution.
