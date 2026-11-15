# ANS-001 — Fantasia revised HRF pilot (Costa-reference PIP)

Dataset: [Fantasia v1.0.0](https://physionet.org/content/fantasia/1.0.0/), DOI 10.13026/C2RG61.
Generated UTC: 2026-11-15T16:05:31.303749+00:00

**The original pilot's provisional PIP is NOT the author's official PIP definition.**
Corrected PIP follows an independently written implementation that matched Costa's
three official test cases in PIP, PNNSS and PNNLS integer counts.
This does NOT validate physiological interpretation, clinical autonomic deterioration, or disease detection.

| Record | Age band | Annotated beats | QC normal NN | Costa-style PIP | Old provisional PIP | Difference (pp) | Status |
|---|---|---:|---:|---:|---:|---:|---|
| f1y01 | — | — | — | — | — | — | Failure: ConnectTimeout |
| f1o01 | — | — | — | — | — | — | Failure: ConnectTimeout |
| f2y01 | — | — | — | — | — | — | Failure: ConnectTimeout |
| f2o01 | — | — | — | — | — | — | Failure: ConnectTimeout |

## Gate decisions

- **Primary reference:** the corrected Costa-style PIP, conditional on external sinus beat annotations and preserved QC.
- **Legacy candidate:** prior symbol-transition PIP; retained for transparent difference reporting only, NOT used as official method.
- Excluded records stay excluded: no retroactive relaxation of 95% normal-NN quality.
- ECG sampling frequency is explicitly recorded; 125 versus 250 Hz longitudinal SHHS runs cannot be naively compared.
- Costa's official source uses strict NN bounds (0.3, 1.8) seconds; previous candidate's bound reached 2.0 seconds.
- Real Fantasia pilot is NOT author source differential proof on clinical populations and not ANS diagnosis.
- No restricted data, future outcomes, or individual clinical records have been accessed.

[Official Costa differential numerical test](HRF_DIFFERENTIAL_TEST.md).
