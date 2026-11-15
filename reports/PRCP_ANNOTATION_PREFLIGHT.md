# PRCP — Source annotation feasibility audit

Generated UTC: 2026-11-15T14:38:25.160460+00:00
Dataset: https://physionet.org/content/prcp/1.0.0/
DOI: 10.13026/C2PC7R

**Purpose:** Read public metadata, QRS annotations, ABP annotations and
posture/event annotation **codes** before any response-curve or ANS
deterioration calculation. No waveforms or participant-level physiological
features were saved or committed.

| Record | Sampling Hz | Signal names | anI markers | QRS annotations | ABP annotations | Status |
|---|---:|---|---:|---:|---:|---|
| 12726 | 250.0 | ABP, ECG, Angle | 22 | 3653 | 3668 | Inspected |
| 12734 | 250.0 | ABP, ECG, Angle | 20 | 3273 | 3249 | Inspected |
| 12744 | 250.0 | ABP, ECG, Angle | 21 | 4951 | 4850 | Inspected |
| 12754 | 250.0 | ABP, ECG, Angle | 21 | 5228 | 5130 | Inspected |
| 12755 | 250.0 | ABP, ECG, Angle | 21 | 4149 | 4045 | Inspected |
| 12814 | 250.0 | ABP, ECG, Angle | 24 | 4390 | 4331 | Inspected |
| 12815 | 250.0 | ABP, ECG, Angle | 29 | 4931 | 4679 | Inspected |
| 12819 | 250.0 | ABP, ECG, Angle | 20 | 5642 | 5539 | Inspected |
| 12821 | 250.0 | ABP, ECG, Angle | 20 | 4232 | 4126 | Inspected |
| 13960 | 250.0 | ABP, ECG, Angle | 26 | 3513 | 3469 | Inspected |

## Source annotation vocabulary — do not assume semantics

### Record 12726

- Event annotation `.anI` symbol counts: `{"\"": 22}`
- Event annotation `.anI` aux-note vocabulary: `{"Conclude rapid tilt down": 2, "Conclude rapid tilt up": 2, "Conclude slow tilt down": 2, "Conclude slow tilt up": 2, "Initiate rapid tilt down": 2, "Initiate rapid tilt up": 2, "Initiate slow tilt down": 2, "Initiate slow tilt up": 2, "Lost ECG signal due to poor electrode-skin contacL": 1, "Movement artifacts": 1, "Stand up": 2, "Transition back to supine": 2}`
- First/last marker sample: 87240 / 769963

### Record 12734

- Event annotation `.anI` symbol counts: `{"\"": 20}`
- Event annotation `.anI` aux-note vocabulary: `{"Back to supine": 2, "End fast tilt down": 1, "End fast tilt up": 1, "End rapid tilt down": 1, "End rapid tilt up": 1, "End slow tilt back down": 1, "End slow tilt down": 1, "End slow tilt up": 2, "Stand-up from supine": 2, "Start fast tilt down": 1, "Start fast tilt up": 1, "Start rapid tilt down": 1, "Start rapid tilt up": 1, "Start slow tilt down": 2, "Start slow tilt up": 2}`
- First/last marker sample: 75175 / 792294

### Record 12744

- Event annotation `.anI` symbol counts: `{"\"": 21}`
- Event annotation `.anI` aux-note vocabulary: `{"Conclusion of rapid tilt dow": 1, "Conclusion of rapid tilt down": 1, "Conclusion of rapid tilt up": 2, "Conclusion of slow tilt down": 2, "Conclusion of slow tilt up": 2, "Initiation of rapid tilt down": 2, "Initiation of rapid tilt up": 2, "Initiation of slow tilt down": 2, "Initiation of slow tilt up": 2, "Misfire of marker signal": 1, "Stand up": 2, "Transition back to supine": 2}`
- First/last marker sample: 96414 / 854350

### Record 12754

- Event annotation `.anI` symbol counts: `{"\"": 21}`
- Event annotation `.anI` aux-note vocabulary: `{"0 -1 0 \tStand up": 1, "Conclude rapid tilt down": 2, "Conclude rapid tilt up": 2, "Conclude slow tilt dow": 1, "Conclude slow tilt down": 1, "Conclude slow tilt up": 2, "ECG noise due to poor electrode contact": 1, "Initiate rapid tilt down": 2, "Initiate rapid tilt up": 2, "Initiate slow tilt down": 2, "Initiate slow tilt up": 2, "Stand up": 1, "Transition back to supine": 2}`
- First/last marker sample: 87961 / 832919

### Record 12755

