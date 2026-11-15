# Independent review — external HRF pre-access patch (not merged)

**Date:** 2026-11-15. **Source:** Claude-authored diff submitted by founder in chat, subject *Fix legacy HRF syntax error; add 125 Hz resolution and shared-signal null gates for SHHS-HRF-001*, commit hash claimed `e53d3f8af3dc769a1346112821131bd283887558`.

**Repository verification:** Checked current `main` with the GitHub connector. None of the seven proposed new scripts/workflows/reports/tests existed at the time of inspection, and the main SHHS protocol lacked the proposed 19-line addendum. The patch was **not applied**. Its reported `72 passed` test result, 50 GUDB recordings and Monte Carlo outputs are **external agent assertions from the diff**, not reproduced in our repository.

**Already fixed independently:** `anslab/heart_rate_fragmentation.py` contained literal `\\n` escape characters in source text that broke Python syntax. Repaired these six escapes via a small direct commit `493ac8472fc4cdf7408e79df70207eb3eaa95805`. This does not imply the rest of the patch was applied. The legacy NN-only algorithm remains flagged non-reference-equivalent.

## What the patch usefully contributes

1. **Resolution sensitivity question:** quantize manually annotated 250 Hz R-peak timestamps down to a simulated 125 Hz grid and quantify change in Costa PIP and a hard-inflections-only alternative. Reported on 50 recordings from 25 Glasgow GUDB participants. Claimed +5–7 percentage-point PIP shift. This is a relevant engineering alarm, subject to independent replication.
2. **Shared-measurement false-positive simulation:** construction where baseline ECG fragmentation contributes to baseline RMSSD, and apparent future RMSSD change is regressed on fragmentation plus baseline RMSSD. In the agent's particular simulation, false rejection occurs in 98–100% of cohorts, compared with 3–8% for a noisy simulated respiratory sinus arrhythmia phase estimator. A useful demonstration of a *possible* collider/regression-to-the-mean or shared-signal mechanism, not a general quantified false-positive rate for SHHS.
3. **Negative results are published rather than hidden.** Declaring failure before access to SHHS outcomes is consistent with the mission guardrails.

## Scientific corrections required before acceptance

### A. The agent's decisive conclusion overreaches the hypothesis

The locked hypothesis uses **visit-1 PIP only as a predictor**, then tests **visit-2 change in a separate breathing-linked cardiac vagal proxy**. It **does not** compare visit-1 and visit-2 PIP as an outcome.

Therefore, demonstrating `PIP(250 Hz) != PIP(125 Hz)` shows **non-interchangeable instrument resolution**, especially across independent replication cohorts, and risks baseline confounding and weak cross-device generalization. But **it does not logically invalidate a predictive model trained and tested using the same 125 Hz visit-1 measurement protocol**. Whether PIP independently predicts actual change, conditional on baseline HRV, is an empirical question; do not prematurely replace the primary marker with an unvalidated alternative.

### B. One subject contributes two recordings

GUDB's 50 recordings are from only **25 distinct participants**, sitting and mental-arithmetic tasks. The report presents 50 rank comparisons as though independent. Report within-person paired changes and **participant-cluster-bootstrap CIs**; assess sitting-only and task-specific shift. Using 50 recordings for point-estimate description is acceptable, but treating them as 50 independent subjects for inferential precision is not.

### C. Spearman rank code mishandles ties

The proposed `spearman()` implements `np.argsort(np.argsort(x))`, which assigns arbitrary unique ranks to ties instead of computing average ranks. This is a material problem in **quantized** 125 Hz signals where ties are common. Replace with a tie-correct Spearman function, e.g. `scipy.stats.spearmanr` or `scipy.stats.rankdata` + correlation, and require regression tests with repeated values.

### D. Claimed preregistration is not independently established

The agent says its 0.90 rank / 2.0 pp shift / 0.30 shift-vs-RMSSD rules were fixed before analysis. The same patch contains scripts and completed reports, so it is **not an external, independently time-stamped preregistration**. Treat these as transparent *agent-defined engineering thresholds*, not a prespecified clinical validity criterion. Do not replace a valid marker solely because an arbitrary non-inferiority threshold fails without considering its intended use.

### E. Simulation interpretation overstates universality

- **98–100% false positive** means a **type-I error in this specific generative model and regression**, not the real-world rate for SHHS or all RMSSD endpoints. It demonstrates a dangerous structural bias worth testing.
- **3–8% RSA rejection** is also only an assumed phase/noise simulation; real SHHS airflow/belt phase quality and sleep-stage changes may be worse. Rejection rates near 8% are borderline relative to 5% under an assumed null.
- **900–1,300 participants** is heuristic scaling from simulated power 36% at n=300, with arbitrarily selected effect size. Not a defensible SHHS power estimate.
- Do not categorically ban RMSSD from descriptive/sensitivity use. **Do not label its decline autonomic dysfunction** and do not treat an outcome derived from the predictor's exact shared NN values as independent validation. Its use must be carefully separated, potentially as a sensitivity/negative-control endpoint.

### F. Other engineering checks

- GUDB lacks trusted sinus/PVC/PAC beat-type labels. The patch uses a >30%-local-median heuristic as if non-sinus, which can mistake physiological changes or detector errors for rhythm labels. Test with verified beat-typed data and report a QC sensitivity analysis.
- Evaluate *effect on within-subject changes and clinical confounding* rather than demanding two protocol-specific PIP values be identical between recording systems. Compare native 125 Hz feature stability across short segments with longer recordings and repeated annotation.
- Validate 125 Hz quantization rules with exact-tie unit tests, fixed seeds, and tie-aware statistics.
- An optional Fantasia stage with `continue-on-error: true` must remain conspicuously *unverified* if the network fails. CI `72 passed` claimed in external workspace is not proof our repository's suite passes.
- A change in **cardiac vagal proxy** is **not clinical ANS dysfunction** without independent testing; keep G3 clinical-reference gate blocked.

## Board decision

**ACCEPT FOR REVIEW, DO NOT BLINDLY APPLY.**

- Keep the locked SHHS-HRF-001 question unchanged, do **not** immediately promote the proposed hard-inflection metric to primary.
- Implement/re-run corrected resolution and simulation experiments in a reviewable branch or controlled environment, fix ties and subject clustering, then independently verify results.
- If reference tests pass, preserve resolution and null analyses as *supporting measurement evidence* with accurate limitations; a resolution failure does not automatically kill baseline-PIP prediction.
- Hold any final OSF preregistration *until* respiratory feature availability and the native visit-1 ECG recording properties can be checked without examining visit-2 outcomes.
- Apply for NSRR study access separately; it does not authorize transferring controlled study data to GitHub/Actions.

**Status:** No original or clinically validated ANS deterioration biomarker; no restricted SHHS outcome data accessed.
