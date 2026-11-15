# CDED-ANS-001 stage 1 — dataset structure (no outcome analysis)

Generated UTC: 2026-11-15T17:00:11.978074+00:00  
Source: https://physionet.org/files/cded/1.0.1/ (CC BY 4.0, DOI 10.13026/00bm-0x81)

- Files: 347; WFDB records: 157 ({'labview_visit2': 69, 'labview_visit8': 41, 'ecg_24h': 47})
- Participants with any record: 78
- **Both lab visits (baseline + 2 years): 41**
- 24-h ECG + baseline lab: 38; 24-h ECG + both lab visits: 23
- Non-WFDB/annotation-like extensions: none
- Header read failures: 4

## Record types

### labview_visit2 (n=68)

- Sampling rates: {'500.0': 68}; multi-segment headers: 0
- Duration (min): {'min': 31.1, 'median': 34.5, 'max': 99.6}
- Channels: marker (68), ecg (68), abp (68), mcar (68), mcal (68), Radi (68), thermst (68), flow_rate (68), o2 (68), co2 (68)

### labview_visit8 (n=39)

- Sampling rates: {'500.0': 39}; multi-segment headers: 0
- Duration (min): {'min': 28.5, 'median': 81.6, 'max': 94.3}
- Channels: marker (39), ecg (39), abp (39), mcar (39), mcal (39), Radi (39), thermst (39), flow_rate (39), o2 (39), co2 (39)

### ecg_24h (n=46)

- Sampling rates: {'1000.0': 46}; multi-segment headers: 0
- Duration (min): {'min': 6.1, 'median': 6.3, 'max': 42.3}
- Channels: emg_0 (46), emg_1 (46), emg_2 (24), emg_3 (24), emg_4 (24), emg_5 (24), emg_6 (24), emg_7 (24), ecg_0 (22), ecg_1 (22), sensor_0 (22), sensor_1 (22), accelerometer_0 (22), accelerometer_1 (22)

## Summary-table variables matching autonomic/diabetes keywords

- BETA BLOCKERS
- Diabetic Medication Taken
- Dizziness AUTONOMIC SYMPTOMS
- Numbness AUTONOMIC SYMPTOMS
- OH AUTONOMIC SYMPTOMS
- Painful feet AUTONOMIC SYMPTOMS
- Syncope AUTONOMIC SYMPTOMS

## Stage 2 gate

Stage 2 (the biomarker test) is frozen in docs/CDED_ANS_001_PLAN.md and runs only after this report confirms: (1) Valsalva and tilt segments can be located in the lab records, (2) ECG and continuous BP exist at both visits, (3) at least ~35 participants have both visits plus a baseline 24-h ECG.
