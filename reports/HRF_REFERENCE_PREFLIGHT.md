# Costa 2024 — Official reference HRF preflight

Generated UTC: 2026-11-15T15:27:10.247935+00:00
Source: https://physionet.org/content/heart-rate-fragmentation-code/1.0.0/
Source SHA256: `aec918325b8ca12074db99370e4429c6e6588016df350af39ca7d11d45e1c1a7`
Software and example inputs were downloaded on the runner. The attributed author reference code below is retained for scientific audit under GPL-3.0; Project ANS Python code remains separate.

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

## Reference algorithm source (audit only)

The following author-owned code is © Madalena Costa, published under GPL-3.0;
provenance: https://physionet.org/content/heart-rate-fragmentation-code/1.0.0/
This appendix is for checking reference semantics; it is NOT a rewrite.

~~~awk
{
    ### Input file: two columns, time of the R peak in seconds and beat type
    ### Ex.: 0.000 1
    ###      0.808 1
    ###      1.618 1
    ###      2.458 1
 
    CONVFMT = "%.3lf";
    
    NN_min = .300;  # NN intervals <= 0.3 s will be excluded
    NN_max = 1.800; # NN intervals >= 1.8 s will be excluded
    SF = 250;    # ECG sampling frequency
    t = $1;      # Time of the R peak in seconds
    ann = $2     # Annotation: beat type (1: sinus; 2: PVC; 3: PAC)

    #### The time of each R peak is rounded (up or down) to the closest multiple of 1/SF.                                          
    #### Ex.: Let SF = 250 Hz (1/SF = 0.004 s). The time of each R peak should be multiples of 0.004 but sometimes it is not due to conversion/export problems.
    #### If, for example, the time of the R peak was 0.809, this value would be rounded down to 0.808.
    #### Users not interested in this "correction," should comment the next five lines.
    
    aux = int(sprintf(CONVFMT, t*SF));
    if (t - aux/SF > 0.5)
	t = (aux+1)/SF;
    if (t - aux/SF  <= 0.5 && t - aux/SF > 0)
	t = aux/SF;
   
    #### Calculation of NN and delta NN intervals after reading 4 data points
    NN = t - t_1;     # Current NN interval
    NN_1 = t_1 - t_2; # Previous NN interval
    NN_2 = t_2 - t_3; # NN interval preceeding the "previous NN interval"
    dNN_formatted = sprintf(CONVFMT, t - 2*t_1 + t_2);      # Current delta NN interval
    dNN = dNN_formatted + 0;
    dNN_1_formatted = sprintf(CONVFMT, t_1 - 2*t_2 + t_3);  # Previous delta NN interval
    dNN_1 = dNN_1_formatted + 0;
    
    #### Verification of whether the current beat and the 3 preceeding ones are "normal sinus" beats (ann == 1)                                        
    if (ann == 1  &&  ann_1 == 1  &&  ann_2 == 1  &&  ann_3 == 1)
	flag_1 = 0;
    else{
	flag_1 = 1;
	non_sinus = 1;
    }
    if (NR <= 4 && (ann < 1 || ann_1 < 1 || ann_2 < 1 || ann_3 < 1))
	non_sinus = 0;

    #### Verification of whether current NN interval and the 3 preceeding one are between NN_min (0.3 sec) and NN_max (1.8 sec)
    if (NN < NN_max  &&  NN > NN_min  &&  NN_1 < NN_max  &&  NN_1 > NN_min  &&  NN_2 < NN_max  &&  NN_2 > NN_min)
	flag_2 = 0;
    else{
	flag_2 = 1;
	outlier = 1; 
    }
    if (NR <= 4 && (NN == 0 || NN_1 == 0 || NN_2 == 0 || NN_3 == 0))
	outlier = 0;

    # Counter for the number of inflection points: IP 
    # Counter for the number of delta NN intervals: n_dNN
    # Counter for the number of delta NN intervals in short (long) accelerative and decelerative segments: short (long) 
    # Counter for the number of delta NN intervals between consecutive inflection points: cont

    #### Hard inflection point criterion: dNN_current * dNN_previous < 0. 
    if (NR > 3 && flag_1 == 0 && flag_2 == 0 && dNN * dNN_1 < 0){
	IP++;
	if (non_sinus != 1 && outlier != 1){
	    if (IP > 1)
		n_dNN += cont;   
	    if (cont <= 2 && IP > 1)
		short += cont;
	    if (cont > 2 && IP > 1)
		long += cont;
#	    print "Hard IP: time =", t_1, " \#  Beat =", NR-2, "  NN =", NN_1;
	    if (IP == 1)
		NN_total = 1;
	    else
		NN_total += cont;
#	    print ("NN_total =", NN_total); 
	}
	if(non_sinus == 1 || outlier == 1){
	    non_sinus = 0; 
	    outlier = 0;
	    NN_total += 1
#	    print "Hard IP: time =", t_1, "  \# Beat =", NR-2, "  NN =", NN_1;
#	    print "NN_total =", NN_total;
	}
	cont = 0;
    }

    #### Soft inflection point criterion: dNN * dNN_prev == 0 and dNN != dNN_prev
    if (NR > 3 && flag_1 == 0 && flag_2 == 0 && dNN * dNN_1 == 0  &&  dNN != dNN_1){
	IP++;
	if (non_sinus != 1 && outlier != 1){
	    if (IP > 1)
		n_dNN += cont;
	    if (dNN_1 != 0) 
		if (cont <= 2 && IP > 1)
		    short += cont;
	    if (cont > 2 && IP > 1)
		    long += cont;
#	    print "Soft IP: time =", t_1, "  \# Beat =", NR-2, "  NN =", NN_1;
	    if (IP == 1)
		NN_total = 1;
	    else
		NN_total += cont;
#	    print ("NN_total =", NN_total); 
	}
	if((non_sinus == 1 || outlier == 1)){
	    non_sinus = 0;
	    outlier = 0;
	    NN_total += 1;
#	    print "Soft IP: time =", t_1, "  \# Beat =", NR-2, "  NN =", NN_1;
#	    print "NN_total =", NN_total;
	}
	cont = 0;
    }
    
    if (NR > 1)
	cont++;
    
    ann_3 = ann_2;
    ann_2 = ann_1;
    ann_1 = ann;
    t_3 = t_2;
    t_2 = t_1;
    t_1 = t;
    N_acc_dec = short + long;

    if (n_dNN > 0)
	PIP = (sprintf(CONVFMT,IP/NN_total*100));
    if (N_acc_dec > 0)
	PNNSS = (sprintf(CONVFMT,short/N_acc_dec*100));
    if (n_dNN > 0)
	PNNLS = (sprintf(CONVFMT,long/n_dNN*100));
}
END{print "PIP =", IP"/"NN_total, "=", PIP";", "  PNNSS =", short"/"N_acc_dec"*100 =", PNNSS";", "  PNNLS =", long"/"n_dNN"*100 =", PNNLS}

~~~

## Gate

- Source program and checksums verified from PhysioNet at runtime.
- These results are the numeric oracle for implementing a new independently written Python adapter.
- **Not yet** evidence that our Python calculation reproduces this AWK program.
- Neither the source nor the three examples involve disease progression or SHHS longitudinal access.
