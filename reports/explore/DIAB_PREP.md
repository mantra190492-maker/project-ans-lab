# DIAB-PIP-001 preparation — structure only (no ECG, no blood pressure)

## CDED: 69 lab records

- table `Data_Description/GE-79_Summary_Table-Cognitive-Testing.csv`: 121 rows, 66 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': None, 'sex': None, 'group': None}
- table `Data_Description/GE-79_Summary_Table-Demographics-MRI-Part1.csv`: 121 rows, 254 columns; id/age/sex/group columns found: {'id': 'Patient ID', 'age': None, 'sex': None, 'group': 'Group'}
- table `Data_Description/GE-79_Summary_Table-Labs-BP-Ophthalmogic-Walk.csv`: 121 rows, 170 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': None, 'sex': None, 'group': None}
- table `Data_Description/GE-79_Summary_Table-MRI-Part2.csv`: 121 rows, 256 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': None, 'sex': None, 'group': None}
- table `Data_Description/GE-79_Summary_Table-MRI-Part3.csv`: 121 rows, 256 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': None, 'sex': None, 'group': None}
- table `Data_Description/GE-79_Summary_Table-MRI-Part4.csv`: 121 rows, 151 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': None, 'sex': None, 'group': None}
- table `Data_Description/GE-79_Summary_Table-MRI-Part5-History.csv`: 121 rows, 174 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': None, 'sex': None, 'group': None}
- people with a lab record and a table row: 67; group labels: {'control': 29, 'dm': 38}; sex labels: {'(blank)': 67}; with age: 0

Documentation rows from `Data_Description/GE-79_Files_and_Channels.csv` mentioning the protocol:

```
Visit 1/Day 2 | Data/labview | Labview | Head up tilt | Vasoreactivity, Valsalva maneuver,  Head up tilt
Valsalva manuever
5 min supine baseline | S####DA.dat | Labview | 10 | 500 Hz | Visit 2
3 min hyperventilation | S####DA.hea | Baseline values of Day 1 and Day 2 Procedures.
3 min CO2 rebreathing | 1 | Marker | Visit 8
5 min supine rest | 2 | ECG | 24-months Follow-up values of Day 1 and Day 2 Procedures.
Head up tilt 10 min | 3 | ABP | *100
Visit 1/Day 1 | Not uploaded | portapres-new | Portapress resting continuous beat-to-beat BP for 1.5/2 hours in supine or sitting position
Continuus beat-to-beat BP monitoring in reclining sitting or supine position for 1.5 - 2 hours while subject is resting using beatscope program.
Day 2 | data/labview | Labview | Vasoreactivity, Valsalva maneuver,  Head up tilt
Valsalva manuever
5 min supine baseline | S####DB.dat | Labview | 10 | 500 Hz | V
3 min hyperventilation | S####DB.hea
3 min CO2 rebreathing | 1 | marker | baseline | Valsalva maneuver | hyperventilation | Co2 rebreathing | head-up tilt | baseline
5 min supine rest | 2 | ECG | ECG
Head up tilt 10 min | 3 | ABP | finger blood pressure waveform | mmHg | *100 | Finapress | 100 HZ
1 | marker | sitting 5min | standing eyes open 3min | sitting | standing eyes closed
1 | marker
Not uploaded | anatomial and perfusion MRI | output | MRI- anatomical, CBF regional perfusiona dn paerfusion in vascular territories;  CO2 vasoreactivity to hyperventilation and C02 rebreathing
SxxxSB.xl0 | ascii | 11 channels | baseline, Valsalva menuever, head up tilt
```

## GE75: 52 lab records

- table `data_description/GE-75_data_summary_table.csv`: 88 rows, 1111 columns; id/age/sex/group columns found: {'id': 'patient ID', 'age': 'age', 'sex': 'Gender', 'group': 'Group'}
- people with a lab record and a table row: 52; group labels: {'dm': 46, 'control': 6}; sex labels: {'(blank)': 52}; with age: 52

Documentation rows from `data_description/GE-75_files_and_channels.csv` mentioning the protocol:

```
Visit 2 | Data/labview | Labview | Head up tilt | Vasoreactivity, Valsalva maneuver,  Head up tilt
Valsalva manuever
5 min supine baseline | S#####DB.dat | Labview | 10 | 500
3 min hyperventilation
3 min CO2 rebreathing | 1 | Marker
5 min supine rest | 2 | ECG
Head up tilt 10 min | 3 | ABP
1 | Marker
Day 2 | Not uploaded | 3TMRI | Anatomial and perfusion MRI | MRI- anatomical, CBF regional perfusiona dn paerfusion in vascular territories;  CO2 vasoreactivity to hyperventilation and C02 rebreathing
```

## Participant-ID overlap (same number in two datasets; age and sex compared to judge whether it is the same person)

- CDED_vs_GE75: {'shared_ids': 11, 'comparable': 0, 'same_sex_and_age_within_3y': 0}
- CDED_vs_GE71: {'shared_ids': 4, 'comparable': 0, 'same_sex_and_age_within_3y': 0}
- GE75_vs_GE71: {'shared_ids': 0, 'comparable': 0, 'same_sex_and_age_within_3y': 0}

## CO2-only search: earliest 240-s quiet-breathing window starting 30–660 s

- CDED: {'window_found': 69}; window start (s) 10/25/50/75/90th percentile: [30.0, 30.0, 30.0, 30.0, 30.0]
- GE75: {'window_found': 52}; window start (s) 10/25/50/75/90th percentile: [30.0, 30.0, 30.0, 30.0, 30.0]
