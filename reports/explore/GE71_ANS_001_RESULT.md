# GE71-ANS-001 — resting heart-rate fragmentation vs lab-computed Valsalva ratio

Generated UTC: 2026-11-15T17:30:06.096040+00:00  
Plan frozen before data were read: `docs/GE71_ANS_001_PLAN.md`  
Predictor table SHA-256 (written before outcomes were parsed): `d37fb39daf449c58ed0b4b09b288d71a8036b8ce2fd02acd7a55592ecd8aabde`

**Decision under the frozen rule: NO CANDIDATE (null or inconclusive)**

## Who was analysed

```
{
 "day2_records": 57,
 "detector_disagreement": 15,
 "ok": 36,
 "ecg_qc_fail": 5,
 "no_breathing_gap": 1,
 "in_summary_table": 30,
 "missing_outcome_or_covariate": 3,
 "analysed": 27
}
```

Groups: {'control': 14, 'dm': 11, 'dmoh': 2}; sex labels: ['f', 'm']; neuropathy: {'': 1, 'no': 25, 'yes': 1}

## Models (outcome: Valsalva ratio; coefficient per 1 SD of the marker)

| Marker (adjusted for age, sex, diabetes, mean HR, log RMSSD) | n | β [95% CI] | p | Bootstrap 95% CI | R² base → full |
|---|---:|---|---:|---|---|
| **PIP (primary)** | 27 | -0.049 [-0.248, +0.150] | 0.612 | -0.220 to +0.170 | 0.18 → 0.19 |
| Deceleration capacity (benchmark) | 27 | +0.151 [-0.066, +0.368] | 0.162 | -0.072 to +0.400 | 0.18 → 0.26 |
| Hard-inflection rate (sensitivity) | 27 | -0.085 [-0.230, +0.060] | 0.235 | -0.249 to +0.053 | 0.18 → 0.24 |
| PIP, adjusted for age, sex, diabetes only | 27 | -0.029 [-0.139, +0.082] | 0.598 | -0.123 to +0.078 | 0.16 → 0.17 |
| PIP vs VMRatio2 (sensitivity) | — | — | — | — | — |

Leave-one-out range of the primary coefficient: -0.110 to +0.019

## Simple rank correlations (ρ, p)

- pip vs vr: ρ = -0.12, p = 0.566
- hr vs vr: ρ = +0.13, p = 0.513
- log rmssd vs vr: ρ = +0.21, p = 0.286
- age vs vr: ρ = +0.17, p = 0.404
- pip vs log rmssd: ρ = -0.65, p = 0.000
- pip vs age: ρ = -0.06, p = 0.751
- dc vs vr: ρ = +0.16, p = 0.437

## Quartiles (25th, median, 75th)

```
{
 "vr_all": [
  1.23,
  1.41,
  1.5739999999999998
 ],
 "pip_all": [
  59.25273480999036,
  63.69710467706013,
  72.12761855802597
 ],
 "age_all": [
  56.0,
  58.0,
  70.0
 ],
 "pip_control": [
  57.55005062216271,
  60.7415513230017,
  65.84478439630057
 ],
 "pip_diabetes": [
  60.256410256410255,
  69.35483870967742,
  75.13812154696133
 ],
 "vr_control": [
  1.26,
  1.54825,
  1.722475
 ],
 "vr_diabetes": [
  1.25,
  1.36,
  1.43
 ],
 "n_control": 14,
 "n_diabetes": 13
}
```

## Limits

- One small dataset from one lab; a single pre-specified test. Not a validated biomarker.
- Valsalva ratio is one cardiovagal reflex test, not a full autonomic battery.
- 4-minute resting window; fragmentation was developed on much longer recordings.
- Cross-sectional: association with current reflex function, not prediction of future decline.
