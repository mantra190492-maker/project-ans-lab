"""WATCH-SYNC-007: WESAD wrist/chest delayed event alignment, with held-out testing.

Scientific constraints:
- Different devices may have clock offsets beyond pulse transit delay. Returned
  offset is an EMPIRICAL alignment shift, NOT physiological pulse transit time.
- Lag is selected using only seconds 10-30, confirmed on seconds 30-50,
  then evaluated on seconds 70-170. No evaluation-time lag tuning.
- Only same-person real ECG/BVP signals. Automated dual-detector ECG consensus,
  NOT manually adjudicated truth or validated medical diagnostics.
- Participant-level waveforms, beat times and identifiers are never reported.
- Original WESAD scientific/non-commercial use with attribution.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly

from wearable.experiments.wesad_real_003 import (
    ECG_FS, BVP_FS, OFFICIAL_URL, STATE_NAMES, _filter_signal, find_ecg_beats,
    get_sync_arrays, match_peaks, remote_sources, select_condition_window,
)
from wearable.experiments.wesad_repair_005 import (
    neurokit_ecg, neurokit_ppg,
)

OUT=Path("wearable/reports/WATCH_SYNC_007.json")
LAG_CANDIDATES=np.arange(-10.0, 10.001, .02)
LAG_TOL=.15
ECG_CONSENSUS_GATE=.98
PPG_AUTOCORR_GATE=.40
QUALITY_EPOCH_SEC=20


def within(x, lo, hi):
    a=np.asarray(x,dtype=float)
    return a[(a>=lo)&(a<hi)]


def _nearest_match_metrics(ecg,ppg,lag,tol=LAG_TOL):
    """Fraction and mean timing discrepancy of matches, calibration only."""
    if len(ecg)==0 or len(ppg)==0:return (0.,float("inf"))
    idx=np.searchsorted(ppg,ecg+lag)
    d1=np.where(idx<len(ppg),np.abs(ppg[np.minimum(idx,len(ppg)-1)]-(ecg+lag)),np.inf)
    d0=np.where(idx>0,np.abs(ppg[np.maximum(idx-1,0)]-(ecg+lag)),np.inf)
    d=np.minimum(d0,d1)
    matched=d<=tol
    if not np.any(matched):return (0.,float("inf"))
    return float(np.mean(matched)),float(np.mean(d[matched]))


def _nearest_match_fraction(ecg,ppg,lag,tol=LAG_TOL):
    return _nearest_match_metrics(ecg,ppg,lag,tol)[0]


def find_clock_shift(ecg_peaks, ppg_peaks, grid=LAG_CANDIDATES):
    """Train at 10-30s; confirm 30-50s, no test-time labels or pulses.

    To support +/-10s offsets without leakage, use only PPG observed
    in [0,60) for all calibration lag candidates.
    """
    e_train=within(ecg_peaks,10,30)
    e_check=within(ecg_peaks,30,50)
    p_train=within(ppg_peaks,0,60)
    if min(len(e_train),len(e_check))<10 or len(p_train)<30:
        raise ValueError("Too few calibration events")
    metrics=[_nearest_match_metrics(e_train,p_train,float(v)) for v in grid]
    sc=np.array([m[0] for m in metrics])
    timing_error=np.array([m[1] for m in metrics])
    # Prefer more matches, then LOWER timing residual among matched beats.
    # Exact match-count ties are common for periodic heart rhythms; without
    # this gate, an entire-beat alias can falsely "win" calibration.
    # Physical clock offset remains unknown even if algorithm selects a lag.
    rank=np.lexsort((np.abs(grid),timing_error,-sc))
    best=int(rank[0])
    lag=float(grid[best])
    train=float(sc[best])
    confirmation=_nearest_match_fraction(e_check,p_train,lag)
    # Other peaks separated by at least 450ms reveal regular-rhythm aliases.
    competitors=sc[np.abs(grid-lag)>=.45]
    other=float(np.max(competitors)) if len(competitors) else 0.0
    ambiguity=other>=train-.06
    return {
        "lag_seconds":lag,
        "train_fraction":train,
        "confirmation_fraction":confirmation,
        "ambiguous_offset":bool(ambiguity),
        "train_pass":bool(train>=.70),
        "confirmation_pass":bool(confirmation>=.60),
        "lag_in_nominal_pulse_transit_window":bool(.05<=lag<=.55),
    }


def ppg_epoch_quality(ppg, pulses, fs=BVP_FS):
    """Signal-only 20s pulse morphology check, without ECG or labels.

    Max normalized lagged autocorrelation at 0.4-1.5s; empirical threshold
    .40 originally motivated by Pettit et al. 2024, not clinically validated here.
    """
    x=np.asarray(ppg,dtype=float)
    if x.ndim!=1 or len(x)<fs*10 or not np.all(np.isfinite(x)):
        return {"passed":False,"autocorrelation_max":None,"plausible_fraction":0.}
    band=_filter_signal(x,fs,.6,5)
    xx=band-np.mean(band)
    if np.std(xx)<1e-8:return {"passed":False,"autocorrelation_max":0.,"plausible_fraction":0.}
    autocorr=[]
    for lag in range(round(.4*fs),round(1.5*fs)+1):
        left=xx[:-lag];right=xx[lag:]
        den=np.linalg.norm(left)*np.linalg.norm(right)
        autocorr.append(float(np.dot(left,right)/den) if den>0 else 0.)
    sqi=max(autocorr)
    ibi=np.diff(np.asarray(pulses,dtype=float))
    plausible=float(np.mean((ibi>=.32)&(ibi<=1.65))) if len(ibi) else 0.
    count=len(pulses)*60/(len(x)/fs)
    passed=(sqi>=PPG_AUTOCORR_GATE and plausible>=.80 and 35<=count<=180 and len(ibi)>=9)
    return {"passed":bool(passed),"autocorrelation_max":sqi,"plausible_fraction":plausible}


def evaluate_state(source, condition, signal_rate=64):
    ecg, bvp, labels=get_sync_arrays(source)
    t0=select_condition_window(labels,condition)
    i=int(round(t0*ECG_FS));j=int(round(t0*BVP_FS))
    e=ecg[i:i+180*ECG_FS]
    p64=bvp[j:j+180*BVP_FS]
    if len(e)!=180*ECG_FS or len(p64)!=180*BVP_FS:
        raise ValueError("Truncated matched window")
    ecg1=find_ecg_beats(e)
    ecg2=neurokit_ecg(e)
    if match_peaks(within(ecg1,70,170),within(ecg2,70,170),0,tol=.12)["f1"]<ECG_CONSENSUS_GATE:
        raise ValueError("ECG algorithm agreement failed QC gate")
    if signal_rate==25:
        p=resample_poly(p64,25,64)
        p64=resample_poly(p,64,25)
    # Keep analysis always 64Hz; see WATCH-REPAIR-006.
    ppg=neurokit_ppg(p64,BVP_FS)
    lag=find_clock_shift(ecg2,ppg)
    have_calibration=lag["train_pass"] and lag["confirmation_pass"]
    evaluations=[]
    for left in (70,90,110,130,150):
        right=left+QUALITY_EPOCH_SEC
        start=left+lag["lag_seconds"]
        stop=right+lag["lag_seconds"]
        sample_lo=int(round(start*BVP_FS));sample_hi=int(round(stop*BVP_FS))
        if sample_lo<0 or sample_hi>len(p64):raise ValueError("Lagged PPG epoch outside source")
        p_events=within(ppg,start,stop)
        waveform=p64[sample_lo:sample_hi]
        quality=ppg_epoch_quality(waveform,p_events-start)
        ecg_events=within(ecg2,left,right)
        # Compare only quality-qualified wrist sections, keeping denominator.
        if not have_calibration or not quality["passed"] or len(ecg_events)<10:
            evaluations.append({"eligible":False,"q":quality["autocorrelation_max"]})
            continue
        matched=match_peaks(ecg_events,p_events,lag["lag_seconds"],tol=LAG_TOL)
        # Counterfactual: shift the observed PPG by 7.3 sec, leaving same
        # pulse sequence and rate. Phase coincidence remains possible.
        null=match_peaks(ecg_events,p_events+7.3,lag["lag_seconds"],tol=LAG_TOL)
        evaluations.append({"eligible":True,"f1":matched["f1"],
                            "chance_shifted_f1":null["f1"],"q":quality["autocorrelation_max"]})
    good=[v for v in evaluations if v["eligible"]]
    return {
        "lag":lag,
        "quality_epochs_accepted":sum(v["eligible"] for v in evaluations),
        "quality_epochs_total":len(evaluations),
        "median_f1_on_accepted_epochs":float(np.median([v["f1"] for v in good])) if good else None,
        "median_shifted_negative_control_f1":float(np.median([v["chance_shifted_f1"] for v in good])) if good else None,
        "median_PPG_autocorr":float(np.median([v["q"] for v in evaluations if v["q"] is not None])),
        "source":"original same-person WESAD ECG and wrist BVP",
    }


def collect_one(src, signal_rate=64):
    result={}
    for code,state in STATE_NAMES.items():
        try:result[state]=evaluate_state(src,code,signal_rate=signal_rate)
        except (ValueError,IndexError,KeyError,ZeroDivisionError) as exc:
            result[state]={"withheld_reason":type(exc).__name__+": "+str(exc)[:120]}
    return result


def _stat(values):
    if not values:return None
    return {"median":float(np.median(values)),
            "min":float(min(values)), "max":float(max(values))}


def aggregate(rows,*,offset,rate):
    report={
        "experiment":"WATCH-SYNC-007",
        "dataset":"Original WESAD (RespiBAN ECG 700Hz and E4 wrist BVP 64Hz)",
        "participants_attempted":len(rows),
        "subset_offset_in_prescribed_order":offset,
        "PPG_source_rate_hz":rate,
        "timing_train_seconds":[10,30],
        "timing_confirmation_seconds":[30,50],
        "timing_test_seconds":[70,170],
        "lag_range_seconds":[-10,10],
        "physical_pulse_transit_time_estimated":False,
        "ecg_reference_manually_verified":False,
        "beat_F1_is_clinical_accuracy":False,
        "clinical_ANS_or_EDS_labels":0,
        "clinical_accuracy":None,
        "source_data_published":False,
        "results":{}
    }
    for state in STATE_NAMES.values():
        success=[r[state] for r in rows if "lag" in r[state]]
        rejected=[r[state].get("withheld_reason") for r in rows if "lag" not in r[state]]
        eligible=[x for x in success if x["quality_epochs_accepted"]>0]
        lags=[x["lag"] for x in success]
        report["results"][state]={
            "n_qc_processed":len(success),
            "n_wholly_withheld":len(rejected),
            "n_train_calibration_pass":sum(x["train_pass"] for x in lags),
            "n_confirmation_calibration_pass":sum(x["train_pass"] and x["confirmation_pass"] for x in lags),
            "n_ambiguous_lag":sum(x["ambiguous_offset"] for x in lags),
            "n_lag_in_nominal_pulse_transit_window":sum(x["lag_in_nominal_pulse_transit_window"] for x in lags),
            "epoch_coverage":sum(x["quality_epochs_accepted"] for x in success)/(5*len(success)) if success else 0.,
            "total_epoch_count":5*len(success),
            "eligible_epoch_count":sum(x["quality_epochs_accepted"] for x in success),
            "n_with_at_least_one_f1_epoch":len(eligible),
            "heldout_f1_per_subject_median":_stat([x["median_f1_on_accepted_epochs"] for x in eligible]),
            "shifted_control_f1_per_subject_median":_stat([x["median_shifted_negative_control_f1"] for x in eligible]),
            "best_lag_seconds_diagnostic":_stat([x["lag_seconds"] for x in lags]),
            "calibration_confirmation_fraction":_stat([x["confirmation_fraction"] for x in lags]),
            "PPG_morphology_sqi":_stat([x["median_PPG_autocorr"] for x in success]),
            "aggregate_withheld_reasons":{z:rejected.count(z) for z in sorted(set(rejected))}
        }
    report["limitations"]=[
        "Clock offset search +/-10 seconds follows published WESAD alignment precedent; offsets are empirical, not physiological pulse transit.",
        "Beat F1 is between automatically identified PPG and ECG events; WESAD ECG events have not been human adjudicated here.",
        "First 20s train and second 20s confirmation avoid test lag optimization. Rhythm aliases can still produce spurious event matches.",
        "Negative shifted-control with regular rhythms can yield high F1 by chance; not a formal null distribution.",
        "PPG quality gating selects clean periods and must report coverage; cannot generalize F1 to excluded epochs.",
        "No clinical ANS deterioration/EDS labels; stress state is not an autonomic diagnosis.",
        "Lag and morphology thresholds fixed for this pilot; future tuning must use new participants and annotated pulse references.",
    ]
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive-url",default=OFFICIAL_URL)
    parser.add_argument("--limit",type=int,default=2)
    parser.add_argument("--offset",type=int,default=0)
    parser.add_argument("--signal-rate",type=int,choices=(25,64),default=64)
    parser.add_argument("--output",type=Path,default=OUT)
    args=parser.parse_args()
    if args.archive_url!=OFFICIAL_URL:parser.error("Use original official WESAD source")
    if not 0<=args.offset<15 or not 1<=args.limit<=15-args.offset:
        parser.error("Invalid subset")
    rows=[collect_one(source,args.signal_rate) for source in remote_sources(args.archive_url,args.limit,offset=args.offset)]
    if len(rows)!=args.limit:raise RuntimeError("Source failed to supply all requested recordings")
    result=aggregate(rows,offset=args.offset,rate=args.signal_rate)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
