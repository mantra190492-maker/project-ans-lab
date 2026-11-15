"""WATCH-REPAIR-006: prespecified 25 Hz reconstruction test on 8 untouched WESAD subjects.

After anti-alias downsampling 64Hz BVP to 25Hz, compare detector at
(a) native 25Hz vs (b) interpolation back to 64Hz prior to the SAME
NeuroKit2 Elgendi algorithm. Interpolation cannot recover lost signal;
it may improve algorithm cadence sensitivity. All metrics are paired
on the same persons and time windows. Not a hardware emulation, not
ANS disease classification, and not independent manually verified ECG.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
from wearable.experiments.wesad_real_003 import (
    ECG_FS,BVP_FS,OFFICIAL_URL,STATE_NAMES,
    find_ecg_beats,get_sync_arrays,match_peaks,
    remote_sources,select_condition_window,
)
from wearable.experiments.wesad_repair_005 import (
    neurokit_ecg,neurokit_ppg,bpm,heldout,MIN_ECG_AGREEMENT_F1,
)

OUT=Path("wearable/reports/WATCH_REPAIR_006.json")


def evaluate(source,state):
    ecg,bvp,labels=get_sync_arrays(source)
    t0=select_condition_window(labels,state)
    chest=ecg[int(round(t0*ECG_FS)):int(round(t0*ECG_FS))+180*ECG_FS]
    wrist=bvp[int(round(t0*BVP_FS)):int(round(t0*BVP_FS))+180*BVP_FS]
    if len(chest)!=180*ECG_FS or len(wrist)!=180*BVP_FS:
        raise ValueError("Truncated paired recording")
    ecg_a=find_ecg_beats(chest)
    ecg_b=neurokit_ecg(chest)
    if match_peaks(heldout(ecg_a),heldout(ecg_b),0,tol=.12)["f1"]<MIN_ECG_AGREEMENT_F1:
        raise ValueError("Reference ECG consensus gate failed")
    hr=bpm(ecg_b)
    if not 40<=hr<=180:raise ValueError("Implausible reference rate")
    # Identical optical input signals in all branches.
    reduced=resample_poly(wrist,25,64)
    reconstructed=resample_poly(reduced,64,25)
    rate64=bpm(neurokit_ppg(wrist,64))
    rate25=bpm(neurokit_ppg(reduced,25))
    rate_interp=bpm(neurokit_ppg(reconstructed,64))
    return {
        "reference_ecg_bpm":hr,
        "abs_64hz_error_bpm":abs(rate64-hr),
        "abs_direct25_error_bpm":abs(rate25-hr),
        "abs_interpolated25_error_bpm":abs(rate_interp-hr),
        "interpolation_minus_direct_abs_error":abs(rate_interp-hr)-abs(rate25-hr)
    }


def summarize(rows):
    output={
        "experiment":"WATCH-REPAIR-006",
        "design":"Prespecified direct 25Hz vs 25Hz->64Hz interpolation detector cadence test",
        "dataset":"Original synchronized WESAD 700Hz chest ECG / 64Hz wrist BVP",
        "subject_offset":7,
        "additional_untouched_subjects_attempted":len(rows),
        "comparison":"NeuroKit2 ECG consensus 0.98 F1-gated; NeuroKit2 Elgendi PPG pulse counts",
        "clinical_ANS_or_EDS_labels":0,
        "manual_ECG_truth":False,
        "beat_alignment_accuracy":None,
        "clinical_accuracy":None,
        "subject_data_shared":False,
        "results":{}
    }
    for name in STATE_NAMES.values():
        valid=[r[name] for r in rows if "abs_64hz_error_bpm" in r[name]]
        excluded=[r[name].get("withheld_reason","unknown") for r in rows if "abs_64hz_error_bpm" not in r[name]]
        fields=["abs_64hz_error_bpm","abs_direct25_error_bpm",
                "abs_interpolated25_error_bpm","interpolation_minus_direct_abs_error"]
        output["results"][name]={
            "n_valid":len(valid),"n_withheld":len(excluded),
            "withheld_reason_counts":{v:excluded.count(v) for v in sorted(set(excluded))},
            "metrics":{k:{
                "median":float(np.median([r[k] for r in valid])),
                "min":float(min(r[k] for r in valid)),
                "max":float(max(r[k] for r in valid)),
                } if valid else None for k in fields},
            "n_interpolated_less_error_than_direct25":sum(r["interpolation_minus_direct_abs_error"]<0 for r in valid),
            "n_interpolated_more_error_than_direct25":sum(r["interpolation_minus_direct_abs_error"]>0 for r in valid),
            "n_equal":sum(r["interpolation_minus_direct_abs_error"]==0 for r in valid)
        }
    output["limits"]=[
        "Remaining eight of 15 WESAD participants after earlier 2-person development and 5-person repair pilots; no claim of clinical external validation.",
        "Signal interpolation cannot recover information absent at 25Hz; algorithm behavior only.",
        "No one-to-one pulse matching or independent human ECG labels; count differences are not heart-rate medical accuracy.",
        "No EDS or autonomic neuropathy labels, no early detection sensitivity."]
    return output


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive-url",default=OFFICIAL_URL)
    args=ap.parse_args()
    if args.archive_url!=OFFICIAL_URL:ap.error("Use original WESAD distribution")
    rows=[]
    for source in remote_sources(args.archive_url,8,offset=7):
        row={}
        for code,name in STATE_NAMES.items():
            try:row[name]=evaluate(source,code)
            except (ValueError,KeyError,IndexError,ZeroDivisionError) as exc:
                row[name]={"withheld_reason":str(exc)[:110]}
        rows.append(row)
    if len(rows)!=8:raise RuntimeError("Incomplete unseen WESAD subject data")
    report=summarize(rows)
    OUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
