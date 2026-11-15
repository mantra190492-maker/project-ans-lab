# Costa 2024 — Official reference HRF preflight

Generated UTC: 2026-11-15T15:26:11.770399+00:00
Source: https://physionet.org/content/heart-rate-fragmentation-code/1.0.0/
Source SHA256: `aec918325b8ca12074db99370e4429c6e6588016df350af39ca7d11d45e1c1a7`
Software and example inputs downloaded only onto the runner. Source GPL code was **not** added to this repository.

**Important:** PhysioNet's landing page contains internally inconsistent figures for its third case. The actual original AWK output is reproduced below rather than pretending one printed reference is definitive.

## Raw outputs from Costa's AWK

### timeseries_1PVC.txt

~~~text
PIP = 33/53 = 62.264;   PNNSS = 24/43*100 = 55.814;   PNNLS = 19/51*100 = 37.255
~~~

Input rows: 61, SHA256: `5c9684266fd2918d4ae5609807aca3a85346838f113eb382510cbbbcf14c4a52`

### timeseries_1PVC_1outlier.txt

~~~text
PIP = 31/50 = 62.000;   PNNSS = 21/40*100 = 52.500;   PNNLS = 19/47*100 = 40.426
~~~

Input rows: 61, SHA256: `6bcb646aefd7c6dabf4c58a5b6ff2e22a0f334b9e3f290ca3e53f07964eeb62e`

### timeseries_1PVC_2outliers.txt

~~~text
PIP = 30/46 = 65.217;   PNNSS = 21/36*100 = 58.333;   PNNLS = 15/43*100 = 34.884
~~~

Input rows: 62, SHA256: `dbd9b1d350ab11bd222e43715a3d51c7264f58fc478ff9f984a1cbb266f86c10`

## Gate

- Source program and checksums verified from PhysioNet at runtime.
- These results are the numeric oracle for implementing a new independently written Python adapter.
- **Not yet** evidence that our Python calculation reproduces this AWK program.
- Neither the source nor the three examples involve disease progression or SHHS longitudinal access.
