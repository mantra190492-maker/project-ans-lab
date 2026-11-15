"""Experimental wrist BVP pulse extraction for Project ANS.

The 25Hz path uses anti-aliased sample-rate conversion to 64Hz before the
same NeuroKit2 Elgendi pulse extractor used for native 64Hz signals.
This addresses sample-rate sensitivity observed in WATCH-REPAIR-006.
It does NOT recover information absent at 25Hz or validate smartwatch
hardware. No disease or autonomic dysfunction diagnoses are returned.

All individual event times remain within the caller's process. Do not
publish participant-level traces or event arrays in public experiment logs.
"""
from __future__ import annotations

import neurokit2 as nk
import numpy as np
from scipy.signal import resample_poly

SUPPORTED_SOURCE_RATES = (25,64)
ANALYSIS_RATE_HZ = 64


def extract_wrist_pulse_times(bvp, sample_rate_hz):
    """Return candidate pulse times in seconds on the original time axis.

    The PPG peak-finder is an experimental software estimator, not
    independently validated against annotated blood-volume pulses.
    """
    if sample_rate_hz not in SUPPORTED_SOURCE_RATES:
        raise ValueError("Only measured 25Hz or 64Hz wrist BVP accepted")
    x=np.asarray(bvp,dtype=float).squeeze()
    if x.ndim!=1 or x.size < int(sample_rate_hz*20):
        raise ValueError("Need at least 20s of 1D wrist BVP signal")
    if not np.isfinite(x).all() or float(np.ptp(x))<1e-7:
        raise ValueError("Wrist BVP contains invalid or flat data")
    if sample_rate_hz==25:
        x=resample_poly(x,ANALYSIS_RATE_HZ,25)
    clean=nk.ppg_clean(x,sampling_rate=ANALYSIS_RATE_HZ,method="elgendi")
    _,info=nk.ppg_peaks(clean,sampling_rate=ANALYSIS_RATE_HZ,
                        method="elgendi",correct_artifacts=False)
    peaks=np.asarray(info["PPG_Peaks"],dtype=float)
    if not len(peaks) or np.any(np.diff(peaks)<=0):
        raise ValueError("Cannot identify ordered PPG pulses")
    return peaks/ANALYSIS_RATE_HZ


def count_based_pulse_rate_bpm(bvp, sample_rate_hz, start_s=60., end_s=177.):
    """Engineering rate estimate, not individual ECG-beat accuracy."""
    if not np.isfinite(start_s) or not np.isfinite(end_s) or end_s<=start_s:
        raise ValueError("Require valid, increasing evaluation window")
    duration=len(np.asarray(bvp).squeeze())/float(sample_rate_hz)
    if not (0<=start_s<end_s<=duration):
        raise ValueError("Evaluation window outside measured signal")
    pulses=extract_wrist_pulse_times(bvp,sample_rate_hz)
    count=int(np.sum((pulses>=start_s)&(pulses<end_s)))
    if count<10:
        raise ValueError("Insufficient pulse observations")
    return float(count*60/(end_s-start_s))
