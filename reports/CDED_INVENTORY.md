# CDED-ANS-001 stage 1 — dataset structure (no outcome analysis)

Generated UTC: 2026-11-15T16:53:04.538938+00:00  
Source: https://physionet.org/files/cded/1.0.1/ (CC BY 4.0, DOI 10.13026/00bm-0x81)

- Files: 347; WFDB records: 157 ({'labview_visit2': 69, 'labview_visit8': 41, 'ecg_24h': 47})
- Participants with any record: 78
- **Both lab visits (baseline + 2 years): 41**
- 24-h ECG + baseline lab: 38; 24-h ECG + both lab visits: 23
- Non-WFDB/annotation-like extensions: none
- Header read failures: 1

## Record types

### labview_visit2 (n=69)

- Sampling rates: {'500.0': 69}; multi-segment headers: 0
- Duration (min): {'min': 31.1, 'median': 34.5, 'max': 99.6}
- Channels: marker (69), ecg (69), abp (69), mcar (69), mcal (69), Radi (69), thermst (69), flow_rate (69), o2 (69), co2 (69)

### labview_visit8 (n=41)

- Sampling rates: {'500.0': 41}; multi-segment headers: 0
- Duration (min): {'min': 28.5, 'median': 81.6, 'max': 94.3}
- Channels: marker (41), ecg (41), abp (41), mcar (41), mcal (41), Radi (41), thermst (41), flow_rate (41), o2 (41), co2 (41)

### ecg_24h (n=46)

- Sampling rates: {'1000.0': 46}; multi-segment headers: 0
- Duration (min): {'min': 6.1, 'median': 6.3, 'max': 42.3}
- Channels: emg_0 (46), emg_1 (46), emg_2 (25), emg_3 (25), emg_4 (25), emg_5 (25), emg_6 (25), emg_7 (25), ecg_0 (21), ecg_1 (21), sensor_0 (21), sensor_1 (21), accelerometer_0 (21), accelerometer_1 (21)

## Summary-table variables matching autonomic/diabetes keywords

- 24Hour-Daytime-DBP
- 24Hour-Daytime-HR
- 24Hour-Daytime-SBP
- 24Hour-Nightime-HR
- 24Hour-Nighttime-DBP
- 24Hour-Nighttime-SBP
- BETA BLOCKERS
- Diabetes Duration
- Diabetic Medication Taken
- Diabetic Retinopathy (more advanced eye)
- Dizziness AUTONOMIC SYMPTOMS
- Hb A1C%
- Left Eye Diabetic Retinopathy
- Numbness AUTONOMIC SYMPTOMS
- OH AUTONOMIC SYMPTOMS
- Painful feet AUTONOMIC SYMPTOMS
- Right Eye Diabetic Retinopathy
- Syncope AUTONOMIC SYMPTOMS

## Stage 2 gate

Stage 2 (the biomarker test) is frozen in docs/CDED_ANS_001_PLAN.md and runs only after this report confirms: (1) Valsalva and tilt segments can be located in the lab records, (2) ECG and continuous BP exist at both visits, (3) at least ~35 participants have both visits plus a baseline 24-h ECG.
