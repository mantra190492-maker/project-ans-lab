# WATCH-REAL-003 — First real wrist-vs-chest results

**Experiment outcome: completed small engineering pilot; failure of pulse timing calibration. NOT an ANS/EDS biomarker result.**

- Execution: [GitHub Actions run 43754521855](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43754521855), **success**, including six regression tests.
- Source: original WESAD release downloaded by bounded HTTP ZIP range; **two same-person recordings** with Empatica E4 wrist 64 Hz BVP and RespiBAN chest 700 Hz ECG.
- Analysis: one 180-second contiguous baseline window and one 180-second stress window for each participant; last 117 seconds evaluated. Same BVP downsampled to 25 Hz as an engineering sampling-rate sensitivity check.
- Clinical outcome labels: **none**. WESAD states are protocol-defined stress tasks, not autonomic neuropathy or EDS diagnoses.
- ECG comparator: **algorithmic R-peak estimates, not manually audited ground truth**. Differences below may be errors in either detector or source synchronization and **cannot be called smartwatch accuracy**.

## Actual observed aggregate comparison

| Measure | Baseline (2 subjects) | Stress (2 subjects) |
|---|---:|---:|
| Absolute 64-Hz wrist pulse-rate vs 700-Hz ECG-rate discrepancy, median | **9.23 bpm** | **25.90 bpm** |
| Absolute 25-Hz rate-proxy vs ECG-rate discrepancy, median | **9.49 bpm** | **27.18 bpm** |
| ECG-to-wrist stable pulse-delay calibration | **0/2 passed** | **0/2 passed** |
| One-to-one wrist pulse/ECG F1 | **Withheld** | **Withheld** |
| Clinical ANS detection sensitivity/specificity | **Not measurable** | **Not measurable** |

All four windows yielded count-based pulse-rate estimates. The predeclared 0.05–0.55 s ECG-to-pulse-delay calibration failed **4/4**. We did **not** optimize the delay against held-out test windows to manufacture a good pulse-matching score.

## Scientific decision

1. **Reject clinical or high-fidelity sensing claims from this version.** The current detection/synchronization pipeline is not sufficiently validated.
2. The differences between 64 Hz and 25 Hz were smaller than the discrepancies to our automated chest ECG rate estimates in these two subjects. That does **not** establish 25 Hz device adequacy: the ECG and wrist algorithms may be wrong.
3. Do not attribute the stress discrepancy to actual autonomic physiology, motion, or pathology without artifact and independently annotated beat verification.
4. **Next test:** Audited chest ECG and wrist BVP pulse detector against independent reference methodology, inspect synchronization/calibration using separate calibration and evaluation windows, repeat on more participants. Maintain subject separation and aggregate-only reporting.

## Provenance and limitations

Code: [WATCH-REAL-003](../experiments/wesad_real_003.py) | [Six local/CI tests](../tests/test_wesad_real_003.py) | [Original run, aggregate artifact](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43754521855)

Dataset: WESAD (Schmidt et al., ICMI 2018, DOI 10.1145/3242969.3242985), [author source](https://ubi29.informatik.uni-siegen.de/usi/data_wesad.html). Scientific/non-commercial use with attribution. No raw source traces, person-level outputs or patient identifiers committed to public GitHub.

**Status:** Engineering pilot completed with serious method limitations; no novel biomarker, EDS detection or clinical ANS accuracy established.
