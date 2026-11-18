# GE-71 documentation and marker structure (no outcomes)

## Data_Description/GE-71_Data_Dictionary.csv — rows mentioning autonomic/protocol terms (52)

```
Group | CONTROL | DIABETES MELLITUS | group control, DM (Diabetes Mellitus) DMOH (Diabetes Mellitus Orthostatic Hypertension)
Neuropathy | no | yes | Neuropathy
Dizziness AUTONOMIC SYMPTOMS | no | yes | Dizziness AUTONOMIC SYMPTOMS
Numbness AUTONOMIC SYMPTOMS | no | yes | Numbness AUTONOMIC SYMPTOMS
Painful feet AUTONOMIC SYMPTOMS | no | yes | Painful feet AUTONOMIC SYMPTOMS
Syncope AUTONOMIC SYMPTOMS | no | yes | Syncope AUTONOMIC SYMPTOMS
VM | 1 | 3 | Valsalva Manuever | 2 | 1.37 | -24 | 29 | 140 | 140 | 130 | 140 | 80 | 85 | 80 | 80 | 82 | 86 | 138 | 140 | 71 | 77
RATIO VALSALVA | 1.72 | 1.21 | RATIO VALSALVA
DBP II  VALSALVA | -8 | -15 | DBP II  VALSALVA
DBP IV  VALSALVA | 15 | 8 | DBP IV  VALSALVA
Baseline SBP TILT TONOMETER | 118 | 120 | Baseline Tilt systolic blood pressure | mmHg
1 Min SBP TILT TONOMETER | 118 | 100 | 1 Min Tilt systolic blood pressure | mmHg
3 Min SBP TILT TONOMETER | 120 | 110 | 3 Min Tilt systolic blood pressure | mmHg
5 Min SBP TILT TONOMETER | 124 | 110 | 5 Min Tilt systolic blood pressure | mmHg
Baseline DBP TILT TONOMETER | 56 | 70 | Baseline Tilt diastolic blood pressure | mmHg
1 Min DBP TILT TONOMETER | 68 | 60 | 1 Min Tilt diastolic blood pressure | mmHg
3 Min DBP TILT TONOMETER | 72 | 60 | 3 Min Tilt diastolic blood pressure | mmHg
5 Min DBP TILT TONOMETER | 68 | 60 | 5 Min Tilt diastolic blood pressure | mmHg
Baseline HR TILT FINAPRES | 53 | 74 | Baseline Tilt Heart Rate - FINAPRES | bpm
Tilt Ave HR TILT FINAPRES | 74 | 86 | Tilt Ave Heart Rate - FINAPRES | bpm
Baseline SBP TILT FINAPRES | 120 | 129 | Baseline Tilt systolic blood pressure - FINAPRES | mmHg
Tilt Ave SBP TILT FINAPRES | 113 | 108 | Tilt Ave systolic blood pressure - FINAPRES | mmHg
Baseline DBP TILT FINAPRES | 87 | 72 | Baseline Tilt diastolic blood pressure - FINAPRES | mmHg
Tilt Ave DBP TILT FINAPRES | 82 | 70 | Tilt Ave diastolic blood pressure - FINAPRES | mmHg
MCAR Baseline Ave | 71.2 | 45.4 | Baseline Right Middle Cerebreal Arterial
MCAL Baseline Ave | 80.7 | 60.7 | Baseline Left Middle Cerebreal Arterial
MCAR HV-Ave | 52.6 | 34.5 | Hyperventilation Right Middle Cerebreal Arterial
MCAL HV-Ave | 58.5 | 53.4 | Hyperventilation Left Middle Cerebreal Arterial
MCAR RB-Ave | 69.9 | 43.8 | CO2 Rebreathing Right Middle Cerebreal Arterial
MCAL RB-Ave | 75.5 | 65 | CO2 Rebreathing Left Middle Cerebreal Arterial
HYPER | 26.9 | 18.8 | Hyperventilation
BASE 2 | 30.5 | 19.1 | Baseline 2
SD BASE 1 | 2.4 | 1.21 | SD Baseline 1
HYPER | 1.3 | 2.98 | Hyperventilation
BASE2 | 1.4 | 2.67 | Baseline 2
Baseline 1 DAVID - TOTAL | Baseline 1 DAVID - TOTAL
Hypervent DAVID - TOTAL | Hyperventilation DAVID - TOTAL
Baseline 2 DAVID - TOTAL | Baseline 2 DAVID - TOTAL
Baseline 1 MRI FLOW NORMALIZED TO BASELINE | 1 | 1 | Baseline 1 MRI FLOW NORMALIZED TO BASELINE
Hypovent MRI FLOW NORMALIZED TO BASELINE | 1.13 | 1.36 | Hypoventilation MRI FLOW NORMALIZED TO BASELINE
Hypervent MRI FLOW NORMALIZED TO BASELINE | 0.49 | 0.79 | Hyperventilation MRI FLOW NORMALIZED TO BASELINE
Baseline 2 MRI FLOW NORMALIZED TO BASELINE | 0.65 | 1.07 | Baseline 2 MRI FLOW NORMALIZED TO BASELINE
hypo-hyper | 0.65 | 0.58 | hypoventilation-hyperventilation
Hypoventilation TCD NORM TO BASELINE | 0.96 | 1.45 | Hypoventilation Transcranial Doppler NORM TO BASELINE
Hyperventilation TCD NORM TO BASELINE | 0.73 | 1.32 | Hyperventilation Transcranial Doppler NORM TO BASELINE
Hypo CO2-MRI-normalized to baseline 1 | 1.34 | 1.45 | Hypoventilation CO2-MRI-normalized to baseline 1
Hyperv CO2-MRI-normalized to baseline 1 | 0.76 | 0.67 | Hyperventilation CO2-MRI-normalized to baseline 1
Baseline 2 CO2-MRI-normalized to baseline 1 | 0.86 | 0.69 | Baseline 2 CO2-MRI-normalized to baseline 1
Hypo CO2 TCD normalized to baseline 1 | 1.11 | 1.07 | Hypoventilation CO2 Transcranial Doppler normalized to baseline 1
Hyperv CO2 TCD normalized to baseline 1 | 0.58 | 0.88 | Hyperventilation CO2 Transcranial Doppler normalized to baseline 1
MRI DIFF HYPO-HYPERV | 0.65 | 0.58 | MRI DIFF Hypoventilation-Hyperventilation
MRI-CO2 DIFF HYPO/HYPERV | 0.59 | 0.77 | MRI-CO2 DIFF Hypoventilation/Hyperventilation
```

