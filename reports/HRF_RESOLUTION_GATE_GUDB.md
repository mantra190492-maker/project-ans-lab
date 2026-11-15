# HRF-RES-001 — PIP stability from 250 Hz to 125 Hz (gudb)

Generated UTC: 2026-11-15T16:17:11.596889+00:00

**Question:** SHHS visit-1 ECG was mostly 125 Hz. Is Costa-reference PIP measured at 125 Hz interchangeable with PIP at 250 Hz on the same heartbeats?

Same human-annotated beats, re-gridded to the nearest 8 ms sample. This is the BEST case for a 125 Hz recording: no extra R-peak detection jitter is added.

Engineering thresholds (agent-defined in code before the first run; not an external preregistration): PASS only if Spearman ≥ 0.90, |mean shift| ≤ 2.0 pp and |Spearman(shift, log RMSSD)| ≤ 0.30. Beats exactly between two 125 Hz samples need a tie rule; a metric passes overall only if it passes under all three rules.

**Overall: Costa PIP FAIL; hard-inflection rate FAIL.**

Spearman is tie-corrected. Brackets are 95% CIs from resampling participants (each GUDB participant contributes two recordings).

| Metric | Tie rule | Recordings (people) | Spearman 250 vs 125 | Mean shift (pp) | Shift vs log RMSSD (ρ) | Decision |
|---|---|---:|---:|---:|---:|---|
| Costa PIP | random | 50 (25) | 0.86 [0.75, 0.93] | +6.0 [+4.5, +7.6] | -0.53 [-0.71, -0.26] | FAIL |
| Costa PIP | floor | 50 (25) | 0.91 [0.82, 0.96] | +5.3 [+4.3, +6.4] | -0.37 [-0.63, -0.06] | FAIL |
| Costa PIP | half_even | 50 (25) | 0.88 [0.78, 0.94] | +7.0 [+5.6, +8.7] | -0.38 [-0.63, -0.07] | FAIL |
| Hard-inflection rate | random | 50 (25) | 0.93 [0.85, 0.96] | -1.1 [-2.5, +0.5] | -0.33 [-0.59, -0.03] | FAIL |
| Hard-inflection rate | floor | 50 (25) | 0.96 [0.90, 0.98] | -2.3 [-3.2, -1.4] | +0.06 [-0.29, +0.40] | FAIL |
| Hard-inflection rate | half_even | 50 (25) | 0.94 [0.87, 0.97] | -3.9 [-5.0, -2.9] | -0.02 [-0.35, +0.34] | FAIL |

Mean share of inflections that are 'soft' (a zero NN change): 23.3% at 250 Hz → 33.1% at 125 Hz.

## Per recording (random tie rule)

