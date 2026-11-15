# WATCH-SYNC-007 — Wrist/chest beat alignment and signal-quality evaluation

**Decision: Partially improved at rest; NOT resolved during stress. DO NOT promote beat-level metrics into biomarker models.**

## Sources and design

- Original synchronized WESAD chest RespiBAN ECG (700Hz) and wrist Empatica E4 BVP (64Hz), **15 people total**, no disease diagnoses.
- WESAD's devices were synchronized via double-tap markers in the original study. The .pkl format does not provide independently verified per-sample physical hardware timing.
- Published PPG beat research on WESAD (Pettit, Charlton & Aston, Frontiers in Physiology, 2024; DOI 10.3389/fphys.2024.1228439) searched an alignment offset in +/-10 seconds. This invalidated our original WATCH-REAL-003 software's simplistic 0.05-0.55 s assumption. The existing offset is therefore treated as a **cross-device empirical alignment**, not physiological pulse transit time.
- Two initial development participants. An initial synthetic-regression failure exposed a full-heartbeat-alias bug, and we corrected the lag-selection tie-break to use lower timing residual. **Six synthetic checks passed** before a subsequent, fixed evaluation on 13 additional people. Those 13 had previously participated in other rate-processing experiments but not in WATCH-SYNC-007 timing-alignment development.
- **Prespecified temporal split in every 180-second real window:** choose lag from ECG 10-30s, confirm it using ECG 30-50s against wrist pulses observed before 60s; assess beat matching at 70-170s. The test windows never adjust lag.
- Evaluate five nonoverlapping 20-second epochs for each condition. ECG quality requires two independent algorithms to agree (F1 >=.98 at 120ms); wrist quality requires periodicity autocorrelation >=.40, plausible beat intervals and enough pulses.
- Positive matching tolerance +/-150ms and single-use ECG/PPG pulse pairing. All data/log outputs are **aggregate only**, no subject-level waveforms, beat arrays or identifiers.

## Observed results

| Item | Development (2 people) — rest | Development — stress | Frozen-method evaluation (13 people) — rest | Evaluation — stress |
|---|---:|---:|---:|---:|
| Confirmed training-window clock calibration | 2/2 | 1/2 | **8/13** | **2/13** |
| Epochs admitted after timing + morphology gates | **4/10 (40%)** | **1/10 (10%)** | **28/65 (43.1%)** | **1/65 (1.5%)** |
| Participants with >=1 accepted matching epoch | 2 | 1 | **8** | **1** |
| Median per-participant F1 across accepted epochs | 0.905 | 0.241 | **0.876** | **0.241 (one epoch only)** |
| Ambiguous selected clock offsets | 2/2 | 2/2 | **11/13** | **12/13** |
| Median PPG morphology autocorrelation (descriptive) | 0.462 | 0.270 | **0.491** | **0.249** |

**Important conditioning:** Resting F1 is computed on a quality-selected minority of observed windows, NOT all wrist measurements. Stress F1 only represents **one window** in the 13-person validation cohort, so it cannot estimate stress accuracy. Many candidate lags are beat-period aliases, and even good algorithmic agreement does not prove exact wrist-to-chest physical timing. No manually adjudicated ECG beats were used in WATCH-SYNC-007.

**Reference sanity check:** Chest ECG peaks are compared using two established automated methods before accepting an F1 window. This is a software-consistency gate, **not** independent adjudicated ground truth.

## Decision after 13-person run

1. **Retain** the widened, calibration-only +/-10s search as a diagnostic alignment method for exploratory clean resting data. Never interpret its offset as pulse transit time.
2. **Retain** explicit signal-quality gates and report their coverage, not only selected-window F1. The high rejection during stress is a major engineering failure, not an algorithm success.
3. **Withhold** claims of wrist-derived HRV accuracy, beat timing, smartwatch transferability, early ANS deterioration or EDS detection. All relevant WESAD labels are stress tasks, not dysautonomia.
4. **Next needed evidence:** Independently validated ECG/PPG pulse annotations and source-side clock synchronization, including externally synchronized inertial markers or vendor timestamps. Then test an artifact-tolerant PPG detector and quantify false rejection versus signal quality without reusing this 13-subject set as untouched validation data.
5. **Research go/no-go:** No HRV or time-based multimodal biomarker model proceeds from WESAD wrist streams until beat-level timing is independently established and the stress/motion coverage problem is solved.

## Exact reproducibility

- [WATCH-SYNC-007 runner](../experiments/wesad_sync_007.py) and [six regression checks](../tests/test_wesad_sync_007.py).
- [Two-person development run 43758310477](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43758310477) (completed successfully, tests passed).
- [13-person fixed-method test run 43758468481](https://github.com/mantra190492-maker/project-ans-lab/actions/runs/43758468481) (completed successfully, tests passed, retained aggregate-only JSON artifact for 14 days).
- Original paper: Schmidt et al., 2018, DOI 10.1145/3242969.3242985, WESAD scientific/noncommercial data; alignment prior art: Pettit, Charlton & Aston, 2024, DOI 10.3389/fphys.2024.1228439.

**No new biomarker found. Engineering timing calibration improved relative to the earlier false 0.55s cutoff; stress data remain poorly usable.**
