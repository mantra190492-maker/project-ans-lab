# ANS-001 — Real annotated heartbeat fragmentation feasibility

Dataset: [Fantasia v1.0.0](https://physionet.org/content/fantasia/1.0.0/), DOI 10.13026/C2RG61.
Generated UTC: 2026-11-15T13:49:57.510544+00:00

**Engineering-only results: these values do not predict disease, ageing rate, or longevity.**
All subjects were screened healthy and recorded while resting and watching a film.
Inputs are visually verified beat annotation files; no patient-level waveforms or identifiers were committed.

| Record | Published age band | Annotated beats | QC eligible | PIP 4 ms | PIP 8 ms | W1 4 ms | RMSSD (ms) | Data status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| f1y01 | 21-34 | 388 | 100.0% | 49.09% | 51.43% | 51.44% | 84.01 | Processed |
| f1o01 | 68-85 | 309 | 100.0% | 65.36% | 53.59% | 19.41% | 13.53 | Processed |
| f2y01 | 21-34 | 350 | 100.0% | 67.72% | 70.61% | 15.65% | 52.96 | Processed |
| f2o01 | 68-85 | 338 | 88.7% | — | — | — | — | Withheld: Insufficient quality-screened sinus NN intervals |

## Interpretive gates
- Sampling-resolution sensitivity is reported because changing the ternary difference threshold changes PIP even with the same biology.
- Beat types other than N are excluded without joining disconnected intervals across gaps.
- Per-record preflight counts distinguish non-N beat annotations and implausible intervals. An excluded record is NOT reclassified as healthy by relaxing quality rules.
- Fantasia labels are visually verified but this does not prove all sinus intervals are free of physiological complexity.
- Four selected healthy participants cannot establish group difference, prognostic accuracy or a clinical cut-off.
- This result **must not** be used to train an age score, infer disease or claim mortality prediction.
- Actual next test: verified sinus Holters in MUSIC with clinical outcome and censoring controls.

Source PIP definition: [Costa et al., 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6129761/).
