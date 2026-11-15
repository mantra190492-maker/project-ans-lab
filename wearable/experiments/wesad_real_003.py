"""WATCH-REAL-003: compare paired WESAD chest ECG and wrist BVP at 64 Hz vs 25 Hz.

WESAD original recordings only, scientific/non-commercial use.
Clinical ANS disease labels absent. No raw or per-person data are committed.

Usage from repo root:
  python -m wearable.experiments.wesad_real_003 --data-dir /path/to/WESAD
  python -m wearable.experiments.wesad_real_003 --archive-url https://uni-siegen.sciebo.de/s/HGdUkoNlW1Ub0Gx/download --limit 2

WARNING: Pickle deserialization can execute code. Only process trusted originals in
an isolated research environment. NOT a Samsung smartwatch device emulator.
"""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
from scipy.signal import butter, find_peaks, resample_poly, sosfiltfilt

ECG_FS = 700
BVP_FS = 64
STATE_NAMES = {1: "baseline", 2: "stress"}
SUBJECTS = ("S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S13", "S14", "S15", "S16", "S17")
OFFICIAL_URL = "https://uni-siegen.sciebo.de/s/HGdUkoNlW1Ub0Gx/download"
RESEARCH_CITATION = "Schmidt et al., Introducing WESAD, ICMI 2018, DOI 10.1145/3242969.3242985"
OUTPUT = Path("wearable/reports/WATCH_REAL_003.json")


def as_channel(x):
    x = np.asarray(x, dtype=np.float64).squeeze()
    if x.ndim != 1 or x.size < 100 or not np.isfinite(x).all():
        raise ValueError("Channel must be 1D, finite and long enough")
    return x


def get_sync_arrays(source):
    if not isinstance(source, dict) or "signal" not in source or "label" not in source:
        raise ValueError("Not a recognized WESAD synchronized subject")
    wrist = source["signal"]["wrist"]
    chest = source["signal"]["chest"]
    ecg = as_channel(chest["ECG"])
    bvp = as_channel(wrist["BVP"])
    labels = np.asarray(source["label"]).reshape(-1)
    if len(labels) != len(ecg):
        raise ValueError("ECG and label stream are not synchronized")
    if abs(len(ecg)/ECG_FS - len(bvp)/BVP_FS) > 2:
        raise ValueError("Chest/wrist durations disagree by >2 s")
    return ecg, bvp, labels


def select_condition_window(labels, condition, *, segment_seconds=180, skip_seconds=20):
    """Select a contiguous task window, never join disjoint epochs."""
    z = np.asarray(labels).reshape(-1) == condition
    boundary = np.flatnonzero(np.diff(z.astype(np.int8))) + 1
    starts, ends = np.r_[0, boundary], np.r_[boundary, len(z)]
    need = (segment_seconds + skip_seconds) * ECG_FS
    possible = [(int(e-s),int(s)) for s,e in zip(starts,ends) if z[s] and e-s >= need]
    if not possible:
        raise ValueError("No sufficiently long contiguous state window")
    _, start = max(possible)
    return (start + skip_seconds*ECG_FS)/ECG_FS


def _filter_signal(values, fs, low, high):
    x = as_channel(values)
    sos = butter(3, (low,high), btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos,x)


def find_ecg_beats(ecg, fs=ECG_FS):
    """Automated QRS picks. No manually validated ECG R-peaks in WESAD."""
    f = _filter_signal(ecg,fs,7,28)
    envelope = np.abs(f)
    if np.std(envelope)<1e-6: raise ValueError("Flat ECG")
    high=float(np.percentile(envelope,97))
    peaks,_=find_peaks(envelope, distance=round(fs*.38),
                       prominence=max(.30*high,.9*np.std(envelope)))
    if not 35<=len(peaks)/(len(ecg)/fs)*60<=180:
        raise ValueError("Implausible ECG detection rate")
    return np.asarray(peaks/fs,dtype=float)


def find_pulse_beats(bvp,fs):
    f=_filter_signal(bvp,fs,.6,5)
    if np.std(f)<1e-6:raise ValueError("Flat BVP")
    peaks,_=find_peaks(f,distance=round(fs*.38),
                       prominence=max(.35*np.std(f),.05*np.ptp(f)))
    if not 30<=len(peaks)/(len(bvp)/fs)*60<=190:
        raise ValueError("Implausible BVP detection rate")
    return np.asarray(peaks/fs,dtype=float)


