# CDED-ANS-001 stage 1b — protocol segment decoding (structure only)

Generated UTC: 2026-11-15T17:12:17.997189+00:00

Decoded 24 of 24 sampled lab records (12 per visit). Failures: 0.

## Dataset channel documentation (GE-79_Files_and_Channels.csv)

```
Visit | Physionet | Directory | Filename | Format | Channels | Sampling rate | Label | description | units | Calibration | Equipment | Calibration/Device output sampling rate | Experiment | Visit | Files |  |  |  |  | 
Screening | Not uploaded | Screening | Medical history |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | TCD window |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | Blood draw |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | MMSE |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | PCP permission |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Screening | Data/ECG | 24 hour ECG and EMG monitoring | ECG | ME6000 | ME6000 files (ECG and EMG files were recorded during the protocol walking test, and during the daily activity and sleeping) |  |  |  |  |  |  |  |  |
 |  |  | 12 min walk |  |  | ME6000 | 5 | 1000Hz |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | sleep |  | S####ECG.dat |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | S####ECG.hea |  | 1 |  | ECG 1 | CH1 V5/V6-L clavicle |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 2 |  | ECG 2 | CH2 V1/V2 L clavicle |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 3 |  | foot switch | right |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 4 |  | foot switch | left |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 |  | EMG | gastrocnemius right |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 |  | EMG | gastrocnemius left |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 |  | accelerometer |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 8 |  | empty |  |  |  |  |  |  |  |  |  |  | 
Visit 1/Day 1 | Not uploaded | Retinal Imaging | Retinal Imaging |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Visit 1/Day 1 | Not uploaded | Cognitive testing | Cognitive |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Visit 1/Day 2 | Data/labview | Labview | Head up tilt | Vasoreactivity, Valsalva maneuver,  Head up tilt |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | with TCD |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | Valsalva manuever |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | 5 min supine baseline |  | S####DA.dat | Labview | 10 | 500 Hz |  |  |  |  |  | Visit 2 |  |  |  |  |  | 
 |  |  | 3 min hyperventilation |  | S####DA.hea |  |  |  |  |  |  |  |  |  | Baseline values of Day 1 and Day 2 Procedures. |  |  |  |  | 
 |  |  | 3 min CO2 rebreathing |  |  |  | 1 |  | Marker |  |  |  |  | Visit 8 |  |  |  |  |  | 
 |  |  | 5 min supine rest |  |  |  | 2 |  | ECG |  |  |  |  |  | 24-months Follow-up values of Day 1 and Day 2 Procedures. |  |  |  |  | 
 |  |  | Head up tilt 10 min |  |  |  | 3 |  | ABP |  |  | *100 |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 4 |  | Mcar |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 |  | Mcal |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 |  | Radi |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 |  | Therm |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 8 |  | Flow |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 9 |  | O2 |  |  | *9.09 |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 10 |  | .CO2 |  |  | *7.74 |  |  |  |  |  |  |  | 
Visit 1/Day1 | Not uploaded | 24-hr-bp | 24 hour BP monitoring | text | 24 hour BP | 20 min day, 30 min night |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | Automated BP measurements every 20 min during daytime and at 30 min at night for 24 hours |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxA.R | raw file | 1 |  | date |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxA.V | validated file | 2 |  | time |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 3 |  | status |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxB.R | second recording | 4 |  | systolic blood pressure |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 |  | diastolic blood pressure |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 |  | mean blood pressure |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 |  | heart rate |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | header subject ID, date, start time, end time, systolic and diastolic data threshold |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
Visit 1/Day 1 | Not uploaded | portapres-new | Portapress resting continuous beat-to-beat BP for 1.5/2 hours in supine or sitting position |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  | portapres |  | Portapress |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  | beatscope-program |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 | Continuus beat-to-beat BP monitoring in reclining sitting or supine position for 1.5 - 2 hours while subject is resting using beatscope program. |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | Sxxxxsabeat1-x.dat | binary proprietary  format | 3 | 100Hz |  | files have anout 300-500 KB about 2 hours |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | Sxxxxsa1-x.dat |  | 1 |  | time ( seconds) |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | Sxxxxsb1-x.dat |  | 2 |  | Porta | finger blood pressure waveform | mmHg |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 3 |  | Height |  | mmHg |  |  |  |  |  |  |  |  | 
Day 1 | Not uploaded | Pedar | Walk test 1&2 ( walk1 around 11 am and walk 2 in the afternoon, normal hallway walking for 12 min  recorded with EMG channels using ME6000) and foot pressure distribution using pedar moile,
 |  |  | Walking test- foot pressure distribution and walking characteristics  using Pedar Mobile |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxS-1.asc | Pedar | 99 |  |  |  | N/cm2 | calibrated | Pedar Mobile X, Novel , Munich GE | 50 Hz |  |  |  |  |  | 
 |  |  |  |  | SxxxxA-1.asc | ascii | 1 | filename Xxxxx-1*.sol |  |  | s |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 2 | insole type |  |  | % |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 3 | date/time |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 4 | total time | (seconds) |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 | time per frame | (s econds : 0.02) |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 | pressure values in N/cm2 |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 | mask definition | ( e.g.M1) |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | channel 8-99 | sensor values |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxA-9rg | text |  | map of 9 regions |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | note filenames inconsistent but this is calibration file for each recording |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxS-1.gtc | text | 16 |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | SxxxxSA-1.gtc.xls | Excel | header: filename,  left insole #, right insole #, mean step left, mean step right, min and max step, total time (s econds), distance ( meters),velocity (m/s) |  |  |  |  |  |  |
 |  |  |  |  |  |  | 1 | step # |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 2 | foot ( 1,2) |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 3 | max force (N) |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 4 | mean force (N) |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 | max pressure [N/cm2] |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 | start |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 | start in % of total time |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 8 | stride |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 9 | step # |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 10 | stance |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 11 | stance in % of stride |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 12 | swing |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 13 | swing % init |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 14 | double in % |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 15 | single limb support |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 16 | terminate double support % |  |  |  |  |  |  |  |  |  |  |  | 
Day 2 | data/labview | Labview | Vasoreactivity, Valsalva maneuver,  Head up tilt |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 | with TCD | TCD |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | Valsalva manuever |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | 5 min supine baseline |  | S####DB.dat | Labview | 10 | 500 Hz |  |  | V |  |  |  |  |  |  |  |  | 
 |  |  | 3 min hyperventilation |  | S####DB.hea |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  | 3 min CO2 rebreathing |  |  |  | 1 |  | marker |  |  |  |  |  | baseline | Valsalva maneuver | hyperventilation | Co2 rebreathing | head-up tilt | baseline
 |  |  | 5 min supine rest |  |  |  | 2 |  | ECG | ECG |  |  |  |  |  |  |  |  |  | 
 |  |  | Head up tilt 10 min |  |  |  | 3 |  | ABP | finger blood pressure waveform | mmHg | *100 | Finapress | 100 HZ |  |  |  |  |  | 
 |  |  |  |  |  |  | 4 |  | Mcar | right middle cerebral artery flow velocity waveform | cm/s |  | Multi |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 |  | Mcal | left middle cerebral artery flow velocity waveform | cm/s |  | MultiDop X4, DWL Neuroscan Inc, Sterling, VA; | 50 Hz |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 |  | Radi | radial artery flow velocity waveform | c,/s |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 |  | Thermst | respiration with nasal thermistor | relative |  | thermisor |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 8 |  | Flow rate | respiration flow rate | ??? |  | Capnomac Ultima |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 9 |  | O2 | end tidal O2 | mmHg | *9.09 | Capnomac Ultima |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 10 |  | CO2 | end tidal CO2 | mmHg | *7.74 | Capnomac Ultima |  |  |  |  |  |  | 
Day 2 | data/labview | labview-sit-to-stand | Sit-to-stand Test |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 | 5 min sitting with eyes open on balance platform with simultaneous cardiovascular, TCD |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 | 5 min standing with eyes open on balance platform with simultaneous cardiovascular, TCD and balance measures |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 | 5 min sitting with eyes closed on balance platform with simultaneous cardiovascular, TCD |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 | 5 min standing with eyes closed on balance platform with simultaneous cardiovascular, TCD and balance measures |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  | S####DC.dat | Labview | 15 | 1000 Hz |  |  | V |  |  |  |  |  |  |  |  | 
 |  |  |  |  | S####DC.hea |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 1 |  | marker |  |  |  |  |  | sitting 5min | standing eyes open 3min | sitting | standing eyes closed |  | 
 |  |  |  |  |  |  | 2 |  | ECG | ECG |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 3 |  | ABP | finger blood pressure waveform | mmHg | *100 | Finapress |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 4 |  | Mcar | right middle cerebral artery flow velocity waveform | cm/s |  | Multi |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 5 |  | Mcal | left middle cerebral artery flow velocity waveform | cm/s |  | MultiDop X4, DWL Neuroscan Inc, Sterling, VA; |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 6 |  | Radi | radial artery flow velocity waveform | cm/s |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 7 |  | Thermst | respiration with nasal thermistor | relative |  | thermisor |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 8 |  | Flow rate | respiration flow rate | ml/s |  | Capnomac Ultima |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 9 |  | O2 | end tidal O2 | mmHg | *9.09 | Capnomac Ultima |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 10 |  | CO2 | end tidal CO2 | mmHg | *7.74 | Capnomac Ultima |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 11 |  | fx | sway trajectory in mediolateral direction | mm |  | Kistler Force plate, Amherst MA |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 12 |  | fy | sway trajectory in anteroposterior direction | mm |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 13 |  | fz | sway trajectory in vertical  direction | mm |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 14 |  | px | center of pressure x component | mm |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  | 15 |  | py | center of pressure x component | mm |  |  |  |  |  |  |  |  | 
```

