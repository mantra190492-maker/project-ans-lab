"""Small reproducible PhysioNet pilot: exploratory signal extraction, not clinical validation."""
import json
import tempfile
from pathlib import Path
import requests
import numpy as np
import wfdb
from scipy.signal import find_peaks, butter, sosfiltfilt
from anslab.physiology import rr_features

BASE="https://physionet.org/files/autonomic-aging-cardiovascular/1.0.0/"
RECORDS=("0001","0002","0003")
OUT=Path("reports/physionet_pilot.json")

def fetch_record(record, folder):
    for suffix in (".hea",".dat"):
        url=BASE+record+suffix
        response=requests.get(url,timeout=90)
        response.raise_for_status()
        (folder/(record+suffix)).write_bytes(response.content)
    return wfdb.rdrecord(str(folder/record))

def extract(record):
    fs=float(record.fs)
    names=[name.upper() for name in record.sig_name]
    ecg_indices=[i for i,n in enumerate(names) if "ECG" in n]
    bp_indices=[i for i,n in enumerate(names) if "BP" in n or "NIBP" in n]
    if not ecg_indices or not bp_indices:
        raise ValueError(f"Missing ECG/BP channels: {record.sig_name}")
    bp=np.asarray(record.p_signal[:,bp_indices[0]],dtype=float)
    if not np.all(np.isfinite(bp)):
        raise ValueError("Nonfinite BP signal")
    # Use ECG with largest robust QRS-scale derivative amplitude.
    ecgs=[np.asarray(record.p_signal[:,i],dtype=float) for i in ecg_indices]
    ecgs=[x for x in ecgs if np.all(np.isfinite(x))]
    if not ecgs:
        raise ValueError("No finite ECG")
    ecg=max(ecgs,key=lambda x:np.percentile(np.abs(np.diff(x[::10])),95))
    filtered=sosfiltfilt(butter(3,[5,22],btype="bandpass",fs=fs,output="sos"),ecg)
    energy=np.abs(filtered)
    threshold=max(float(np.percentile(energy,97))*0.48,float(np.median(energy))*3)
    r,_=find_peaks(energy,distance=int(.40*fs),prominence=threshold)
    if len(r)<35:
        raise ValueError(f"Too few ECG peaks: {len(r)}")
    rr=np.diff(r)/fs
    # This deliberately strict preliminary filter rejects ectopy/noisy intervals.
    keep=(rr>=.4)&(rr<=1.5)
    if keep.sum()<30:
        raise ValueError("Too few plausible intervals")
    hrv=rr_features(rr[keep])
    bp_smooth=sosfiltfilt(butter(2,8,btype="lowpass",fs=fs,output="sos"),bp)
    systolic,_=find_peaks(bp_smooth,distance=int(.4*fs),prominence=8)
    # Associate BP systolic peaks with ECG R-peaks at physiologically plausible delay.
    aligned=[]
    for j,beat in enumerate(r[:-1]):
        possible=systolic[(systolic>=beat+int(.08*fs))&(systolic<=beat+int(.6*fs))]
        if len(possible)!=1:
            continue
        aligned.append((j,float(bp_smooth[possible[0]])))
    # Require contiguous matched beats to avoid treating dropped beats as sequences.
    sequences=[]
    for k in range(len(aligned)-2):
        triple=aligned[k:k+3]
        if triple[1][0]!=triple[0][0]+1 or triple[2][0]!=triple[1][0]+1:
            continue
        if triple[2][0]+2>=len(r):
            continue
        sequences.append(triple)
    # Evaluate each matched three-beat segment individually; do not stitch gaps.
    slopes=[]
    for triple in sequences:
        indices=[x[0] for x in triple]
        sbp=[x[1] for x in triple]
        subsequent_rr=[(r[i+2]-r[i+1])/fs for i in indices]
        if not all(.4<=x<=1.5 for x in subsequent_rr):
            continue
        x=np.array(sbp);y=np.array(subsequent_rr)*1000
        dx=np.diff(x);dy=np.diff(y)
        if (np.all(dx>=1)&np.all(dy>=5)) or (np.all(dx<=-1)&np.all(dy<=-5)):
            corr=np.corrcoef(x,y)[0,1] if np.std(x)>0 and np.std(y)>0 else 0
            if np.isfinite(corr) and corr>=.85:
                slope=float(np.polyfit(x,y,1)[0])
                if slope>0:slopes.append(slope)
    return {"duration_sec":round(len(ecg)/fs,1),"sampling_hz":fs,
            "channels":record.sig_name,"detected_ecg_peaks":len(r),
            "plausible_rr_fraction":round(float(keep.mean()),3),
            "hrv":hrv,"bp_matched_beats":len(aligned),
            "brs_ms_per_mmHg":round(float(np.mean(slopes)),3) if len(slopes)>=3 else None,
            "brs_sequences":len(slopes),
            "quality":"EXPLORATORY; ECG/BP alignment and peak-detection require manual audit"}

def main():
    results=[]
    with tempfile.TemporaryDirectory() as temp:
        for name in RECORDS:
            try:
                results.append({"record":name,"status":"processed",**extract(fetch_record(name,Path(temp)))})
            except Exception as exc:
                results.append({"record":name,"status":"failed","error":str(exc)})
    payload={"dataset":"PhysioNet Autonomic Aging v1.0.0","doi":"10.13026/2hsy-t491",
             "analysis":"exploratory signal-processing feasibility; NOT clinical validation",
             "records":results}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2))
    if not any(x["status"]=="processed" for x in results):
        raise SystemExit("All recordings failed processing")

if __name__=="__main__":
    main()