def match_peaks(ref, observed, lag, tol=.13):
    """One-to-one matching after pulse transit delay calibrated separately."""
    ref=np.asarray(ref);obs=np.asarray(observed)
    used=set();matches=0
    for t in ref:
        target=t+lag
        j=int(np.searchsorted(obs,target))
        candidates=[k for k in (j-1,j) if 0<=k<len(obs) and k not in used
                    and abs(obs[k]-target)<=tol]
        if candidates:
            pick=min(candidates,key=lambda k:abs(obs[k]-target))
            used.add(pick);matches+=1
    precision=matches/len(obs) if len(obs) else 0.0
    recall=matches/len(ref) if len(ref) else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"matched":matches,"ref_beats":len(ref),"pulse_beats":len(obs),
            "precision":precision,"recall":recall,"f1":f1}


def calibrate_lag(ref,pulses,*,calibration_seconds=60):
    """Select pulse-to-ECG delay exclusively on a calibration segment."""
    ecg=np.asarray(ref);ppg=np.asarray(pulses)
    ecg=ecg[(ecg>=3)&(ecg<calibration_seconds-1)]
    ppg=ppg[(ppg>=3)&(ppg<calibration_seconds)]
    if len(ecg)<35 or len(ppg)<35:raise ValueError("Insufficient calibration beats")
    lags=np.arange(.05,.551,.01)
    def score(l):
        distances=np.array([np.min(np.abs(ppg-(t+l))) for t in ecg])
        matched=distances<.09
        return (int(matched.sum()),-float(np.median(distances[matched])) if matched.any() else -float("inf"))
    scores=[score(float(l)) for l in lags]
    best=max(range(len(scores)),key=lambda i:scores[i])
    if scores[best][0]/len(ecg)<.60:raise ValueError("Calibration pulses do not align with ECG")
    return float(lags[best])


def one_state(ecg,bvp,labels,condition):
    t0=select_condition_window(labels,condition)
    seconds=180
    a=int(round(t0*ECG_FS));b=int(round(t0*BVP_FS))
    c=ecg[a:a+seconds*ECG_FS];w=bvp[b:b+seconds*BVP_FS]
    if len(c)!=seconds*ECG_FS or len(w)!=seconds*BVP_FS:
        raise ValueError("Truncated simultaneous data window")
    e=find_ecg_beats(c)
    native=find_pulse_beats(w,BVP_FS)
    watch=find_pulse_beats(resample_poly(w,25,64),25)
    lag=calibrate_lag(e,native)
    # 60s calibration. 117s held-out validation. Buffer before last 3s.
    ref=e[(e>=60)&(e<177)]
    b64=native[(native>=60)&(native<177)]
    b25=watch[(watch>=60)&(watch<177)]
    if len(ref)<50:raise ValueError("Insufficient validation reference beats")
    raw=match_peaks(ref,b64,lag)
    reduced=match_peaks(ref,b25,lag)
    return {"ecg_beat_f1_vs_manual":None,
            "raw_wrist_bvp_64hz":raw,"watch_rate_bvp_25hz":reduced,
            "f1_change_watch_minus_raw":reduced["f1"]-raw["f1"],
            "estimated_pulse_delay_seconds_calibrated":lag,
            "time_alignment":"Source sample-index synchronization, not independently established clock truth",
            "state_label":STATE_NAMES[condition],
            "data_type":"WESAD synchronized wrist/chest; automated reference ECG"}


def process_subject(source):
    ecg,bvp,labels=get_sync_arrays(source)
    out={}
    for condition,name in STATE_NAMES.items():
        try:out[name]=one_state(ecg,bvp,labels,condition)
        except (ValueError,KeyError,IndexError) as exc:
            out[name]={"status":"withheld","reason":type(exc).__name__+": "+str(exc)[:150]}
    return out


def _load_trusted_pickle(fp):
    return pickle.load(fp,encoding="latin1")


def local_sources(root,limit):
    root=Path(root)
    for sid in SUBJECTS[:limit]:
        file=root/sid/(sid+".pkl")
        if file.is_file():
            with file.open("rb") as f:yield _load_trusted_pickle(f)


