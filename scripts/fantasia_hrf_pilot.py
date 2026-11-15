"""Four-record real annotated-NN heart-rate fragmentation feasibility (no outcomes).

Downloads Fantasia .hea and human-reviewed .ecg annotation files ONLY:
<100 KB across four records; no waveform .dat download required.
"""
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
import wfdb

from anslab.heart_rate_fragmentation import fragmentation_features

BASE = "https://physionet.org/files/fantasia/1.0.0/"
RECORDS = ("f1y01", "f1o01", "f2y01", "f2o01")
BEAT_SYMBOLS = set("NLRBAaJSVreEj/FfQ")
OUT = Path("reports")
START_S = 60
DURATION_S = 300

def annotation_intervals(samples, symbols, fs):
    """Derive NN interval candidates without collapsing anomalous annotated beats."""
    samples = np.asarray(samples, dtype=np.int64)
    if len(samples) != len(symbols):
        raise ValueError("Beat samples and types length mismatch")
    rr_ms = np.diff(samples) * (1000.0 / fs)
    allowed = np.asarray([s == "N" for s in symbols], dtype=bool)
    valid = allowed[:-1] & allowed[1:]
    return rr_ms, valid

def fetch(url, destination):
    r = requests.get(url, timeout=40, headers={"User-Agent":"ProjectANS-Lab/0.4"})
    r.raise_for_status()
    if len(r.content) > 100_000:
        raise ValueError("Expected small annotation/header, not waveform")
    destination.write_bytes(r.content)

def one_record(name, directory):
    for ext in (".hea",".ecg"):
        fetch(BASE + name + ext, directory / (name + ext))
    record=str(directory/name)
    header=wfdb.rdheader(record)
    fs=float(header.fs)
    annotations=wfdb.rdann(record,"ecg")
    lo, hi=int(START_S*fs),int((START_S + DURATION_S)*fs)
    pairs=[(int(sample),symbol) for sample,symbol in zip(annotations.sample,annotations.symbol)
           if lo <= sample < hi and symbol in BEAT_SYMBOLS]
    if len(pairs) < 240:
        raise ValueError(f"Too few annotated beats in five minutes: {len(pairs)}")
    times=[a for a,_ in pairs]
    labels=[s for _,s in pairs]
    rr, valid=annotation_intervals(times,labels,fs)
    n_eligible=int(valid.sum())
    plausibility=np.isfinite(rr) & (rr>=300) & (rr<=2000)
    clean=valid & plausibility
    diagnostics={
        "record":name,"age_band":"21-34" if "y" in name else "68-85",
        "sampling_hz":fs,"window_s":DURATION_S,
        "annotated_beats":len(pairs),
        "non_normal_beat_annotations":int(sum(x!="N" for x in labels)),
        "intervals_with_normal_beat_endpoints":n_eligible,
        "physiologically_plausible_intervals":int(plausibility.sum()),
        "intervals_passing_all_checks":int(clean.sum()),
        "preflight_clean_fraction":round(float(np.mean(clean)),4),
    }
    try:
        base=fragmentation_features(rr, validated_sinus=True, valid_mask=valid,
                                    quantization_ms=4.0,min_clean_intervals=200)
        sensitive=fragmentation_features(rr, validated_sinus=True, valid_mask=valid,
                                         quantization_ms=8.0,min_clean_intervals=200)
    except ValueError as error:
        return {**diagnostics,"status":"qc_excluded",
                "qc_exclusion_reason":str(error),
                "clinical_validation":"none; QC exclusion, no measurement reported"}
    return {
        **diagnostics,"status":"processed",
        "candidate_pip_4ms":round(base["pip_percent"],3),
        "candidate_pip_8ms":round(sensitive["pip_percent"],3),
        "candidate_w1_4ms":round(base["w1_percent"],3),
        "candidate_rmssd_ms":round(base["rmssd_ms"],3),
        "candidate_mean_hr_bpm":round(base["heart_rate_bpm"],3),
        "retained_interval_fraction":round(base["clean_fraction"],4),
        "clinical_validation":"none; four selected healthy records, no outcomes"
    }

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results=[]
    with tempfile.TemporaryDirectory() as folder:
        for name in RECORDS:
            try:
                result=one_record(name,Path(folder))
            except Exception as exc:
                result={"record":name,"status":"failed",
                        "error_type":type(exc).__name__,
                        "error":str(exc)[:250]}
            results.append(result)
            print(name,result["status"],result.get("candidate_pip_4ms"),flush=True)
    payload={
        "study":"ANS-001 Fantasia annotated beat HRF feasibility",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "source":BASE,"doi":"10.13026/C2RG61",
        "measurement":"PIP / W1 from human-reviewed beat annotations; 5-minute segment; 4 and 8 ms resolutions",
        "records":results,
        "constraints":"No prospective outcome, no clinical validity, not a new discovered biomarker"
    }
    (OUT/"fantasia_hrf_pilot.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    lines=["# ANS-001 — Real annotated heartbeat fragmentation feasibility","",
        "Dataset: [Fantasia v1.0.0](https://physionet.org/content/fantasia/1.0.0/), DOI 10.13026/C2RG61.",
        f"Generated UTC: {payload['generated_utc']}", "",
        "**Engineering-only results: these values do not predict disease, ageing rate, or longevity.**",
        "All subjects were screened healthy and recorded while resting and watching a film.",
        "Inputs are visually verified beat annotation files; no patient-level waveforms or identifiers were committed.",
        "", "| Record | Published age band | Annotated beats | QC eligible | PIP 4 ms | PIP 8 ms | W1 4 ms | RMSSD (ms) | Data status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in results:
        if r["status"]=="processed":
            lines.append(f"| {r['record']} | {r['age_band']} | {r['annotated_beats']} | {r['preflight_clean_fraction']:.1%} | {r['candidate_pip_4ms']:.2f}% | {r['candidate_pip_8ms']:.2f}% | {r['candidate_w1_4ms']:.2f}% | {r['candidate_rmssd_ms']:.2f} | Processed |")
        elif r["status"]=="qc_excluded":
            lines.append(f"| {r['record']} | {r['age_band']} | {r['annotated_beats']} | {r['preflight_clean_fraction']:.1%} | — | — | — | — | Withheld: {r['qc_exclusion_reason']} |")
        else:
            lines.append(f"| {r['record']} | n/a | — | — | — | — | — | — | Failure: {r['error_type']} |")
    lines += ["", "## Interpretive gates",
        "- Sampling-resolution sensitivity is reported because changing the ternary difference threshold changes PIP even with the same biology.",
        "- Beat types other than N are excluded without joining disconnected intervals across gaps.",
        "- Per-record preflight counts distinguish non-N beat annotations and implausible intervals. An excluded record is NOT reclassified as healthy by relaxing quality rules.",
        "- Fantasia labels are visually verified but this does not prove all sinus intervals are free of physiological complexity.",
        "- Four selected healthy participants cannot establish group difference, prognostic accuracy or a clinical cut-off.",
        "- This result **must not** be used to train an age score, infer disease or claim mortality prediction.",
        "- Actual next test: verified sinus Holters in MUSIC with clinical outcome and censoring controls.",
        "","Source PIP definition: [Costa et al., 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6129761/)."]
    (OUT/"FANTASIA_HRF_PILOT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    if sum(x["status"]=="processed" for x in results) < 2:
        raise SystemExit("Fewer than 2 annotated records could be processed")

if __name__=="__main__":
    main()