## Data_Description/GE-71_File_and_channels.csv

```
Visit | Physionet Directory | Directory | Protocol | Filename | Format | Channels | Sampling rate | Label | description | units | Calibration | Equipment | Device output sampling rate | Experiment
Day 1 | Not Uploaded | Screening | ICF
PCP permission
Blood draw
Retinal imaging
Day 1 | Not Uploaded | TCD | TCD window
Day 1 | Data/Labview/ Head-upTilt_ Day1 | Head-up tilt test | Deep breathing at 0.1Hz
Valsalva maneuver
5-minutes head-up tilt test | S#####DA.dat | 1 | marker
2 | ECG | ECG
3 | ABP | finger blood pressure waveform | mmHg | *100 | Finapress | 100 HZ
4 | Mcar | right middle cerebral artery flow velocity waveform | cm/s | Multi | empty channels not recorded
5 | Mcal | left middle cerebral artery flow velocity waveform | cm/s | MultiDop X4, DWL Neuroscan Inc, Sterling, VA | 50 Hz | empty channels not recorded
6 | Radi | radial artery flow velocity waveform | c,/s | empty channels not recorded
7 | Thermst | respiration with nasal thermistor | relative | thermisor
8 | Flow rate | respiration flow rate | Capnomac Ultima
9 | O2 | end tidal O2 | mmHg | *9.09 | Capnomac Ultima
10 | CO2 | end tidal CO2 | mmHg | *7.74 | Capnomac Ultima
Day 1 | Not Uploaded | Portapress | Beat-to-beat BP | Portapress resting continuous beat-to-beat BP during  head-up tilt (day 1) recording
S####D_Portapress.dat
Note: This was recorded during Head-up tilt test. Not all the subjects had a recording.
Note: During recording the machine did not work proprerly, so files which are labeled as Beat1, Beat2, Beat 3 and Beat4. It means those files are from the same subject.
Day 1 | Data/Pedar | Pedar | 12 minute Walking test | Walk test 1&2 ( walk1 around 11 am and walk 2 in the afternoon, normal hallway walking for 12 min  recorded with EMG channels using ME6000) and foot pressure distribution using pedar mobile, some subjects a
Walking test- foot pressure distribution and walking characteristics  using Pedar Mobile
S####DA.ASC_Pedar | DAT
S####DA.ASC_Pedar | HEA
16
header: filename,  left insole #, right insole #, mean step left, mean step right, min and max step, total time (s econds), distance ( meters),velocity (m/s)
1 | step_no
2 | foot
3 | max. force[N]
4 | mean force[N]
5 | max pressure [N/cm²]
6 | start
7 | start in % of total time
8 | stride
9 | step
10 | stance
11 | stance in % of stride
12 | swing
13 | swing in %
14 | init double in %
15 | single limb support %
16 | terminate double %
Day 2 | Data/Labview/ Head-upTilt_ Day2 | Labview | Head up tilt | Vasoreactivity, Valsalva maneuver,  Head up tilt
TCD | with TCD
Valsalva manuever
5 min supine baseline | S####DB.dat | Labview | 10 | 500 Hz | V
3 min hyperventilation
3 min CO2 rebreathing | 1 | marker | baseline | Valsalva maneuver | hyperventilation | Co2 rebreathing | head-up tilt | baseline
5 min supine rest | 2 | ECG | ECG
Head up tilt 10 min | 3 | ABP | finger blood pressure waveform | mmHg | *100 | Finapress | 100 HZ
4 | Mcar | right middle cerebral artery flow velocity waveform | cm/s | Multi
5 | Mcal | left middle cerebral artery flow velocity waveform | cm/s | MultiDop X4, DWL Neuroscan Inc, Sterling, VA; | 50 Hz
6 | Radi | radial artery flow velocity waveform | c,/s
7 | Thermst | respiration with nasal thermistor | relative | thermisor
8 | Flow rate | respiration flow rate | Capnomac Ultima
9 | O2 | end tidal O2 | mmHg | *9.09 | Capnomac Ultima
10 | CO2 | end tidal CO2 | mmHg | *7.74 | Capnomac Ultima
Day 2 | Data/Labview/Sit-To-Stand | labview-sit-to-stand | Sit-to stand with eyes open and closed | Sit-to-stand Test
5 min sitting with eyes open on balance platform with simultaneous cardiovascular, TCD
5 min standing with eyes open on balance platform with simultaneous cardiovascular, TCD and balance measures
5 min sitting with eyes closed on balance platform with simultaneous cardiovascular, TCD
5 min standing with eyes closed on balance platform with simultaneous cardiovascular, TCD and balance measures
S####DC.dat | Labview | 15 | 1000 Hz | V
1 | marker | sitting 5min | standing eyes open 3min | sitting | standing eyes closed
2 | ECG | ECG
3 | ABP | finger blood pressure waveform | mmHg | *100 | Finapress
4 | Mcar | right middle cerebral artery flow velocity waveform | cm/s | Multi
5 | Mcal | left middle cerebral artery flow velocity waveform | cm/s | MultiDop X4, DWL Neuroscan Inc, Sterling, VA;
6 | Radi | radial artery flow velocity waveform | cm/s
7 | Thermst | respiration with nasal thermistor | relative | thermisor
8 | Flow rate | respiration flow rate | ml/s | Capnomac Ultima
9 | O2 | end tidal O2 | mmHg | *9.09 | Capnomac Ultima
10 | CO2 | end tidal CO2 | mmHg | *7.74 | Capnomac Ultima
11 | fx | sway trajectory in mediolateral direction | mm | Kistler Force plate, Amherst MA
12 | fy | sway trajectory in anteroposterior direction | mm
13 | fz | sway trajectory in vertical  direction | mm
14 | px | center of pressure x component | mm
15 | py | center of pressure x component | mm
S#####DC.ch1-10.dat | Labview | 10 | 1000 Hz
1 | marker
2 | ECG | ECG
3 | ABP | finger blood pressure waveform | mmHg | *100 | Finapress
4 | Mcar | right middle cerebral artery flow velocity waveform | cm/s | Multi
5 | Mcal | left middle cerebral artery flow velocity waveform | cm/s | MultiDop X4, DWL Neuroscan Inc, Sterling, VA;
6 | Radi | radial artery flow velocity waveform | cm/s
7 | Thermst | respiration with nasal thermistor | relative | thermisor
8 | Flow rate | respiration flow rate | ml/s | Capnomac Ultima
9 | O2 | end tidal O2 | mmHg | *9.09 | Capnomac Ultima
10 | CO2 | end tidal CO2 | mmHg | *7.74 | Capnomac Ultima
Day 3 | Not uploaded | 3T MRI | Anatomical MRI | MRI- anatomical, CBF regional perfusiona dn paerfusion in vascular territories;  CO2 vasoreactivity to hyperventilation and C02 rebreathing
Perfusion MRI | 3Tesla  GE Signa Vhi or Excite scanner and phase arrays head coil ( GE Medical Systmes, Milwaukee, WI)
MP-RAGE | MP-RAGE) (repetition | ml or % of total brain volume
time [TR]/echo time [TE]/inversion time [TI]  7.8/3.1/600
msec, 3.0 mm slice thickness, 52 slices, bandwidth  122 Hz
per pixel, flip angle  10�, 24 cm  24 cm field of view [FOV],
256  192 matrix size)
FLAIR | fluid-attenuated inversion recovery
(FLAIR) (TR/TE/TI  11,000/161/2,250 msec, 5 mm slice
thickness, 30 slices, bandwidth  122 Hz per pixel, flip angle 
90�, 24 cm  24 cm FOV, 256  160 matrix size),
DWI | diffusion-weighted image (b value of 1,000 seconds/
mm2, TR/TE  10,000/86.6 msec, 5 mm slice thickness, bandwidth
 250 kHz, 128  128 matrix size
CASL | CBF | three-dimensional stack of | mL � 100 g1 � min1
interleaved spirals fast spin echo sequence (TR/TE  6,000/
23.8 msec, echo train length  66, with a 18  18 cm FOV, in
the coronal plane and 64 slices with thickness  3.8 mm, eight
see Zhao et al. Neurology 2009 ;72:643-649 for procecessing details | spiral interleaves, two averages and a bandwidth62.5 kHz).
```

