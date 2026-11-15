# HRF-RES-001 — PIP stability from 250 Hz to 125 Hz (fantasia)

Generated UTC: 2026-11-15T17:04:54.684939+00:00

**Question:** SHHS visit-1 ECG was mostly 125 Hz. Is Costa-reference PIP measured at 125 Hz interchangeable with PIP at 250 Hz on the same heartbeats?

Same human-annotated beats, re-gridded to the nearest 8 ms sample. This is the BEST case for a 125 Hz recording: no extra R-peak detection jitter is added.

Engineering thresholds (agent-defined in code before the first run; not an external preregistration): PASS only if Spearman ≥ 0.90, |mean shift| ≤ 2.0 pp and |Spearman(shift, log RMSSD)| ≤ 0.30. Beats exactly between two 125 Hz samples need a tie rule; a metric passes overall only if it passes under all three rules.

**Overall: Costa PIP FAIL; hard-inflection rate FAIL.**

Spearman is tie-corrected. Brackets are 95% CIs from resampling participants (each GUDB participant contributes two recordings).

| Metric | Tie rule | Recordings (people) | Spearman 250 vs 125 | Mean shift (pp) | Shift vs log RMSSD (ρ) | Decision |
|---|---|---:|---:|---:|---:|---|
| Costa PIP | random | 38 (38) | 0.96 [0.89, 0.98] | +4.9 [+4.2, +5.7] | -0.82 [-0.94, -0.62] | FAIL |
| Costa PIP | floor | 38 (38) | 0.97 [0.92, 0.99] | +4.2 [+3.7, +4.8] | -0.78 [-0.91, -0.56] | FAIL |
| Costa PIP | half_even | 38 (38) | 0.94 [0.87, 0.97] | +6.3 [+5.5, +7.2] | -0.76 [-0.91, -0.53] | FAIL |
| Hard-inflection rate | random | 38 (38) | 0.97 [0.90, 0.98] | -3.0 [-3.7, -2.4] | +0.26 [-0.16, +0.66] | FAIL |
| Hard-inflection rate | floor | 38 (38) | 0.96 [0.90, 0.99] | -4.0 [-4.7, -3.5] | +0.73 [+0.46, +0.89] | FAIL |
| Hard-inflection rate | half_even | 38 (38) | 0.92 [0.81, 0.97] | -5.6 [-6.4, -4.8] | +0.65 [+0.30, +0.90] | FAIL |

Mean share of inflections that are 'soft' (a zero NN change): 19.5% at 250 Hz → 30.3% at 125 Hz.

## Per recording (random tie rule)