def remote_sources(url,limit):
    """Retrieve individual members with HTTP ranges, not a full 2.5GB download."""
    from remotezip import RemoteZip
    with RemoteZip(url) as rz:
        files=rz.namelist()
        for sid in SUBJECTS[:limit]:
            match=[name for name in files if name.endswith("/"+sid+"/"+sid+".pkl")
                   or name==sid+"/"+sid+".pkl"]
            if not match:raise ValueError("Official archive missing expected subject member")
            info=rz.getinfo(match[0])
            if info.file_size>1_500_000_000 or info.compress_size>250_000_000:
                raise ValueError("Refusing large subject member (>1.5GB raw or >250MB transferred)")
            with rz.open(match[0]) as f:yield _load_trusted_pickle(f)


def aggregate(subject_outputs,*,verified_source=False):
    report={"experiment":"WATCH-REAL-003",
            "dataset":"WESAD original synchronized chest/wrist",
            "source_citation":RESEARCH_CITATION,
            "subjects_attempted":len(subject_outputs),
            "official_subject_labels":"stress task, NOT ANS disorder",
            "device":"Empatica E4 wrist; 25Hz downsample a watch-rate proxy, NOT Samsung hardware",
            "ecg_reference":"Automated RespiBAN chest ECG; no manual beat annotations",
            "clinical_diagnosis":"none","early_ANS_detection_accuracy":None,
            "per_subject_data_committed":False,"results":{}}
    for state in STATE_NAMES.values():
        eligible=[s[state] for s in subject_outputs if s[state].get("data_type")]
        def stat(name):
            values=[v[name]["f1"] for v in eligible]
            return {"median":float(np.median(values)),"min":float(min(values)),
                    "max":float(max(values))} if values else None
        delta=[v["f1_change_watch_minus_raw"] for v in eligible]
        failure_reasons={}
        for subject in subject_outputs:
            failure = subject[state] if subject[state].get("status") == "withheld" else None
            if failure is not None:
                reason = failure.get("reason","unspecified")
                # Aggregate categorical counts only; no participant IDs.
                failure_reasons[reason] = failure_reasons.get(reason,0)+1
        report["results"][state]={
            "n_valid_subjects":len(eligible),
            "n_withheld":len(subject_outputs)-len(eligible),
            "withheld_reasons_aggregate":failure_reasons,
            "f1_bvp64":stat("raw_wrist_bvp_64hz"),
            "f1_bvp25":stat("watch_rate_bvp_25hz"),
            "median_25_minus_64_f1":float(np.median(delta)) if delta else None}
    report["source_verified_original_archive"]=bool(verified_source)
    report["status"]=(("real_recordings_processed" if any(v["n_valid_subjects"] for v in report["results"].values())
                      else "no_quality_eligible_real_recordings") if verified_source
                      else "unverified_source_not_claimed_as_real_data")
    report["limitations"]=[
        "ECG reference is automated not manually adjudicated; cannot certify true beat-finding accuracy.",
        "Pulse transit lag fitted only on first 60s; F1 computed on held-out seconds 60-177.",
        "One short window per state; no clinically useful confidence interval or population generalization.",
        "WESAD states are not ANS disease diagnoses and cannot show EDS or early ANS detection.",
        "25Hz downsampling is a sample-rate stress test, not a Samsung optical hardware emulation.",
        "No individual traces or individual participant outputs published."]
    return report


def main(argv=None):
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--data-dir",type=Path)
    g.add_argument("--archive-url",type=str)
    parser.add_argument("--limit",type=int,default=2)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args(argv)
    if not 1<=args.limit<=15:parser.error("limit must be 1..15")
    subjects=[]
    itr=local_sources(args.data_dir,args.limit) if args.data_dir else remote_sources(args.archive_url,args.limit)
    for item in itr:subjects.append(process_subject(item))
    if not subjects:raise RuntimeError("No authentic WESAD recordings loaded; cannot claim real-data result")
    report=aggregate(subjects,verified_source=(args.archive_url==OFFICIAL_URL))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    # Negative/quality-withheld real results also count as tested data, never
    # as validated positive detection. Do not force successes.


if __name__=="__main__":
    main()
