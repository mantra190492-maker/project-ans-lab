"""WATCH-DIAG-004: independent established ECG/PPG detectors on original WESAD.

Diagnostics, not clinical/biomarker results. Only pooled state summaries leave runner.
NeuroKit2 detectors are software comparators, not manually adjudicated truth.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import neurokit2 as nk
import numpy as np
from scipy.signal import find_peaks

from wearable.experiments.wesad_real_003 import (
    BVP_FS, ECG_FS, OFFICIAL_URL, STATE_NAMES, _filter_signal, find_ecg_beats,
    find_pulse_beats, get_sync_arrays, match_peaks, remote_sources,
    select_condition_window,
)

OUT=Path("wearable/reports/WATCH_DIAG_004.json")


def nk_ecg_beats(signal):
    clean=nk.ecg_clean(signal,sampling_rate=ECG_FS,method="neurokit")
    _,info=nk.ecg_peaks(clean,sampling_rate=ECG_FS,method="neurokit",correct_artifacts=False)
    return np.asarray(info["ECG_R_Peaks"],dtype=float)/ECG_FS


def nk_ppg_beats(signal):
    clean=nk.ppg_clean(signal,sampling_rate=BVP_FS,method="elgendi")
    _,info=nk.ppg_peaks(clean,sampling_rate=BVP_FS,method="elgendi",correct_artifacts=False)
    return np.asarray(info["PPG_Peaks"],dtype=float)/BVP_FS


def count_rate(beats):
    p=np.asarray(beats)
    return len(p[(p>=60)&(p<177)])*60/117


def report_one(source,condition):
    ecg,bvp,labels=get_sync_arrays(source)
    t0=select_condition_window(labels,condition)
    e=ecg[int(round(t0*ECG_FS)):int(round(t0*ECG_FS))+180*ECG_FS]
    p=bvp[int(round(t0*BVP_FS)):int(round(t0*BVP_FS))+180*BVP_FS]
    if len(e)!=180*ECG_FS or len(p)!=180*BVP_FS:raise ValueError("Truncated")
    orig_e=find_ecg_beats(e)
    new_e=nk_ecg_beats(e)
    orig_p=find_pulse_beats(p,BVP_FS)
    new_p=nk_ppg_beats(p)
    f=_filter_signal(p,BVP_FS,.6,5)
    troughs,_=find_peaks(-f,distance=round(BVP_FS*.38),
                         prominence=max(.35*np.std(f),.05*np.ptp(f)))
    troughs=troughs/BVP_FS
    # Agreement uses same chest signal but different algorithms, not truth.
    o=orig_e[(orig_e>=60)&(orig_e<177)]
    n=new_e[(new_e>=60)&(new_e<177)]
    agreement=match_peaks(o,n,0,tol=.12)
    output={
      "ecg_old_bpm":count_rate(orig_e),
      "ecg_neurokit_bpm":count_rate(new_e),
      "ecg_detector_f1":agreement["f1"],
      "wrist_old_positive_bpm":count_rate(orig_p),
      "wrist_neurokit_bpm":count_rate(new_p),
      "wrist_negative_peak_bpm":count_rate(troughs),
      "neurokit_vs_ecg_abs_bpm":abs(count_rate(new_p)-count_rate(new_e)),
      "old_wrist_vs_neurokit_ecg_abs_bpm":abs(count_rate(orig_p)-count_rate(new_e)),
      "old_ecg_vs_neurokit_abs_bpm":abs(count_rate(orig_e)-count_rate(new_e)),
    }
    # Do NOT optimize lag from evaluation interval. Only 3..59s.
    for name,xx,yy in (("old",orig_e,orig_p),("neurokit",new_e,new_p)):
        calib_x=xx[(xx>=3)&(xx<59)]
        calib_y=yy[(yy>=3)&(yy<60)]
        if len(calib_x)<20 or len(calib_y)<20:
            output[name+"_calibration_max_match_fraction"]=0.0
            output[name+"_calibration_best_lag_seconds"]=None
            continue
        offsets=np.arange(-.20,1.201,.02)
        quality=[]
        for lag in offsets:
            scored=match_peaks(calib_x,calib_y,float(lag),tol=.08)
            quality.append(scored["matched"]/max(1,len(calib_x)))
        best=int(np.argmax(quality))
        output[name+"_calibration_max_match_fraction"]=float(quality[best])
        output[name+"_calibration_best_lag_seconds"]=float(offsets[best])
    return output


def aggregate(rows):
    out={"experiment":"WATCH-DIAG-004",
         "dataset":"original WESAD synchronized pickles",
         "algorithms":"Legacy ECG/PPG vs NeuroKit2 ECG/Elgendi PPG; no human adjudication",
         "subjects_attempted":len(rows),
         "source_verified_original_archive":True,
         "clinical_diagnosis_accuracy":None,
         "per_person_waveforms_or_features_published":False,
         "states":{}}
    for st in STATE_NAMES.values():
        valid=[x[st] for x in rows if x[st].get("ecg_old_bpm") is not None]
        failures=[x[st].get("failure","unknown") for x in rows if x[st].get("ecg_old_bpm") is None]
        fields=[
          "ecg_old_bpm","ecg_neurokit_bpm","ecg_detector_f1",
          "wrist_old_positive_bpm","wrist_neurokit_bpm","wrist_negative_peak_bpm",
          "neurokit_vs_ecg_abs_bpm","old_wrist_vs_neurokit_ecg_abs_bpm",
          "old_ecg_vs_neurokit_abs_bpm",
          "old_calibration_max_match_fraction","neurokit_calibration_max_match_fraction",
          "old_calibration_best_lag_seconds","neurokit_calibration_best_lag_seconds"]
        results={key:(
          {"median":float(np.median(arr)), "min":float(min(arr)), "max":float(max(arr))}
          if (arr:=[r.get(key) for r in valid if r.get(key) is not None]) else None)
          for key in fields}
        out["states"][st]={"n_valid":len(valid),"n_withheld":len(failures),
                          "withheld_failure_types":{v:failures.count(v) for v in sorted(set(failures))},
                          "metrics":results}
    out["limits"]=[
      "No independently manually annotated WESAD beats, so algorithmic consensus is not ground truth.",
      "Only small two-subject pilot; do not optimize parameters on held-out test windows.",
      "Pulse delay positive and negative are diagnostics, not calibrated final values.",
      "Only aggregate metrics; no clinical ANS or EDS labels."]
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive-url",default=OFFICIAL_URL)
    parser.add_argument("--limit",type=int,default=2)
    args=parser.parse_args()
    if args.archive_url!=OFFICIAL_URL:parser.error("Diagnostics restricted to original source")
    if args.limit<1 or args.limit>15:parser.error("Limit must be 1..15")
    rows=[]
    for x in remote_sources(args.archive_url,args.limit):
        subject={}
        for code,state in STATE_NAMES.items():
            try:subject[state]=report_one(x,code)
            except Exception as exc:subject[state]={"failure":type(exc).__name__}
        rows.append(subject)
    report=aggregate(rows)
    OUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
