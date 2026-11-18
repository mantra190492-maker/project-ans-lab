# Project ANS — Wearable laboratory (separate track)

This folder is an **independent wearable engineering experiment**. It does not change the locked ANS biomarker-discovery mission, hypotheses or original research code. All new wearable code, tests, profile, reports and data-handling instructions remain here.

**Objective:** Test what physiological information survives realistic wrist-device sampling, noise and missingness. **NOT** a wearable diagnosis or validated ANS biomarker.

## Engineering checkpoints (not the discovery hypothesis)

| Component | Purpose | Present status |
|---|---|---|
| L0 | Same-person source provenance and labels | Paired real WESAD wrist/chest recordings processed; stress-task labels only, no clinical disease labels |
| L1 | Watch acquisition profile | 25 Hz PPG/accelerometer, 1 Hz EDA; optional temperature with explicit assumed cadence |
| L2 | Artifacts | Seeded optical noise, motion-linked interference, missing PPG |
| L3 | Quality checks | Stream consistency and data-coverage gate |
| L4 | Measurements | EDA range, motion context, temperature context; no unverified HRV |
| L5 | Fusion | First real-data check done on **lab-scored clinic values, not watch signals**: [FUSION-001](reports/FUSION_001.md), 46 people, two domains, no demonstrated gain for separating diabetes from controls. Watch-signal fusion still held until cross-modal data and independent outcome labels exist |
| L6 | Clinical validation | Held: no independent ANS disease/progression ground truth |

## Source device and caveats

[Samsung's Health Sensor SDK specification](https://developer.samsung.com/health/sensor/guide/data-specifications.html) reports **25 Hz** continuous PPG, **25 Hz** accelerometer, **1 Hz** EDA (Watch8+), processed HR/IBI at **1 Hz**, and **500 Hz** *on-demand* ECG. The continuous skin-temperature tracker has no fixed output rate in that table. Foreground ECG is a short session and can affect continuous tracker reliability.

**This is NOT an official Watch emulator.** The physical optical response, device firmware, vendor IBI values, timestamps, individual skin contact and sensor noise are not recoverable from SDK specifications. Resampling WESAD BVP from 64 Hz to 25 Hz is a bandwidth test, not a faithful Samsung optical model.

## Run in repository root

```bash
python -m pip install -r requirements.txt pytest neurokit2 remotezip
python -m pytest -q wearable/tests
python -m wearable.experiments.watch_sim_001
```

Produces `wearable/reports/WATCH_SIM_001.json` from **synthetic** signals only (no patient records or smartwatch).

## Real-data source and clinical validation gap

WESAD provides simultaneous wrist E4 blood-volume pulse (64 Hz), EDA (4 Hz), temperature (4 Hz), accelerometer (32 Hz), and chest ECG/respiration (700 Hz). Use the original source only within its scientific/noncommercial research terms. Our controlled GitHub runners download directly from the official source; no participant-level recordings, beat arrays or personal signals are committed or published. Do not combine our other ECG/BP cohort with WESAD as though they were the same participants.

Before computing pulse-HRV, independently validate PPG peaks against the *same person's* reference ECG. Before any ANS diagnostic accuracy claim, use independently assessed autonomic dysfunction/progression labels. WESAD's labels denote stress-related task states, **not ANS disease**.

Sources: [Samsung SDK](https://developer.samsung.com/health/sensor/guide/introduction.html), [Samsung specifications](https://developer.samsung.com/health/sensor/guide/data-specifications.html), [WESAD UCI](https://archive.ics.uci.edu/dataset/465/wesad%2Awearable%2Astress%2Aand%2Aaffect%2Adetection).

**Privacy:** Committed results comprise aggregate diagnostics from both synthetic experiments and original WESAD paired recordings. No raw physiological waveforms or person-level records are committed. Never upload restricted records or identifiers.

## External clinical-reference accuracy layer

The specialist measurements selected by the founder (MSNA, cardiac sympathetic imaging, peripheral small-fibre and sweat-gland morphology, corneal nerves, skin alpha-synuclein pathology, gastrointestinal, urinary, and tear/salivary function) are documented under [clinical_reference/](clinical_reference/README.md). These are **external, disease-/domain-specific comparison outcomes**, NOT wrist sensors or validated general ANS labels. Only same-person paired studies can establish whether wearable features predict them. The existing WATCH-SIM-001 remains synthetic-only.

## Real-data wrist/chest experiment (2026-11-15)

[WATCH-REAL-003 findings](reports/WATCH_REAL_003_FINDINGS.md): the first original-WESAD two-participant pilot completed. It exposed large discrepancies between automatically detected wrist-pulse and ECG heart rates and **failed 4/4 pulse-delay calibrations**. Beat-level F1 is withheld and clinical ANS/EDS accuracy is unmeasured. This is a measurement-method failure requiring further validation, **not** evidence of a discovered biomarker.

## Corrected real-data pulse extraction (November 2026)

Across the 15 original WESAD volunteers, three **disjoint** pilot samples were used in sequence (2 development + 5 repaired-detector assessment + 8 independent sample-rate assessment). These are engineering tests without ANS disease labels.

- [Initial 2-subject measurement failure](reports/WATCH_REAL_003_FINDINGS.md): legacy wrist peak-finder grossly undercounted pulses, especially under stress.
- [Independent 5-subject detector repair](reports/WATCH_REPAIR_005_FINDINGS.md): 64Hz median absolute rate difference versus *algorithmic* chest ECG fell from **5.13 to 2.05 bpm** at rest, and **19.49 to 8.21 bpm** during stress.
- [Unseen 8-subject sample-rate correction](reports/WATCH_REPAIR_006_FINDINGS.md): 25Hz direct processing stress discrepancy **23.85 bpm**, versus **7.69 bpm** after interpolating 25Hz -> 64Hz and using the same Elgendi extractor; all 8 improved in this small study.
- The [reusable experimental extractor](signal_processing.py) now handles source-rate 25Hz and 64Hz explicitly and uses a consistent 64Hz analysis rate. It is **not clinically validated**, and interpolation does not create information missing from 25Hz recordings.
- **Still unsolved:** wrist pulse-to-ECG one-to-one event matching and independently verified clinical reference. All 10 calibration windows in the 5-subject study were withheld; no beat-level accuracy or ANS/EDS biomarker can be claimed.

For the corrected extractor use: `python -m pytest -q wearable/tests/test_signal_processing.py`. The original real-data experiment workflows preserve the frozen reproducible comparisons.

## Beat-level alignment and quality-gate findings (WATCH-SYNC-007)

[Verified 15-person WESAD timing/quality report](reports/WATCH_SYNC_007_FINDINGS.md): the wider +/-10s cross-device clock-offset search now yields meaningful **exploratory** resting wrist/ECG pulse matching, but the offset often remains rhythm-ambiguous. On the 13-person frozen timing evaluation, only **28/65 resting epochs** passed all timing and wrist quality gates (median **0.876** F1 on selected epochs); only **1/65 stress epochs** passed (F1 **0.241**, one epoch). **Do not interpret as validated sensor accuracy**, especially given no manually adjudicated WESAD ECG/PPG beat labels or proven physical timestamp alignment. Resting results are quality-selected, and stress/movement coverage is a severe blocker. Next priority: independently annotated ECG/PPG data and source-side clock verification before wearable HRV or biomarker claims.