| Record | Beats | RMSSD (ms) | PIP 250 | PIP 125 | Shift | Hard 250 | Hard 125 |
|---|---:|---:|---:|---:|---:|---:|---:|
| gudb_s00_sitting | 140 | 44.0 | 51.1 | 59.6 | +8.4 | 48.9 | 43.1 |
| gudb_s00_maths | 144 | 59.0 | 62.4 | 63.8 | +1.4 | 61.0 | 58.2 |
| gudb_s01_sitting | 183 | 30.0 | 27.4 | 33.0 | +5.6 | 21.7 | 21.7 |
| gudb_s01_maths | 235 | 12.8 | 60.8 | 72.6 | +11.8 | 29.3 | 41.4 |
| gudb_s02_sitting | 148 | 51.1 | 46.8 | 48.2 | +1.4 | 37.2 | 40.0 |
| gudb_s02_maths | 164 | 45.8 | 50.3 | 54.1 | +3.8 | 44.7 | 39.8 |
| gudb_s03_sitting | 150 | 34.3 | 63.9 | 69.4 | +5.4 | 46.9 | 47.6 |
| gudb_s03_maths | 187 | 14.6 | 60.3 | 65.2 | +4.9 | 34.2 | 34.2 |
| gudb_s04_sitting | 148 | 44.6 | 50.3 | 57.3 | +7.0 | 46.9 | 38.6 |
| gudb_s04_maths | 152 | 35.7 | 54.5 | 59.3 | +4.8 | 46.3 | 42.3 |
| gudb_s05_sitting | 170 | 31.9 | 51.5 | 53.3 | +1.8 | 37.7 | 36.5 |
| gudb_s05_maths | 193 | 20.1 | 57.9 | 65.6 | +7.7 | 37.9 | 38.4 |
| gudb_s06_sitting | 157 | 44.6 | 35.5 | 41.1 | +5.7 | 28.2 | 24.2 |
| gudb_s06_maths | 153 | 44.8 | 52.3 | 55.7 | +3.4 | 46.7 | 44.7 |
| gudb_s07_sitting | 164 | 33.1 | 44.7 | 54.0 | +9.3 | 37.3 | 35.4 |
| gudb_s07_maths | 185 | 16.2 | 49.7 | 65.7 | +16.0 | 30.8 | 28.0 |
| gudb_s08_sitting | 151 | 32.6 | 47.6 | 57.1 | +9.5 | 41.9 | 36.5 |
| gudb_s08_maths | 156 | 43.1 | 62.7 | 68.7 | +6.0 | 54.9 | 50.3 |
| gudb_s09_sitting | 177 | 35.3 | 56.1 | 64.2 | +8.1 | 46.6 | 43.1 |
| gudb_s09_maths | 210 | 10.2 | 72.0 | 72.7 | +0.7 | 29.5 | 33.8 |
| gudb_s10_sitting | 153 | 25.3 | 59.7 | 67.1 | +7.4 | 47.3 | 44.0 |
| gudb_s10_maths | 153 | 27.1 | 57.9 | 65.5 | +7.6 | 42.7 | 34.0 |
| gudb_s11_sitting | 119 | 88.7 | 64.0 | 65.8 | +1.8 | 59.5 | 57.8 |
| gudb_s11_maths | 135 | 57.1 | 56.5 | 57.3 | +0.8 | 53.0 | 52.3 |
| gudb_s12_sitting | 239 | 6.4 | 55.3 | 70.8 | +15.4 | 18.6 | 29.7 |
| gudb_s12_maths | 282 | 4.2 | 72.7 | 78.9 | +6.2 | 24.0 | 38.0 |
| gudb_s13_sitting | 168 | 37.2 | 33.6 | 41.0 | +7.4 | 24.5 | 25.2 |
| gudb_s13_maths | 173 | 45.6 | 33.1 | 39.1 | +5.9 | 25.9 | 21.8 |
| gudb_s14_sitting | 143 | 46.7 | 58.7 | 59.0 | +0.3 | 47.9 | 45.7 |
| gudb_s14_maths | 148 | 44.5 | 62.9 | 62.9 | +0.0 | 53.8 | 53.8 |
| gudb_s15_sitting | 159 | 39.8 | 42.9 | 50.3 | +7.5 | 32.1 | 32.7 |
| gudb_s15_maths | 187 | 22.7 | 50.0 | 63.6 | +13.6 | 31.5 | 31.0 |
| gudb_s16_sitting | 141 | 33.1 | 56.9 | 56.2 | -0.7 | 47.8 | 44.9 |
| gudb_s16_maths | 140 | 39.5 | 59.1 | 58.4 | -0.7 | 48.9 | 48.2 |
| gudb_s17_sitting | 139 | 28.2 | 50.7 | 51.9 | +1.1 | 39.7 | 38.2 |
| gudb_s17_maths | 148 | 25.0 | 61.4 | 70.3 | +9.0 | 51.0 | 51.0 |
| gudb_s18_sitting | 127 | 87.5 | 30.3 | 30.6 | +0.3 | 25.0 | 23.4 |
| gudb_s18_maths | 152 | 31.6 | 47.9 | 51.0 | +3.2 | 27.5 | 30.9 |
| gudb_s19_sitting | 150 | 18.3 | 34.3 | 49.0 | +14.7 | 21.1 | 17.7 |
| gudb_s19_maths | 172 | 12.1 | 46.7 | 61.1 | +14.4 | 24.3 | 29.0 |
| gudb_s20_sitting | 171 | 34.0 | 39.5 | 52.2 | +12.7 | 25.6 | 22.0 |
| gudb_s20_maths | 186 | 22.7 | 49.5 | 60.4 | +11.0 | 26.8 | 25.1 |
| gudb_s21_sitting | 143 | 58.2 | 44.6 | 48.9 | +4.3 | 41.4 | 38.6 |
| gudb_s21_maths | 145 | 45.8 | 49.6 | 50.0 | +0.4 | 46.5 | 46.5 |
| gudb_s22_sitting | 187 | 23.3 | 63.0 | 66.3 | +3.3 | 53.3 | 50.0 |
| gudb_s22_maths | 189 | 24.0 | 60.2 | 65.6 | +5.4 | 46.2 | 41.9 |
| gudb_s23_sitting | 149 | 31.9 | 56.6 | 61.4 | +4.8 | 47.9 | 47.3 |
| gudb_s23_maths | 191 | 16.9 | 50.8 | 59.8 | +9.0 | 33.0 | 37.2 |
| gudb_s24_sitting | 135 | 31.4 | 39.7 | 46.2 | +6.5 | 36.4 | 30.3 |
| gudb_s24_maths | 140 | 26.0 | 67.6 | 70.6 | +2.9 | 56.9 | 49.6 |

## Limits

- Quantization only; a real 125 Hz detector adds timing jitter, so real-world shifts are likely larger.
- GUDB windows are 2 minutes (~140 beats), so absolute PIP is noisy; the comparison is paired on identical beats.
- GUDB beats are not rhythm-typed; the reference algorithm's NN bounds are the only beat filter.
- Healthy adults only. Not a clinical, ageing or outcome result.