## Marker values across records

- value -0.0: present in 24 records
- value 1.02: present in 7 records

## Most common marker sequences (values in time order)

- 12 records: [0.0]
- 2 records: [-0.0, -0.0, -0.0, -0.0, -0.0, 0.0, -0.0, 0.0, -0.0, 0.0, -0.0, -0.0, 0.0]
- 1 records: [-0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 1.02, 0.0, 1.02, 0.0, 1.02, -0.0, 0.0, -0.0]
- 1 records: [-0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0]
- 1 records: [0.0, -0.0, 0.0, 0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, 1.02, 0.0, -0.0]
- 1 records: [-0.0, 0.0, 1.02, 0.0, 1.02, 0.0, 1.02, 0.0, 0.0, 1.02, 0.0, 0.0, 1.02, -0.0, 1.02, 0.0]
- 1 records: [-0.0, -0.0, -0.0, -0.0, 1.02, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0]
- 1 records: [-0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
- 1 records: [-0.0, 1.02, -0.0, -0.0, 0.0, 0.0, -0.0, 0.0, 1.02, -0.0, -0.0, 0.0, 1.02, 0.0, 1.02, 0.0, 0.0, -0.0]
- 1 records: [0.0, 0.0, 0.0, -0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 1.02, -0.0]

## Example records

### ./Data/Labview/Converted/Labview-v2/s0033DB-v2 (34.8 min, flat channels: {'ecg': False, 'abp': False})
- -0.0 at 0.0 s for 3.2 s
- 0.0 at 3.4 s for 604.8 s
- 0.0 at 608.8 s for 36.0 s
- 0.0 at 645.1 s for 186.0 s
- 0.0 at 831.4 s for 9.2 s
- 0.0 at 840.9 s for 182.6 s
- 0.0 at 1023.8 s for 14.0 s
- -0.0 at 1038.1 s for 302.5 s
- 0.0 at 1340.9 s for 10.8 s
- 1.02 at 1351.7 s for 0.5 s
- 0.0 at 1352.2 s for 14.1 s
- 1.02 at 1366.3 s for 0.8 s
- 0.0 at 1367.1 s for 616.6 s
- 1.02 at 1983.7 s for 0.7 s
- -0.0 at 1984.5 s for 9.3 s
- 0.0 at 1994.3 s for 64.7 s
- -0.0 at 2059.5 s for 30.8 s

### ./Data/Labview/Converted/Labview-v2/s0068DB-v2 (32.8 min, flat channels: {'ecg': False, 'abp': False})
- -0.0 at 0.0 s for 1.2 s
- -0.0 at 1.6 s for 600.3 s
- -0.0 at 602.2 s for 7.2 s
- -0.0 at 609.7 s for 179.6 s
- -0.0 at 789.6 s for 6.1 s
- -0.0 at 796.0 s for 179.8 s
- -0.0 at 976.2 s for 3.4 s
- -0.0 at 979.9 s for 300.1 s
- -0.0 at 1280.3 s for 6.7 s
- -0.0 at 1287.2 s for 9.8 s
- -0.0 at 1297.2 s for 147.8 s
- -0.0 at 1445.0 s for 442.4 s
- -0.0 at 1887.8 s for 7.7 s
- -0.0 at 1895.8 s for 68.0 s
- -0.0 at 1964.0 s for 4.9 s

### ./Data/Labview/Converted/Labview-v2/s0078DB-v2 (34.6 min, flat channels: {'ecg': False, 'abp': False})
- 0.0 at 0.0 s for 2.0 s
- -0.0 at 2.3 s for 605.7 s
- 0.0 at 608.3 s for 7.0 s
- 0.0 at 615.7 s for 183.6 s
- -0.0 at 799.6 s for 15.7 s
- -0.0 at 815.7 s for 25.5 s
- 0.0 at 841.5 s for 183.3 s
- 0.0 at 1025.1 s for 19.1 s
- 0.0 at 1044.6 s for 304.4 s
- 0.0 at 1349.4 s for 11.7 s
- -0.0 at 1361.5 s for 23.8 s
- -0.0 at 1385.7 s for 603.7 s
- 1.02 at 1989.4 s for 0.6 s
- 0.0 at 1990.1 s for 18.3 s
- -0.0 at 2008.7 s for 67.9 s

### ./Data/Labview/Converted/Labview-v2/s0153DB-v2 (35.8 min, flat channels: {'ecg': False, 'abp': False})
- -0.0 at 0.0 s for 5.5 s
- 0.0 at 5.8 s for 608.4 s
- 1.02 at 614.3 s for 0.6 s
- 0.0 at 614.9 s for 54.1 s
- 1.02 at 669.0 s for 0.5 s
- 0.0 at 669.5 s for 184.1 s
- 1.02 at 853.7 s for 0.6 s
- 0.0 at 854.3 s for 46.7 s
- 0.0 at 901.5 s for 132.7 s
- 1.02 at 1034.2 s for 0.7 s
- 0.0 at 1034.9 s for 163.3 s
- 0.0 at 1198.6 s for 309.7 s
- 1.02 at 1508.6 s for 0.7 s
- -0.0 at 1509.3 s for 544.4 s
- 1.02 at 2053.7 s for 0.5 s
- 0.0 at 2054.2 s for 94.7 s