- Event annotation `.anI` symbol counts: `{"\"": 21}`
- Event annotation `.anI` aux-note vocabulary: `{"Conclude slow tilt down": 1, "Conclude slow tilt up": 1, "Conclusion of rapid tilt dow": 1, "Conclusion of rapid tilt up": 1, "Conclusion of slow tilt down": 1, "Conclusion of slow tilt up": 1, "Failed attempt to tilt rapidly": 1, "Initiate rapid tilt down": 2, "Initiate rapid tilt up": 2, "Initiate slow tilt down": 1, "Initiate slow tilt up": 1, "Initiation of rapid tilt down": 1, "Initiation of rapid tilt up": 1, "Initiation of slow tilt down": 1, "Initiation of slow tilt up": 1, "Stand up": 2, "Transition back to supine": 2}`
- First/last marker sample: 81636 / 832533

### Record 12814

- Event annotation `.anI` symbol counts: `{"\"": 24}`
- Event annotation `.anI` aux-note vocabulary: `{"Conclude rapid tilt down": 2, "Conclude rapid tilt up": 2, "Conclude slow tilt down": 2, "Conclude slow tilt up": 2, "ECG signal is back": 2, "Initiate rapid tilt down": 2, "Initiate rapid tilt up": 2, "Initiate slow tilt down": 2, "Initiate slow tilt up": 2, "Loss of ECG signal": 2, "Stand up": 2, "Transition back to supine": 2}`
- First/last marker sample: 91148 / 820370

### Record 12815

- Event annotation `.anI` symbol counts: `{"\"": 29}`
- Event annotation `.anI` aux-note vocabulary: `{"Blood pressure artifacts": 1, "Blood pressure signal fades": 2, "Conclusion of rapid tilt down": 1, "Conclusion of rapid tilt up": 2, "Conclusion of slow tilt down": 2, "Conclusion of slow tilt up": 2, "Initiation of rapid tilt down": 3, "Initiation of rapid tilt up": 2, "Initiation of slow tilt down": 2, "Initiation of slow tilt up": 2, "Stand up": 2, "Switched Finapres on": 3, "Switched off Finapres": 3, "Transition back to supin": 1, "Transition back to supine": 1}`
- First/last marker sample: 91915 / 927390

### Record 12819

- Event annotation `.anI` symbol counts: `{"\"": 20}`
- Event annotation `.anI` aux-note vocabulary: `{"Conclusion of rapid tilt down": 2, "Conclusion of rapid tilt up": 2, "Conclusion of slow tilt down": 1, "Conclusion of slow tilt up": 2, "Conslusion of slow tilt down": 1, "Initiation of rapid tilt down": 2, "Initiation of rapid tilt up": 2, "Initiation of slow tilt down": 2, "Initiation of slow tilt up": 2, "Stand-up": 2, "Transition back to supine": 2}`
- First/last marker sample: 116645 / 1041582

### Record 12821

- Event annotation `.anI` symbol counts: `{"\"": 20}`
- Event annotation `.anI` aux-note vocabulary: `{"Conclude rapid tilt down": 2, "Conclude rapid tilt up": 2, "Conclude slow tilt dow": 1, "Conclude slow tilt down": 1, "Conclude slow tilt up": 1, "Initiate rapid tilt down": 2, "Initiate rapid tilt up": 2, "Initiate slow tilt down": 2, "Initiate slow tilt up": 3, "Stand up": 2, "Transition back to supine": 2}`
- First/last marker sample: 117164 / 869279

### Record 13960

- Event annotation `.anI` symbol counts: `{"\"": 26}`
- Event annotation `.anI` aux-note vocabulary: `{"Blood pressure signal back up": 1, "Blood pressure signal faded": 1, "Blood pressure signal faded again": 1, "Break in signal": 1, "Conclude rapid tilt down": 2, "Conclude rapid tilt up": 2, "Conclude slow tilt dow": 1, "Conclude slow tilt down": 1, "Conclude slow tilt up": 2, "Initiate rapid tilt down": 2, "Initiate rapid tilt up": 2, "Initiate slow tilt down": 2, "Initiate slow tilt up": 2, "Stand up": 2, "Switched FINAPRES back on": 1, "Switched off FINAPRES": 1, "Transition back to supine": 2}`
- First/last marker sample: 1641 / 839110

## Required next interpretation step

- Match event/annotation vocabulary to the official PRCP study protocol.
- **Manually verify** that posture-onset annotations correspond to actual waveform transitions, without assuming `.anI` is a gold-standard task-label file.
- Distinguish active stand, slow tilt and rapid tilt; never pool the protocols into one repeated-challenge benchmark.
- Before any clinical claims, verify whether repeatable events are correctly time-aligned; report negative controls and incomplete cases.
- This source only contains **ten healthy subjects**. It cannot by itself validate ANS dysfunction diagnosis or longitudinal deterioration.

[Measurement validation protocol](../docs/EXPERIMENT_002_ANS_DYSFUNCTION_MEASUREMENT_GATE.md)
