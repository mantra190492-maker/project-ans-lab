# TILT-001 — resting heart-rate fragmentation vs heart-rate response to tilt

Generated UTC: 2026-11-15T18:40:45.747019+00:00  
Plan frozen first: `docs/TILT_001_PLAN.md`  
Predictor table SHA-256 (before outcomes were parsed): `d37fb39daf449c58ed0b4b09b288d71a8036b8ce2fd02acd7a55592ecd8aabde`

**Decision under the frozen rule: NO CANDIDATE (null or inconclusive)**

Analysed: 29 people (14 diabetes, 15 control).

```
{
 "day2_records": 57,
 "ecg_qc_fail": 17,
 "ok": 36,
 "beat_shape_inconsistent": 3,
 "no_breathing_gap": 1,
 "in_summary_table": 30,
 "missing_outcome_or_covariate": 1,
 "analysed": 29
}
```

| Marker (adjusted for age, sex, diabetes, resting HR, log RMSSD) | n | β in bpm per SD [95% CI] | p | Bootstrap 95% CI | R² base → full |
|---|---:|---|---:|---|---|
| **PIP (primary)** | 29 | +0.37 [-3.70, +4.43] | 0.854 | -3.68 to +3.85 | 0.30 → 0.30 |
| Deceleration capacity (benchmark) | 29 | +0.83 [-3.50, +5.16] | 0.694 | -4.22 to +5.40 | 0.30 → 0.31 |
| Hard-inflection rate (sensitivity) | 29 | -1.20 [-3.99, +1.58] | 0.379 | -4.69 to +2.33 | 0.30 → 0.33 |

Leave-one-out range of the primary coefficient: -0.31 to +1.47

## Simple rank correlations (ρ, p)

- pip vs tilt hr change: ρ = +0.11, p = 0.555
- resting hr vs tilt hr change: ρ = +0.30, p = 0.113
- log rmssd vs tilt hr change: ρ = -0.02, p = 0.914
- age vs tilt hr change: ρ = -0.03, p = 0.882
- pip vs log rmssd: ρ = -0.65, p = 0.000

## Limits

- One small dataset; second test of the same marker in the same people.
- Tilt heart-rate change is one half of the orthostatic response; pressure data were not used here.
- Cross-sectional association, not prediction of decline.
