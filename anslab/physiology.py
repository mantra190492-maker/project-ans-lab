"""Exploratory resting cardiovascular features; not a clinical device."""
import numpy as np

def rr_features(rr_seconds):
    """Time-domain HRV from cleaned normal-to-normal intervals in seconds."""
    rr=np.asarray(rr_seconds,dtype=float)
    if rr.ndim!=1 or len(rr)<30 or not np.all(np.isfinite(rr)):
        raise ValueError("Need >=30 finite normal-to-normal intervals")
    if np.any((rr<0.3)|(rr>2.0)):
        raise ValueError("Intervals outside prespecified 0.3–2.0 s limits")
    return {"n_intervals":int(len(rr)),
            "mean_hr_bpm":float(60/rr.mean()),
            "sdnn_ms":float(np.std(rr,ddof=1)*1000),
            "rmssd_ms":float(np.sqrt(np.mean(np.diff(rr)**2))*1000)}

def sequence_brs(systolic_bp_mmHg, rr_seconds, min_sequences=3):
    """Exploratory sequence-method cardiac BRS (ms/mmHg).
    Uses paired SBP and *next-beat* RR; assumes correctly synchronized inputs.
    Does not measure sympathetic nerve activity.
    """
    sbp=np.asarray(systolic_bp_mmHg,dtype=float)
    rr=np.asarray(rr_seconds,dtype=float)
    if sbp.ndim!=1 or rr.ndim!=1 or len(sbp)!=len(rr) or len(rr)<12:
        raise ValueError("Equal-length beat-aligned arrays with >=12 beats required")
    if not np.all(np.isfinite(sbp)) or not np.all(np.isfinite(rr)):
        raise ValueError("Finite measurements required")
    if np.any((sbp<60)|(sbp>250)) or np.any((rr<0.3)|(rr>2.0)):
        raise ValueError("Measurements outside broad physiological plausibility limits")
    # Each three-beat segment requires same-direction SBP and subsequent RR changes.
    slopes=[]
    for i in range(len(rr)-3):
        x=sbp[i:i+3]
        y=rr[i+1:i+4]*1000
        dx=np.diff(x)
        dy=np.diff(y)
        if not (np.all(dx>=1) and np.all(dy>=5) or np.all(dx<=-1) and np.all(dy<=-5)):
            continue
        slope=float(np.polyfit(x,y,1)[0])
        if np.isfinite(slope) and slope>0 and abs(np.corrcoef(x,y)[0,1])>=0.85:
            slopes.append(slope)
    if len(slopes)<min_sequences:
        return {"brs_ms_per_mmHg":None,"n_sequences":len(slopes),"quality":"insufficient_sequences"}
    return {"brs_ms_per_mmHg":float(np.mean(slopes)),"n_sequences":len(slopes),"quality":"exploratory_only"}

def compare_age_association(age, baseline_hrv, extra_brs):
    """No fitting until real cohort and subject-level splits are available."""
    raise NotImplementedError("Requires verified participant metadata, cohort splits, and leakage audit")
