"""ANS-001 ECG detector benchmark against human-reviewed Fantasia beat annotations.

This tests ECG R-peak timing only, not BRS, ageing, clinical outcomes or longevity.
No parameter tuning against benchmark records is performed.
"""
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import requests
import wfdb

from anslab.physio_qc import detect_ecg_rpeaks

BASE = "https://physionet.org/files/fantasia/1.0.0/"
RECORDS = ("f1y01", "f1o01", "f2y01", "f2o01")
START_SECONDS = 60
DURATION_SECONDS = 300
MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024
OUT = Path("reports")
BEAT_SYMBOLS = set("NLRBAaJSVreEj/FfQ")
TOLERANCE_SECONDS = 0.15

def download(url, destination):
    with requests.get(url, stream=True, timeout=90,
                      headers={"User-Agent":"ProjectANS-Lab/0.3"}) as resp:
        resp.raise_for_status()
        size = 0
        with destination.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=512*1024):
                size += len(chunk)
                if size > MAX_DOWNLOAD_BYTES:
                    raise ValueError("Single-file download exceeded cap")
                f.write(chunk)

def match_peaks(predicted, reference, tolerance_samples, fs=250.0):
    """One-to-one nearest-match precision/recall; rejects duplicate matches."""
    predictions = np.sort(np.asarray(predicted, dtype=np.int64))
    truth = np.sort(np.asarray(reference, dtype=np.int64))
    i = j = correct = 0
    offsets = []
    while i < len(predictions) and j < len(truth):
        delta = int(predictions[i] - truth[j])
        if abs(delta) <= tolerance_samples:
            correct += 1
            offsets.append(delta)
            i += 1
            j += 1
        elif predictions[i] < truth[j] - tolerance_samples:
            i += 1
        else:
            j += 1
    false_pos = len(predictions) - correct
    false_neg = len(truth) - correct
    precision = correct / len(predictions) if len(predictions) else 0.0
    recall = correct / len(truth) if len(truth) else 0.0
    f1 = 2 * precision * recall / (precision+recall) if precision+recall else 0.0
    return {
        "truth_beats":int(len(truth)),
        "predicted_beats":int(len(predictions)),
        "true_positive":int(correct),
        "false_positive":int(false_pos),
        "false_negative":int(false_neg),
        "precision":round(precision,5),
        "recall":round(recall,5),
        "f1":round(f1,5),
        "median_abs_timing_error_ms":round(float(np.median(np.abs(offsets))) * 1000.0 / float(fs),2) if offsets else None
    }

def process(name, directory):
    root = directory / name
    for suffix in (".hea", ".dat", ".ecg"):
        download(BASE + name + suffix, directory / (name + suffix))
    header = wfdb.rdheader(str(root))
    fs = float(header.fs)
    start = int(START_SECONDS * fs)
    stop = int((START_SECONDS + DURATION_SECONDS) * fs)
    if header.sig_len < stop:
        raise ValueError("Record too short for standardized 5-minute window")
    waveform = wfdb.rdrecord(str(root), sampfrom=start, sampto=stop)
    channels = waveform.sig_name
    idx = next((i for i,x in enumerate(channels) if "ECG" in x.upper()), None)
    if idx is None:
        raise ValueError(f"No ECG channel in {channels}")
    ecg = np.asarray(waveform.p_signal[:,idx], dtype=float)
    primary, secondary, _ = detect_ecg_rpeaks(ecg, fs)
    annotated = wfdb.rdann(str(root), "ecg")
    reference = np.array(
        [int(n-start) for n,symbol in zip(annotated.sample,annotated.symbol)
         if start <= n < stop and symbol in BEAT_SYMBOLS],
        dtype=np.int64
    )
    if len(reference) < 100:
        raise ValueError(f"Too few human-reviewed beat annotations: {len(reference)}")
    metrics = match_peaks(primary, reference, int(round(fs*TOLERANCE_SECONDS)), fs=fs)
    return {
        "record":name,
        "status":"processed",
        "age_group":"young_21_34" if "y" in name else "older_68_85",
        "fs_hz":fs,
        "ecg_channel":channels[idx],
        "reference_annotation_extension":"ecg",
        "analysis_start_seconds":START_SECONDS,
        "analysis_duration_seconds":DURATION_SECONDS,
        "annotation_match_tolerance_ms":int(1000*TOLERANCE_SECONDS),
        "quality_gate":"pass" if metrics["f1"]>=0.95 else "needs_improvement",
        **metrics
    }

def main():
    OUT.mkdir(exist_ok=True)
    results=[]
    with tempfile.TemporaryDirectory() as tmp:
        for name in RECORDS:
            try:
                result=process(name,Path(tmp))
            except Exception as e:
                result={"record":name,"status":"failed",
                        "error_type":type(e).__name__,
                        "error":str(e)[:400]}
            results.append(result)
            print(f"{name}: {result['status']}; F1={result.get('f1','NA')}",flush=True)
    payload={
        "benchmark":"Fantasia manually reviewed ECG beat annotation validation",
        "dataset_url":"https://physionet.org/content/fantasia/1.0.0/",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "method":"existing Project ANS primary ECG detector; 150ms one-to-one annotation comparison",
        "records":results,
        "limitations":[
            "Four selected records only; not overall detector validation",
            "Annotation sample convention and R-peak fiducials may produce systematic offsets",
            "No baroreflex/blood pressure validation",
            "Results are not clinical validation and cannot establish an ageing biomarker",
            "No test-retest repeatability or prospective health outcomes"
        ]
    }
    (OUT/"fantasia_ecg_benchmark.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    lines=["# ANS-001 — Fantasia ECG human-annotation benchmark",
           "",f"Generated: {payload['generated_utc']}","",
           "Automatic R-peak detector compared against the dataset's **manually reviewed beat annotations**.",
           "No model parameters were optimized against these records.",
           "",
           "| Record | Age group | Reference beats | Predicted beats | Precision | Recall | F1 | Median abs timing error | QC |",
           "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in results:
        if r["status"]=="processed":
            lines.append(f"| {r['record']} | {r['age_group']} | {r['truth_beats']} | {r['predicted_beats']} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['median_abs_timing_error_ms']} ms | {r['quality_gate']} |")
        else:
            lines.append(f"| {r['record']} | NA | — | — | — | — | — | — | FAILED: {r['error_type']} |")
    lines += ["","**Engineering target (prospective):** F1 ≥ 0.95 in both age strata, no silent processing failures.",
              "F1 and timing agreement are not verification of beat-type classification, arrhythmia handling or BP/BRS alignment.",
              "This first four-record pilot is for software feasibility; expand to all Fantasia participants only after inspecting failures.",
              "","Dataset: https://physionet.org/content/fantasia/1.0.0/",
              "Cite: Iyengar et al. 1996 and PhysioNet Fantasia DOI 10.13026/C2RG61."]
    (OUT/"FANTASIA_ECG_BENCHMARK.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    if sum(r["status"]=="processed" for r in results)<2:
        raise SystemExit("Benchmark failed: fewer than two human-annotated records processed")

if __name__ == "__main__":
    main()
