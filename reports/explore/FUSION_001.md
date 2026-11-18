# FUSION-001 — do two autonomic domains together beat one?

Generated UTC: 2026-11-15T18:32:22.266244+00:00  
Plan frozen before values were read: `wearable/experiments/FUSION_001_PLAN.md`

**Decision under the frozen rule: NO DEMONSTRATED GAIN FROM FUSION**

People analysed: 46 (25 diabetes, 21 control). Inputs are lab-scored clinic tests, not watch signals. Label is diabetes status, an at-risk label, not confirmed autonomic dysfunction.

| Model (leave-one-out AUC for diabetes vs control) | AUC |
|---|---:|
| M0: age + sex | 0.38 |
| M1: + cardiovagal (Valsalva ratio) | 0.36 |
| M2: + adrenergic (tilt systolic change) | 0.56 |
| **M3: + both domains** | **0.52** (bootstrap 95% CI 0.35 to 0.69) |
| Secondary: both + tilt heart-rate change | 0.58 |

Fusion gain over the better single-domain model (M2_plus_adrenergic): -0.05 (bootstrap 95% CI -0.11 to -0.01; rule: ≥ +0.05 and CI above 0).

Are the two domains independent? Spearman ρ = -0.08 (p = 0.61); age-adjusted -0.12.

Single measures alone (unadjusted AUC): valsalva ratio low 0.59, tilt sbp fall 0.34, tilt hr rise low 0.67.

## Quartiles (25th, median, 75th)

```
{
 "valsalva_ratio": {
  "control": [
   1.35,
   1.56,
   1.72
  ],
  "diabetes": [
   1.25,
   1.39,
   1.57
  ]
 },
 "tilt_sbp_change_mmHg": {
  "control": [
   -10.0,
   -2.0,
   3.0
  ],
  "diabetes": [
   -3.0,
   8.0,
   15.0
  ]
 },
 "tilt_hr_change_bpm": {
  "control": [
   7.0,
   12.2,
   15.0
  ],
  "diabetes": [
   5.7,
   9.0,
   13.0
  ]
 },
 "age": {
  "control": [
   56.0,
   62.0,
   72.0
  ],
  "diabetes": [
   57.0,
   60.0,
   68.0
  ]
 }
}
```

## Limits

- One small table from one lab; AUC here is uncertain by roughly ±0.15.
- Two of three domains only: no sweat (sudomotor) test exists in the open data.
- Diabetes status is not autonomic dysfunction. A clinic cohort with a full reflex battery is needed for that.