| Record | Beats | RMSSD (ms) | PIP 250 | PIP 125 | Shift | Hard 250 | Hard 125 |
|---|---:|---:|---:|---:|---:|---:|---:|
| f1y01 | 2286 | 74.0 | 49.1 | 51.2 | +2.1 | 43.7 | 41.0 |
| f1y02 | 1814 | 66.0 | 55.2 | 57.7 | +2.5 | 48.7 | 46.7 |
| f1y03 | 1962 | 29.4 | 41.3 | 49.3 | +8.0 | 30.7 | 27.6 |
| f1y04 | 1371 | 101.2 | 73.2 | 75.3 | +2.1 | 71.0 | 69.4 |
| f1y05 | 1829 | 47.5 | 61.7 | 64.9 | +3.2 | 55.4 | 51.9 |
| f1y06 | 1747 | 65.5 | 50.8 | 54.2 | +3.4 | 44.6 | 42.0 |
| f1y07 | 1548 | 113.1 | 47.8 | 49.9 | +2.1 | 45.0 | 42.4 |
| f1y08 | 1856 | 45.2 | 53.5 | 57.0 | +3.5 | 46.5 | 42.6 |
| f1y09 | 2107 | 36.0 | 52.8 | 58.0 | +5.3 | 43.9 | 40.9 |
| f1y10 | 2252 | 53.7 | 51.8 | 55.9 | +4.0 | 45.0 | 41.8 |
| f1o02 | 1744 | 11.6 | 74.0 | 79.9 | +5.9 | 51.7 | 43.9 |
| f1o03 | 1846 | 21.3 | 64.0 | 70.7 | +6.7 | 46.6 | 42.2 |
| f1o04 | 1553 | 33.7 | 58.8 | 62.7 | +4.0 | 46.7 | 41.7 |
| f1o05 | 1699 | 11.3 | 65.2 | 75.4 | +10.3 | 38.1 | 39.4 |
| f1o06 | 1529 | 25.4 | 70.3 | 73.7 | +3.4 | 59.1 | 55.3 |
| f1o07 | 1834 | 27.0 | 58.4 | 64.1 | +5.7 | 45.8 | 40.3 |
| f1o08 | 2192 | 21.7 | 65.9 | 71.8 | +5.9 | 53.9 | 48.8 |
| f1o09 | 1276 | 65.6 | 68.4 | 71.7 | +3.3 | 58.0 | 55.0 |
| f1o10 | 2112 | 19.2 | 60.3 | 68.7 | +8.4 | 45.1 | 41.7 |
| f2y01 | 2061 | 67.3 | 63.1 | 66.0 | +2.8 | 57.7 | 55.1 |
| f2y03 | 1718 | 31.6 | 66.5 | 70.1 | +3.6 | 57.2 | 54.0 |
| f2y04 | 2251 | 24.7 | 57.1 | 62.8 | +5.8 | 43.7 | 42.5 |
| f2y05 | 2342 | 18.7 | 54.8 | 62.4 | +7.6 | 39.5 | 35.3 |
| f2y06 | 1831 | 28.6 | 63.1 | 66.1 | +3.0 | 53.7 | 49.0 |
| f2y07 | 1648 | 78.5 | 51.4 | 52.8 | +1.4 | 48.4 | 47.1 |
| f2y08 | 1832 | 96.8 | 62.2 | 62.8 | +0.7 | 58.4 | 57.0 |
| f2y09 | 2250 | 50.8 | 53.4 | 56.8 | +3.4 | 41.5 | 39.3 |
| f2y10 | 1845 | 50.3 | 34.9 | 44.0 | +9.1 | 24.6 | 22.1 |
| f2o01 | 1991 | 24.7 | 49.9 | 56.5 | +6.7 | 36.7 | 32.3 |
| f2o02 | 1649 | 27.8 | 67.4 | 71.3 | +3.9 | 58.3 | 53.5 |
| f2o03 | 1702 | 24.2 | 69.7 | 75.4 | +5.7 | 57.9 | 51.7 |
| f2o04 | 1751 | 28.2 | 51.3 | 56.1 | +4.9 | 41.7 | 38.2 |
| f2o05 | 2279 | 9.8 | 66.3 | 76.8 | +10.4 | 30.8 | 34.4 |
| f2o06 | 1344 | 43.3 | 51.9 | 54.8 | +2.8 | 42.3 | 40.4 |
| f2o07 | 1501 | 25.5 | 65.7 | 69.3 | +3.6 | 51.4 | 47.6 |
| f2o08 | 1847 | 18.4 | 69.0 | 75.1 | +6.1 | 49.7 | 45.7 |
| f2o09 | 1589 | 15.0 | 60.3 | 67.5 | +7.2 | 38.6 | 38.0 |
| f2o10 | 2325 | 12.6 | 66.3 | 73.9 | +7.7 | 39.0 | 37.4 |

## Excluded (reported, not hidden)

- f1o01: HTTPError: 502 Server Error: Bad Gateway for url: https://physionet.org/files/fantasia/1.0.0/f1o01.hea
- f2y02: ValueError: Unexpected sampling rate 333

## Limits

- Quantization only; a real 125 Hz detector adds timing jitter, so real-world shifts are likely larger.
- GUDB windows are 2 minutes (~140 beats), so absolute PIP is noisy; the comparison is paired on identical beats.
- GUDB beats are not rhythm-typed; the reference algorithm's NN bounds are the only beat filter.
- Healthy adults only. Not a clinical, ageing or outcome result.
