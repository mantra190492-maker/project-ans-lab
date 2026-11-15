# ANS-001 research ledger — every test, including the ones that failed

Purpose: one honest list of what has been tested, so a later "hit" can be judged against the number of attempts. A result counts as a **possibility** only if a pre-specified test passes **and** it repeats in a second dataset.

| # | ID | Question | Status | Result |
|---|---|---|---|---|
| 1 | HRF-RES-001 | Is Costa PIP stable from 250 Hz to 125 Hz? | Done (engineering) | No: +4 to +7 points at 125 Hz, larger at low HRV (GUDB n=25; Fantasia n=36, ρ ≈ −0.85) |
| 2 | HRF-NULL-001 | Can PIP falsely "predict" RMSSD decline? | Done (simulation) | Yes in the model (98–100%); breathing-locked RSA outcome 3–8% |
| 3 | SHHS-HRF-001 | Does visit-1 PIP predict loss of vagal function by visit 2? | Blocked | Needs NSRR access (founder to apply) |
| 4 | CDED-ANS-001 | Overnight PIP vs Valsalva ratio, baseline and 2-year change | Stopped before any outcome | No overnight ECG in release; no reference values in tables; visit-8 respiratory channels look corrupted |
| 5 | GE71-ANS-001 | Resting PIP vs lab-computed Valsalva ratio beyond age, sex, diabetes, HR, RMSSD | **Done — null** | β = −0.05 per SD (95% CI −0.25 to +0.15), p = 0.61, n = 27. Underpowered: only a partial correlation ≥ ~0.5 was detectable |

| 6 | POOL-VR-001 stage A | Does an automated Valsalva ratio agree with the lab's values (GE-71)? | **Done — failed, stopped** | Best Spearman 0.37 (rule: ≥ 0.60). Automated values run about 0.5 higher than the lab's. Pooled test not run |
| 7 | NAT-BREATH-001 | Heart-rate response to spontaneous large breaths as a passive deep-breathing test | **Dropped before any test** | Prior art: heart-rate variation with deep breathing is the established cardiovagal test, and respiratory sinus arrhythmia in diabetic neuropathy has been studied since the 1980s. With ~4 minutes of rest in ~35 people it could not show added value over RMSSD |
| 8 | FUSION-001 | Do two autonomic domains together separate diabetes from controls better than one? (founder request, 2026-11-15) | **Done — no demonstrated gain** | n = 46 (25 diabetes, 21 control), lab-scored values. Leave-one-out AUC: Valsalva 0.36, tilt pressure 0.56, both 0.52 (95% CI 0.35–0.69). Gain −0.05. The two domains are uncorrelated (ρ = −0.08) but neither separates diabetes from controls here. Report: `wearable/reports/FUSION_001.md` |
| 9 | TILT-001 | Resting PIP vs lab-computed heart-rate response to tilt, beyond age, sex, diabetes, resting HR, RMSSD | **Done — null** | β = +0.4 bpm per SD (95% CI −3.7 to +4.4), p = 0.85, n = 29. Report: `reports/explore/TILT_001_RESULT.md` |

Outcome-level hypothesis tests run so far: **3** (GE71-ANS-001, FUSION-001, TILT-001). Candidates found: **0**.

Practical note: physionet.org timed out from GitHub runners for ~45 minutes on 2026-11-15; open-access files are also served from `https://physionet-open.s3.amazonaws.com/<project>/<version>/...`.

## Notes from GE71-ANS-001 that must not be treated as findings

- Post hoc, descriptive only: median resting PIP was 69 in diabetes vs 61 in controls. Not pre-specified, not adjusted, n = 13 vs 14.
- Even expected relationships (age or RMSSD vs Valsalva ratio) were not visible at n = 27, so this dataset alone cannot settle the question.
- 15 of 57 records were lost to the two-detector agreement check. The check is outcome-blind, but relaxing it now on the same data would be a forking path. Improve ECG quality control only in the next, separately frozen plan.

## Open-data queue (fixed order; each needs its own frozen plan before outcomes are computed)

1. **POOL-VR-001:** automated Valsalva ratio from ECG + pressure across CDED visit 2 (69 people) and GE-75 (52), first validated against the lab's values in GE-71. Then one pooled test of resting PIP, independent of the 27 people already analysed.
2. **NAT-BREATH-001:** passive stand-in for the deep-breathing test: heart-rate response to spontaneous large breaths at rest vs the formal deep-breathing and Valsalva results (GE-71 Day 1 has a marked deep-breathing test). Needs a prior-art check first.
3. **TILT-001:** resting markers vs head-up-tilt heart-rate and pressure response (neurogenic pattern: pressure falls ≥20 mmHg with a blunted heart-rate rise).

Stopping rule: stop when a candidate replicates, or when this queue is exhausted. No fourth open-data experiment without the founder's go-ahead. Larger tests need NSRR (SHHS/MrOS) or a clinical-cohort partner.

## Open-data verdict — 2026-11-15

The fixed queue is exhausted. No candidate.

- Every outcome test had 27–46 people, enough only for large effects. The results are "not shown", not "disproved".
- About 40% of GE-71 Day-2 resting ECGs failed outcome-blind quality checks under either rule (two-detector agreement, or beat-shape consistency plus usable-beat fraction).
- In 4-minute resting windows PIP tracked RMSSD closely (ρ = −0.65 in both analyses), so at this recording length it largely re-measures ordinary HRV. Fragmentation was developed on overnight recordings.
- The automated Valsalva ratio did not reproduce the lab's values, so self-computed reflex outcomes cannot yet extend the sample to CDED or GE-75.

Routes that can answer the question:
1. **NSRR (SHHS, MrOS):** thousands of people, overnight ECG, two visits. Founder to apply.
2. **A clinic cohort with a full reflex battery** (and a sweat test): the only way to test early detection of confirmed dysfunction, and the three-domain idea.

Not run, needs the founder's go-ahead under the stopping rule: **DIAB-PIP-001**, resting PIP in type 2 diabetes vs controls pooled over CDED visit 2 and GE-75 (about 120 people), prompted by the post hoc difference noted above. Diabetes status is an at-risk label, not autonomic dysfunction.
