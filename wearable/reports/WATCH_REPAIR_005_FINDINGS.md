# WATCH-REPAIR-005 — Independent-detector repair, unseen WESAD sample

**Status: PARTIALLY RECTIFIED (engineering fidelity improved; timing and 25-Hz stress performance not solved).**

The original WATCH-REAL-003 trial on 2 WESAD subjects demonstrated a wrist peak-detection fault. A subsequent independent detector diagnostic on those 2 development subjects compared the legacy ECG/BVP detector with NeuroKit2 ECG and Elgendi PPG detectors. The legacy wrist peak finder produced ~58-60 beats/min across resting and stress periods despite strong evidence from two closely agreeing ECG algorithms of a substantial physiological rise in heart rate. A secondary ECG check implicated pulse detection rather than chest peak detection, but it is not manually adjudicated ECG truth.

## Independent test — five additional participants

Workflow: [WATCH REPAIR 005 run 43756399790](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43756399790) — **completed, successful**, 10 regression tests passed.

Original WESAD synchronized chest/wrist recordings, **five additional participants** (offset 2, excluding the two preliminary diagnostic subjects); 180-second baseline/stress windows, evaluating seconds 60-177. Same participants, same windows, original legacy versus repaired wrist algorithms. Independent chest ECG algorithms must agree F1>=0.98 at 120 ms tolerance before accepting rate pairs.

| Metric: median within-participant absolute rate discrepancy versus algorithmic chest ECG | Baseline (5 participants) | Stress (5 participants) |
|---|---:|---:|
| Legacy pulse detector on wrist BVP 64 Hz | 5.13 bpm | 19.49 bpm |
| **Repaired NeuroKit2 Elgendi wrist detector, BVP 64 Hz** | **2.05 bpm** | **8.21 bpm** |
| Repaired detector on anti-aliased 25 Hz BVP proxy | 2.05 bpm | **22.05 bpm** |
| Independent ECG detector beat-matching F1, median | 1.000 | 1.000 |
| Matched individual ECG/wrist pulse F1 | WITHHELD | WITHHELD |
| Calibration success for individual beat comparisons | 0/5 | 0/5 |

The new wrist detector reduced median rate discrepancy about 60% during baseline and about 58% during stress, relative to the old wrist algorithm in the unseen five-person sample. **This is not an estimate of true clinical accuracy:** the ECG comparator remains algorithmic, both ECG methods share the same source waveform, and no manual annotation ground truth exists in this experiment.

**Key negative result:** Simply resampling to 25 Hz and applying the same pulse detector did **not** preserve 64-Hz performance under stress; the 25-Hz median discrepancy (22.05 bpm) was worse than the original 64-Hz legacy detector (19.49 bpm). Do not claim watch-hardware readiness.

**Second negative result:** ECG-to-wrist calibration using only the first minute failed in **10/10** (5 baseline, 5 stress). Consequently, one-to-one pulse F1 was deliberately left null. An acceptable mean rate discrepancy cannot establish beat-by-beat timing quality.

## Decision

**RETAIN:** NeuroKit2 Elgendi BVP pulse detection as the current stronger experimental baseline, subject to independent validation.

**REJECT:** The older fixed-prominence/simple wrist peak finder as the default research signal extractor. Preserve it as a frozen negative-control comparator for reproducibility.

**WITHHOLD:** Claims about beat-level PPG accuracy, 25-Hz smartwatch-class viability under stress, novel ANS markers, early ANS deterioration or EDS prediction.

**Next experiments:** validate ECG R-peaks against manually annotated signals; find independent pulse or PPG beat annotations; determine whether calibration failure reflects wrist artifacts, pulse morphology, device timestamps, or offset; test dedicated lower-rate pulse extraction with person-held-out evaluation rather than retuning on the five evaluation subjects. Motion and external respiration must be addressed in subsequent models.

## Reproducibility

- Repaired pipeline: [wesad_repair_005.py](../experiments/wesad_repair_005.py)
- Regression gates: [test_wesad_repair_005.py](../tests/test_wesad_repair_005.py)
- Diagnostic: [wesad_diagnostic_004.py](../experiments/wesad_diagnostic_004.py)
- CI reproducibility: [run 43756399790](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43756399790) (includes aggregate-only JSON artifact, 14-day retention).
- Raw source: WESAD (Schmidt et al., ICMI 2018, DOI 10.1145/3242969.3242985). Scientific/noncommercial access with attribution. No subject-level output, individual waveforms, or private identifiers published in GitHub.
- The code's default `--offset 2` reserves the initial two subjects as development data; the five-subject pilot was run as `--offset 2 --limit 5`. Later reuse of these five cases is no longer an untouched external validation set.
- WESAD labels **stress tasks only**. Zero clinical ANS/EDS disease labels. No sensitivity/specificity measured.

**Experiment completed on real paired data. Problem partially solved; two major engineering limitations remain.**
