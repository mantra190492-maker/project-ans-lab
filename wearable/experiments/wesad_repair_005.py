"""WATCH-REPAIR-005: improved same-person WESAD wrist/chest engineering test.

Retains WATCH-REAL-003 as the frozen legacy baseline. Uses independent
NeuroKit2 ECG/PPG algorithms, checks chest ECG agreement against legacy
before comparing wrist beat counts, and withholds beat-level F1 unless
ECG-to-pulse timing calibrated on DISJOINT first-minute data.

This is a research test, not a validated ECG/BVP device or ANS biomarker.
All source recordings are from the official WESAD archive under its
scientific/non-commercial research conditions; no individual waveforms
or subject-specific measurements leave the runner.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import neurokit2 as nk
import numpy as np
from scipy.signal import resample_poly

from wearable.experiments.wesad_real_003 import (
    ECG_FS, BVP_FS, OFFICIAL_URL, STATE_NAMES, RESEARCH_CITATION,
    calibrate_lag, find_ecg_beats, find_pulse_beats, get_sync_arrays,
    match_peaks, remote_sources, select_condition_window,
)

OUT=Path("wearable/reports/WATCH_REPAIR_005.json")
EVAL_START=60
EVAL_END=177
MIN_ECG_AGREEMENT_F1=.98


def neurokit_ecg(signal):
    clean=nk.ecg_clean(signal,sampling_rate=ECG_FS,method="neurokit")
    _,info=nk.ecg_peaks(clean,sampling_rate=ECG_FS,method="neurokit",
                        correct_artifacts=False)
    beats=np.asarray(info["ECG_R_Peaks"],dtype=float)/ECG_FS
    if len(beats)<45:raise ValueError("Too few independently detected ECG beats")
    return beats


def neurokit_ppg(signal,fs):
    clean=nk.ppg_clean(signal,sampling_rate=fs,method="elgendi")
    _,info=nk.ppg_peaks(clean,sampling_rate=fs,method="elgendi",
                        correct_artifacts=False)
    beats=np.asarray(info["PPG_Peaks"],dtype=float)/fs
    if len(beats)<45:raise ValueError("Too few independently detected wrist pulses")
    return beats


def heldout(x):
    x=np.asarray(x)
    return x[(x>=EVAL_START)&(x<EVAL_END)]


def bpm(beats):
    return len(heldout(beats)) * 60.0/(EVAL_END-EVAL_START)


def one_state(source,condition):
    ecg,bvp,labels=get_sync_arrays(source)
    t0=select_condition_window(labels,condition)
    e0=int(round(t0*ECG_FS))
    w0=int(round(t0*BVP_FS))
    chest=ecg[e0:e0+180*ECG_FS]
    wrist=bvp[w0:w0+180*BVP_FS]
    if len(chest)!=180*ECG_FS or len(wrist)!=180*BVP_FS:
        raise ValueError("Simultaneous 180-second window truncated")
    old_ecg=find_ecg_beats(chest)
    new_ecg=neurokit_ecg(chest)
    agreement=match_peaks(heldout(old_ecg),heldout(new_ecg),0,tol=.12)
    # Consent to no data points when the ECG "reference" fails QC; no
    # optimization using wrist signals can rescue a bad ECG comparator.
    if agreement["f1"] < MIN_ECG_AGREEMENT_F1:
        raise ValueError("Independent ECG detectors disagree (reference quality withheld)")
    old_wrist=find_pulse_beats(wrist,BVP_FS)
    new_wrist=neurokit_ppg(wrist,BVP_FS)
    wrist_25=resample_poly(wrist,25,64)
    new_wrist25=neurokit_ppg(wrist_25,25)
    ref_rate=bpm(new_ecg)
    if not 40<=ref_rate<=180:raise ValueError("ECG heart rate outside prespecified range")
    outputs={
        "ecg_algorithm_agreement_f1":agreement["f1"],
        "chest_neurokit_bpm":ref_rate,
        "legacy_wrist_abs_rate_error_bpm":abs(bpm(old_wrist)-ref_rate),
        "repaired_wrist_64_abs_rate_error_bpm":abs(bpm(new_wrist)-ref_rate),
        "repaired_wrist_25_abs_rate_error_bpm":abs(bpm(new_wrist25)-ref_rate),
        "legacy_wrist_bpm":bpm(old_wrist),
        "repaired_wrist_64_bpm":bpm(new_wrist),
        "repaired_wrist_25_bpm":bpm(new_wrist25),
        "pulse_timing_calibration":"withheld",
        "beat_f1_64":None,
        "beat_f1_25":None,
        "pulse_lag_from_first_minute_seconds":None,
    }
    try:
        lag=calibrate_lag(new_ecg,new_wrist)
        outputs["pulse_timing_calibration"]="passed"
        outputs["pulse_lag_from_first_minute_seconds"]=lag
        outputs["beat_f1_64"]=match_peaks(heldout(new_ecg),heldout(new_wrist),lag)["f1"]
        outputs["beat_f1_25"]=match_peaks(heldout(new_ecg),heldout(new_wrist25),lag)["f1"]
    except ValueError:
        # Keep held-out F1 null. Never retune lag using held-out seconds.
        pass
    return outputs


def run_subject(source):
    out={}
    for code,state in STATE_NAMES.items():
        try:out[state]=one_state(source,code)
        except (ValueError,KeyError,IndexError,ZeroDivisionError) as exc:
            out[state]={"withheld_reason":str(exc)[:110]}
    return out


def _summarize(values):
    return None if not values else {
        "median":float(np.median(values)),
        "min":float(min(values)),
        "max":float(max(values)),
    }


def aggregate(rows,verified_source=False):
    report={
        "experiment":"WATCH-REPAIR-005",
        "source":"Official original synchronized WESAD chest/wrist recordings",
        "citation":RESEARCH_CITATION,
        "participants_attempted":len(rows),
        "original_archive_verified":bool(verified_source),
        "ECG_reference":"NeuroKit2 algorithmic ECG with legacy detector agreement gate (not manual ground truth)",
        "wrist_pulse_methods":"Legacy simple peak finder versus NeuroKit2 Elgendi BVP pulse detector",
        "reference_precondition":"Cross-method ECG peak F1 >=0.98 at 120ms tolerance",
        "calibration":"first 60s; held-out evaluation seconds 60-177",
        "hardware":"Empatica E4 BVP at 64Hz; anti-aliased resampling to 25Hz is not Samsung hardware",
        "number_of_true_clinical_ANS_labels":0,
        "ANS_or_EDS_diagnostic_accuracy":None,
        "per_subject_data_shared":False,
        "results":{}
    }
    for st in STATE_NAMES.values():
        valid=[r[st] for r in rows if r[st].get("ecg_algorithm_agreement_f1") is not None]
        reasons=[r[st]["withheld_reason"] for r in rows if "withheld_reason" in r[st]]
        timing=[r for r in valid if r["pulse_timing_calibration"]=="passed"]
        keys=["ecg_algorithm_agreement_f1","legacy_wrist_abs_rate_error_bpm",
              "repaired_wrist_64_abs_rate_error_bpm","repaired_wrist_25_abs_rate_error_bpm",
              "beat_f1_64","beat_f1_25"]
        report["results"][st]={
            "n_valid_rate_pairs":len(valid),
            "n_withheld_rate_pairs":len(rows)-len(valid),
            "n_timing_calibration_pass":len(timing),
            "n_timing_calibration_withheld":len(valid)-len(timing),
            "failure_reasons_aggregated":{v:reasons.count(v) for v in sorted(set(reasons))},
            "stats":{k:_summarize([r[k] for r in valid if r[k] is not None]) for k in keys}
        }
    report["limitations"]=[
        "At most 15 WESAD subjects; source labels are protocol-defined affect, not ANS diagnoses.",
        "Two ECG algorithms using the SAME chest signal can agree but still share errors.",
        "No WESAD manually adjudicated R-wave truth and no ECG-to-wrist hardware clock accuracy assessment.",
        "Rate counts can agree without beat-for-beat agreement. Withhold beat-F1 when first-minute calibration fails.",
        "Not an EDS screening test, validated clinical wearable, or novel ANS biomarker.",
        "No one-to-one watch-hardware equivalence established by PPG downsampling.",
    ]
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive-url",default=OFFICIAL_URL)
    p.add_argument("--limit",type=int,default=5)
    p.add_argument("--output",type=Path,default=OUT)
    args=p.parse_args()
    if args.archive_url!=OFFICIAL_URL:p.error("Original WESAD source only")
    if not 1<=args.limit<=15:p.error("Limit must be between 1 and 15")
    rows=[run_subject(s) for s in remote_sources(args.archive_url,args.limit)]
    if len(rows)!=args.limit:raise RuntimeError("Original WESAD participant count incomplete")
    report=aggregate(rows,verified_source=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
