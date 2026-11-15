# FUSION-001 — do two autonomic domains together beat one?

**Frozen 2026-11-15 before any tilt value, or any Valsalva value by group, was read.** Requested by the founder as the first real-data check of the layered ("three position lines") idea.

## What this can and cannot test

- **Data:** GE-71 summary table (PhysioNet "Cerebral Vasoregulation in Diabetes", DOI 10.13026/m40k-4758, CC BY 4.0). It holds **lab-scored** results for two of the three core domains in the same people: cardiovagal (Valsalva ratio) and adrenergic (blood-pressure response to head-up tilt). There is no sweat (sudomotor) test in any open dataset found, so the third layer is untested here.
- **These are clinic-grade measurements, not watch signals.** The result is an upper bound: if fusion does not help with lab-grade inputs, noisier home versions are unlikely to do better.
- **Label:** type 2 diabetes vs control. The dataset's nerve-damage flag is too sparse to use (1 of 27 in the earlier sample), and the "diabetes with orthostatic hypotension" group is defined by the blood-pressure response itself, so using it would be circular. Diabetes status is an at-risk label, **not** confirmed autonomic dysfunction.

## Locked analysis

- **People:** table rows with Valsalva ratio (`VM RATIO` ≥ 0.9), `SBP TILT BASELINE1`, `TILT AVE1`, `HR TILT BASELINE`, `TILT AVE`, `Age`, `Gender`, `Group`.
- **Cardiovagal measure:** Valsalva ratio. **Adrenergic measure:** tilt systolic change = tilt average − supine baseline (mmHg).
- **Models:** ridge-penalised logistic regression, all with age and sex. M0 age + sex; M1 + cardiovagal; M2 + adrenergic; M3 + both. Features standardised inside each training fold.
- **Score:** leave-one-out cross-validated AUC.
- **Independence check:** Spearman correlation between the two domain measures (age-adjusted partial correlation reported too).
- **Decision rule:** fusion "adds" only if AUC(M3) exceeds the better single-domain model by ≥ 0.05 **and** the participant-bootstrap 95% CI of that difference (2,000 resamples of out-of-fold predictions) excludes 0. Otherwise: no demonstrated gain.
- **Honest power note:** about 45 people. AUC is uncertain by roughly ±0.15, so only a large gain can pass. A failure here means "not shown", not "fusion is useless".
- Secondary, descriptive only: tilt heart-rate change as a third feature; AUC of each single measure.

No other labels, features or cut-offs will be tried on this table under this plan.