## Data_Description/GE-71_Head-up-tilt-Day1_Markers_per_subject.csv (87 rows)

Header rows:
```
Subject ID | Group | Start 1 min | Deep breathing | End  | Val 1 | End  | Val 2  | End  | Val 3 | End  | Tilt  | End  | Notes
S0030 | Control | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 
```

| column index | numeric values | min | median | max |
|---:|---:|---:|---:|---:|
| 0 | 0 | None | None | None |
| 1 | 0 | None | None | None |
| 2 | 86 | 0.0 | 1.0 | 1.0 |
| 3 | 86 | 0.0 | 2.0 | 2.0 |
| 4 | 86 | 0.0 | 3.0 | 4.0 |
| 5 | 85 | 0.0 | 4.0 | 5.0 |
| 6 | 86 | 0.0 | 5.0 | 6.0 |
| 7 | 86 | 0.0 | 6.0 | 7.0 |
| 8 | 86 | 0.0 | 7.0 | 8.0 |
| 9 | 86 | 0.0 | 0.0 | 8.0 |
| 10 | 86 | 0.0 | 0.0 | 9.0 |
| 11 | 86 | 0.0 | 8.0 | 12.0 |
| 12 | 86 | 0.0 | 9.0 | 13.0 |
| 13 | 0 | None | None | None |

