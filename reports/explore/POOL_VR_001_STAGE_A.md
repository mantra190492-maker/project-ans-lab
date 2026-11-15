# POOL-VR-001 stage A — automated vs lab Valsalva ratio (GE-71)

Generated UTC: 2026-11-15T17:48:47.370981+00:00

**Gap-based automated ratio validated: NO** (rule: Spearman ≥ 0.6 in ≥ 20 people)

| Comparison | n | Spearman | Median abs diff | Bias |
|---|---:|---:|---:|---:|
| gap day2 vs lab VM RATIO | 37 | 0.37 | 0.54 | +0.56 |
| gap day1 vs lab VM RATIO | 36 | -0.23 | 0.48 | +0.48 |
| marker day1 vs lab VM RATIO | 37 | 0.04 | 0.34 | +0.34 |
| gap day2 vs lab VMRatio2 | 0 | nan | nan | +nan |
| marker day1 vs lab VMRatio2 | 0 | nan | nan | +nan |
| lab VM RATIO vs lab VMRatio2 | 0 | nan | nan | +nan |
| gap day2 vs marker day1 | 34 | 0.44 | 0.29 | +0.11 |
| gap day1 vs marker day1 | 49 | 0.75 | 0.00 | +0.07 |

```
{
 "day1": {
  "records": 59,
  "template_quality_p10_25_50_75_90": [
   0.91,
   0.98,
   1.0,
   1.0,
   1.0
  ],
  "records_with_gap": 55,
  "gaps_per_record_quantiles": [
   1.0,
   2.0,
   2.0,
   3.0,
   3.0
  ],
  "records_with_vr": 52
 },
 "day2": {
  "records": 57,
  "template_quality_p10_25_50_75_90": [
   0.86,
   0.98,
   1.0,
   1.0,
   1.0
  ],
  "records_with_gap": 49,
  "gaps_per_record_quantiles": [
   0.0,
   1.0,
   2.0,
   3.0,
   3.4
  ],
  "records_with_vr": 44
 },
 "value_quantiles": {
  "gap_day1": [
   1.32,
   1.7,
   1.89,
   2.16,
   2.75
  ],
  "gap_day2": [
   1.25,
   1.71,
   1.91,
   2.44,
   2.73
  ],
  "marker_day1": [
   1.32,
   1.66,
   1.85,
   1.97,
   2.48
  ],
  "lab_VM_RATIO": [
   1.19,
   1.27,
   1.44,
   1.66,
   1.86
  ]
 }
}
```
