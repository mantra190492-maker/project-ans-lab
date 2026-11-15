# ANS-001 research ledger — every test, including the ones that failed

Purpose: one honest list of what has been tested, so a later "hit" can be judged against the number of attempts. A result counts as a **possibility** only if a pre-specified test passes **and** it repeats in a second dataset.

| # | ID | Question | Status | Result |
|---|---|---|---|---|
| 1 | HRF-RES-001 | Is Costa PIP stable from 250 Hz to 125 Hz? | Done (engineering) | No: +4 to +7 points at 125 Hz, larger at low HRV (GUDB n=25; Fantasia n=36, ρ ≈ −0.85) |
| 2 | HRF-NULL-001 | Can PIP falsely "predict" RMSSD decline? | Done (simulation) | Yes in the model (98–100%); breathing-locked RSA outcome 3–8% |
| 3 | SHHS-HRF-001 | Does visit-1 PIP predict loss of vagal function by visit 2? | Blocked | Needs NSRR access (founder to apply) |
| 4 | CDED-ANS-001 | Overnight PIP vs Valsalva ratio, baseline and 2-year change | Stopped before any outcome | No overnight ECG in release; no reference values in tables; visit-8 respiratory channels look corrupted |
| 5 | GE71-ANS-001 | Resting PIP vs lab-computed Valsalva ratio beyond age, sex, diabetes, HR, RMSSD | **Done — null** | β = −0.05 per SD (95% CI −0.25 to +0.15), p = 0.61, n = 27. Underpowered: only a partial correlation ≥ ~0.5 was detectable |

Outcome-level hypothesis tests run so far: **1** (GE71-ANS-001). Candidates found: **0**.

## Notes from GE71-ANS-001 that must not be treated as findings

- Post hoc, descriptive only: median resting PIP was 69 in diabetes vs 61 in controls. Not pre-specified, not adjusted, n = 13 vs 14.
- Even expected relationships (age or RMSSD vs Valsalva ratio) were not visible at n = 27, so this dataset alone cannot settle the question.
- 15 of 57 records were lost to the two-detector agreement check. The check is outcome-blind, but relaxing it now on the same data would be a forking path. Improve ECG quality control only in the next, separately frozen plan.

## Open-data queue (fixed order; each needs its own frozen plan before outcomes are computed)

1. **POOL-VR-001:** automated Valsalva ratio from ECG + pressure across CDED visit 2 (69 people) and GE-75 (52), first validated against the lab's values in GE-71. Then one pooled test of resting PIP, independent of the 27 people already analysed.
2. **NAT-BREATH-001:** passive stand-in for the deep-breathing test: heart-rate response to spontaneous large breaths at rest vs the formal deep-breathing and Valsalva results (GE-71 Day 1 has a marked deep-breathing test). Needs a prior-art check first.
3. **TILT-001:** resting markers vs head-up-tilt heart-rate and pressure response (neurogenic pattern: pressure falls ≥20 mmHg with a blunted heart-rate rise).

Stopping rule: stop when a candidate replicates, or when this queue is exhausted. No fourth open-data experiment without the founder's go-ahead. Larger tests need NSRR (SHHS/MrOS) or a clinical-cohort partner.