## Data_Description/GE-71_Head-up-tilt-Day2_Markers_per_subject.csv (87 rows)

Header rows:
```
Subject ID | Group | Start 10 min | Val 1 | End | Val 2 | End | Val 3 | End | Val 4 | End | Hyper | End | Hypo | End | Tilt | End | Hypo | Tilt | End tilt | Notes
S0030 | Control | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 
```

| column index | numeric values | min | median | max |
|---:|---:|---:|---:|---:|
| 0 | 0 | None | None | None |
| 1 | 0 | None | None | None |
| 2 | 86 | 0.0 | 0.0 | 1.0 |
| 3 | 86 | 0.0 | 0.0 | 2.0 |
| 4 | 86 | 0.0 | 0.0 | 3.0 |
| 5 | 86 | 0.0 | 0.0 | 7.0 |
| 6 | 86 | 0.0 | 0.0 | 8.0 |
| 7 | 86 | 0.0 | 0.0 | 6.0 |
| 8 | 86 | 0.0 | 0.0 | 7.0 |
| 9 | 86 | 0.0 | 0.0 | 8.0 |
| 10 | 86 | 0.0 | 0.0 | 9.0 |
| 11 | 86 | 0.0 | 0.0 | 10.0 |
| 12 | 86 | 0.0 | 0.0 | 11.0 |
| 13 | 86 | 0.0 | 0.0 | 12.0 |
| 14 | 86 | 0.0 | 0.0 | 13.0 |
| 15 | 86 | 0.0 | 0.0 | 14.0 |
| 16 | 86 | 0.0 | 0.0 | 15.0 |
| 17 | 86 | 0.0 | 0.0 | 16.0 |
| 18 | 86 | 0.0 | 0.0 | 17.0 |
| 19 | 86 | 0.0 | 0.0 | 18.0 |
| 20 | 0 | None | None | None |

Day-2 record names (first 5): ['s0030DB', 's0044DB', 's0058DB', 's0059DB', 's0063DB']
Day-1 record names (first 5): ['s0030DA', 's0044DA', 's0058DA', 's0059DA', 's0064DA']
