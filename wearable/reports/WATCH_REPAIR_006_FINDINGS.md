# WATCH-REPAIR-006 — Repaired 25Hz wrist-processing failure

**Status: successful correction of a specific algorithmic sample-rate problem in the WESAD pulse-rate pilot.** This does not constitute independent medical accuracy verification or pulse-by-pulse ECG validation.

This experiment was **specified before inspecting the next eight WESAD participants** (all eight remaining after the first 2 development and subsequent 5 evaluation participants). We compared a fixed published pulse extractor on the *same* wrist signal recorded at 64Hz, digitally downsampled to 25Hz, and then optionally reconstructed by band-limited interpolation to 64Hz **before running that same pulse extractor**.

## Result on 8 further people, independent from the first 7

Run: [GitHub Actions 43756912806](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43756912806), successful; **13 regression tests passed**. 180-second contiguous baseline and stress windows, BPM comparison measured from seconds 60–177. All 8 participants produced valid rate pairs in each condition.

| Median *within-person absolute difference* vs algorithmic chest ECG | Resting | Stress |
|---|---:|---:|
| Wrist original 64Hz BVP with NeuroKit2 Elgendi | 1.54 bpm | 7.44 bpm |
| 25Hz BVP with direct 25Hz Elgendi processing | 2.05 bpm | **23.85 bpm** |
| **25Hz BVP -> interpolated 64Hz -> same Elgendi pulse extractor** | **1.54 bpm** | **7.69 bpm** |

Paired improvement with interpolation:
- Stress: **8/8 people improved**, paired median change in absolute discrepancy **-14.10 bpm**; none worsened.
- Rest: **6/8 improved**, 2 worsened; paired median change **-1.03 bpm**.

The corrected 25Hz analysis pipeline *behaved much more like the original 64Hz extraction algorithm*. This supports a **software sampling-rate sensitivity issue** as a major cause of the previous 25Hz degradation. **Interpolating cannot restore physiologic information removed by prior sampling/anti-aliasing.** This is not evidence that any specific 25Hz optical smartwatch gives equally good readings.

## Decisions

1. **Adopt as an experimental pulse-rate processing option** the 25Hz to 64Hz polyphase interpolation followed by NeuroKit2 Elgendi, with explicit source-rate handling. Implemented in [wearable/signal_processing.py](../signal_processing.py); separate from the frozen diagnostic comparisons.
2. **Do not report beat-event F1 or diagnostic sensitivity**: original WESAD ECG and wrist clocks are not independently validated at beat-level precision in our pipeline, and previous first-minute calibration failed 10/10 cases.
3. **Reject the old fixed-prominence wrist pulse finder as the default research extractor.** It undercounted pulses severely under stress.
4. **Next independent reference experiment:** obtain annotated ECG and PPG beat timestamps or manually adjudicated same-person pulse periods; verify pulse transit delay/synchronization with movement and signal quality gates; test additional hardware datasets and prospective clinical reference, before biomarkers.

## Source and limitations

Original WESAD synchronized wrist BVP (Empatica E4 64Hz) and chest RespiBAN ECG (700Hz); Schmidt et al., ICMI 2018, DOI 10.1145/3242969.3242985. Dataset permits scientific/noncommercial use with attribution. Only aggregate metrics appear in public GitHub.

ECG is estimated by NeuroKit2 from the chest waveform, with agreement to a second algorithm required, **not human-labelled ground truth**. Stress is an experimental task, not a diagnosed autonomic disorder. **No clinical ANS deterioration, EDS detection, specificity, sensitivity, or novel biomarker established.**

Code: [Experiment 006](../experiments/wesad_repair_006.py), [three evaluation safeguard tests](../tests/test_wesad_repair_006.py), [source run and result artifact](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43756912806). Artifact retention 14 days. Freeze these original comparison results; any later tuning requires new participant-held-out data.
