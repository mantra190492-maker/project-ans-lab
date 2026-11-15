# ANS-001 — Fantasia Benchmark Run #1: provenance and timing-unit correction

**Status:** Four ECG records processed; **preliminary R-peak detection benchmark**, not general algorithm or clinical validation.

The completed GitHub Actions run saved `reports/fantasia_ecg_benchmark.json` / `reports/FANTASIA_ECG_BENCHMARK.md` at **2026-11-15 13:02:40 UTC**. All four records had 1:1 predicted/reference beat counts and a reported F1 = 1.000 under a 150 ms matching tolerance.

## Known reporting bug in Run #1
The archived output mislabeled **sample offsets as milliseconds** in the median absolute R-peak timing-error column. The waveform sampling rate was **250 Hz**, or **4 ms per sample**. Therefore the following values are the **correct interpretation** of the stored run:

| Record | Reference beat count | F1 (150 ms tolerance) | Stored offset mislabeled "ms" | Correct median absolute offset |
|---|---:|---:|---:|---:|
| f1y01 | 388 | 1.000 | 1 sample | **4 ms** |
| f1o01 | 309 | 1.000 | 2 samples | **8 ms** |
| f2y01 | 350 | 1.000 | 3 samples | **12 ms** |
| f2o01 | 338 | 1.000 | 2 samples | **8 ms** |

This is a unit correction only, **not** a rerun or independent verification. Code commit `5938ff5` corrected the conversion formula; its GitHub workflow run #2 is shown **failed** in the founder's screenshot, so the correction has **not yet passed a verified execution**. Failure cause still requires the actual job logs; do not speculate.

## Scientific interpretation
- F1=1.000 for four selected five-minute segments is promising but **cannot establish general ECG-detector accuracy**, accuracy in arrhythmia, or transfer to the Autonomic Aging recordings.
- A 150 ms tolerance can obscure fiducial timing discrepancies. In later analysis also report sensitivity at **50 ms and 100 ms** and waveform overlays.
- The current four-record sample does not validate systolic BP detection, ECG/BP delay, baroreflex sensitivity, risk prediction, biological ageing, or longevity.
- The latest failed run may be a data/network, test, workflow, or repository-publication issue. Until log inspection, categorize as **unknown execution failure** rather than a failed scientific benchmark.

**Decision:** Keep the original result for auditability; correct the units; HOLD further scientific interpretation until the corrected workflow passes and annotated reference beat checks are independently reviewed.
