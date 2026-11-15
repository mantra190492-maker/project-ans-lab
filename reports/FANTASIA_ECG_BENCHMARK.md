# ANS-001 — Fantasia ECG human-annotation benchmark

Generated: 2026-11-15T13:02:40.230099+00:00

Automatic R-peak detector compared against the dataset's **manually reviewed beat annotations**.
No model parameters were optimized against these records.

| Record | Age group | Reference beats | Predicted beats | Precision | Recall | F1 | Median abs timing error | QC |
|---|---|---:|---:|---:|---:|---:|---:|---|
| f1y01 | young_21_34 | 388 | 388 | 1.000 | 1.000 | 1.000 | 1.0 ms | pass |
| f1o01 | older_68_85 | 309 | 309 | 1.000 | 1.000 | 1.000 | 2.0 ms | pass |
| f2y01 | young_21_34 | 350 | 350 | 1.000 | 1.000 | 1.000 | 3.0 ms | pass |
| f2o01 | older_68_85 | 338 | 338 | 1.000 | 1.000 | 1.000 | 2.0 ms | pass |

**Engineering target (prospective):** F1 ≥ 0.95 in both age strata, no silent processing failures.
F1 and timing agreement are not verification of beat-type classification, arrhythmia handling or BP/BRS alignment.
This first four-record pilot is for software feasibility; expand to all Fantasia participants only after inspecting failures.

Dataset: https://physionet.org/content/fantasia/1.0.0/
Cite: Iyengar et al. 1996 and PhysioNet Fantasia DOI 10.13026/C2RG61.
