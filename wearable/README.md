# Project ANS — Wearable laboratory (separate track)

This folder is an **independent wearable engineering experiment**. It does not change the locked ANS biomarker-discovery mission, hypotheses or original research code. All new wearable code, tests, profile, reports and data-handling instructions remain here.

**Objective:** Test what physiological information survives realistic wrist-device sampling, noise and missingness. **NOT** a wearable diagnosis or validated ANS biomarker.

## Seven-layer architecture

| Layer | Purpose | Present status |
|---|---|---|
| L0 | Same-person source provenance and labels | Synthetic only; public wrist dataset adapter pending |
| L1 | Watch acquisition profile | 25 Hz PPG/accelerometer, 1 Hz EDA; optional temperature with explicit assumed cadence |
| L2 | Artifacts | Seeded optical noise, motion-linked interference, missing PPG |
| L3 | Quality checks | Stream consistency and data-coverage gate |
| L4 | Measurements | EDA range, motion context, temperature context; no unverified HRV |
| L5 | Fusion | Held until authentic cross-modal data and independent outcome labels |
| L6 | Clinical validation | Held: no independent ANS disease/progression ground truth |

## Source device and caveats

[Samsung's Health Sensor SDK specification](https://developer.samsung.com/health/sensor/guide/data-specifications.html) reports **25 Hz** continuous PPG, **25 Hz** accelerometer, **1 Hz** EDA (Watch8+), processed HR/IBI at **1 Hz**, and **500 Hz** *on-demand* ECG. The continuous skin-temperature tracker has no fixed output rate in that table. Foreground ECG is a short session and can affect continuous tracker reliability.

**This is NOT an official Watch emulator.** The physical optical response, device firmware, vendor IBI values, timestamps, individual skin contact and sensor noise are not recoverable from SDK specifications. Resampling WESAD BVP from 64 Hz to 25 Hz is a bandwidth test, not a faithful Samsung optical model.

## Run in repository root

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q wearable/tests
python -m wearable.experiments.watch_sim_001
```

Produces `wearable/reports/WATCH_SIM_001.json` from **synthetic** signals only (no patient records or smartwatch).

## Next real-data step

WESAD provides simultaneous wrist E4 blood-volume pulse (64 Hz), EDA (4 Hz), temperature (4 Hz), accelerometer (32 Hz), and chest ECG/respiration (700 Hz). Load each person *locally* after checking research use conditions; do not commit raw person-level source data or pass restricted data to public workflows. Do not combine our other ECG/BP cohort with WESAD as though they were the same participants.

Before computing pulse-HRV, independently validate PPG peaks against the *same person's* reference ECG. Before any ANS diagnostic accuracy claim, use independently assessed autonomic dysfunction/progression labels. WESAD's labels denote stress-related task states, **not ANS disease**.

Sources: [Samsung SDK](https://developer.samsung.com/health/sensor/guide/introduction.html), [Samsung specifications](https://developer.samsung.com/health/sensor/guide/data-specifications.html), [WESAD UCI](https://archive.ics.uci.edu/dataset/465/wesad%2Awearable%2Astress%2Aand%2Aaffect%2Adetection).

**Privacy:** The only committed outputs are aggregate diagnostics of artificial signals. Do not upload clinical waveforms, personal IDs, or restricted outcome records.

## External clinical-reference accuracy layer

The specialist measurements selected by the founder (MSNA, cardiac sympathetic imaging, peripheral small-fibre and sweat-gland morphology, corneal nerves, skin alpha-synuclein pathology, gastrointestinal, urinary, and tear/salivary function) are documented under [clinical_reference/](clinical_reference/README.md). These are **external, disease-/domain-specific comparison outcomes**, NOT wrist sensors or validated general ANS labels. Only same-person paired studies can establish whether wearable features predict them. The existing WATCH-SIM-001 remains synthetic-only.

## Real-data wrist/chest experiment (2026-11-15)

[WATCH-REAL-003 findings](reports/WATCH_REAL_003_FINDINGS.md): the first original-WESAD two-participant pilot completed. It exposed large discrepancies between automatically detected wrist-pulse and ECG heart rates and **failed 4/4 pulse-delay calibrations**. Beat-level F1 is withheld and clinical ANS/EDS accuracy is unmeasured. This is a measurement-method failure requiring further validation, **not** evidence of a discovered biomarker.
