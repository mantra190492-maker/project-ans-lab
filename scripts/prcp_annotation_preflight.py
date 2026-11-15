"""PhysioNet PRCP annotation/ECG/BP event inventory only.

Research target: ascertain timing and annotation availability BEFORE implementing
a stand/tilt recovery biomarker. No waveform data, patient-level physiology,
autonomic dysfunction diagnosis, or medical claims are produced.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import requests
import wfdb

BASE="https://physionet.org/files/prcp/1.0.0/"
RECORDS=("12726","12734","12744","12754","12755",
         "12814","12815","12819","12821","13960")
EXTENSIONS=(".hea",".anI",".wqrs",".wabp")
OUT=Path("reports")
MAX_BYTES={".hea":5000,".anI":10000,".wqrs":175000,".wabp":175000}

def annotation_summary(ann):
    symbols=[str(s) for s in ann.symbol]
    notes=[str(x).strip() for x in ann.aux_note if x and str(x).strip()]
    return {
        "n_annotations":len(ann.sample),
        "symbol_counts":dict(sorted(Counter(symbols).items())),
        "aux_labels_counts":dict(sorted(Counter(notes).items())),
        "first_event_sample":int(ann.sample[0]) if len(ann.sample) else None,
        "last_event_sample":int(ann.sample[-1]) if len(ann.sample) else None,
    }

def fetch_file(ext,name,folder):
    response=requests.get(BASE+name+ext,timeout=40,headers={"User-Agent":"ProjectANS-Lab/0.5"})
    response.raise_for_status()
    if len(response.content)>MAX_BYTES[ext]:
        raise ValueError("Annotation/header size guard triggered for "+ext)
    (folder/(name+ext)).write_bytes(response.content)

def scan_record(name,folder):
    report={"record":name}
    for ext in EXTENSIONS:
        fetch_file(ext,name,folder)
    base=str(folder/name)
    header=wfdb.rdheader(base)
    report["sampling_hz"]=float(header.fs)
    report["signal_names"]=list(header.sig_name)
    report["waveform_samples"]=int(header.sig_len)
    report["waveform_seconds"]=round(float(header.sig_len/header.fs),2)
    for annot in ("anI","wqrs","wabp"):
        a=wfdb.rdann(base,annot)
        report[annot]=annotation_summary(a)
    report["status"]="inspected"
    return report

def render(report):
    lines=[
        "# PRCP — Source annotation feasibility audit",
        "",f"Generated UTC: {report['generated_utc']}",
        "Dataset: https://physionet.org/content/prcp/1.0.0/",
        "DOI: 10.13026/C2PC7R", "",
        "**Purpose:** Read public metadata, QRS annotations, ABP annotations and",
        "posture/event annotation **codes** before any response-curve or ANS",
        "deterioration calculation. No waveforms or participant-level physiological",
        "features were saved or committed.","",
        "| Record | Sampling Hz | Signal names | anI markers | QRS annotations | ABP annotations | Status |",
        "|---|---:|---|---:|---:|---:|---|"
    ]
    for x in report["records"]:
        if x["status"]=="inspected":
            lines.append("| {record} | {sampling_hz:.1f} | {signals} | {n} | {q} | {a} | Inspected |".format(
                record=x["record"],sampling_hz=x["sampling_hz"],
                signals=", ".join(x["signal_names"]),n=x["anI"]["n_annotations"],
                q=x["wqrs"]["n_annotations"],a=x["wabp"]["n_annotations"]))
        else:
            lines.append("| {} | — | — | — | — | — | {}: {} |".format(
                x["record"],x.get("error_type","error"),x.get("error","")[:80]))
    lines+=["","## Source annotation vocabulary — do not assume semantics",""]
    for x in report["records"]:
        if x["status"]=="inspected":
            lines+= [
                f"### Record {x['record']}", "",
                f"- Event annotation `.anI` symbol counts: `{json.dumps(x['anI']['symbol_counts'])}`",
                f"- Event annotation `.anI` aux-note vocabulary: `{json.dumps(x['anI']['aux_labels_counts'])}`",
                f"- First/last marker sample: {x['anI']['first_event_sample']} / {x['anI']['last_event_sample']}",
                ""
            ]
    lines+=["## Required next interpretation step","",
        "- Match event/annotation vocabulary to the official PRCP study protocol.",
        "- **Manually verify** that posture-onset annotations correspond to actual waveform transitions, without assuming `.anI` is a gold-standard task-label file.",
        "- Distinguish active stand, slow tilt and rapid tilt; never pool the protocols into one repeated-challenge benchmark.",
        "- Before any clinical claims, verify whether repeatable events are correctly time-aligned; report negative controls and incomplete cases.",
        "- This source only contains **ten healthy subjects**. It cannot by itself validate ANS dysfunction diagnosis or longitudinal deterioration.",
        "","[Measurement validation protocol](../docs/EXPERIMENT_002_ANS_DYSFUNCTION_MEASUREMENT_GATE.md)"]
    return "\n".join(lines)+"\n"

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results=[]
    with TemporaryDirectory() as dirname:
        work=Path(dirname)
        for name in RECORDS:
            try:
                x=scan_record(name,work)
            except Exception as exc:
                x={"record":name,"status":"failed",
                   "error_type":type(exc).__name__,"error":str(exc)[:180]}
            results.append(x)
            print(name,x["status"],flush=True)
    report={"generated_utc":datetime.now(timezone.utc).isoformat(),
            "source":BASE,"downloaded_waveforms":False,
            "records":results,
            "interpretation":"Source-data inventory only, no autonomic-dysfunction measurement"}
    (OUT/"prcp_annotation_preflight.json").write_text(json.dumps(report,indent=2)+"\n")
    (OUT/"PRCP_ANNOTATION_PREFLIGHT.md").write_text(render(report),encoding="utf-8")
    if not any(x["status"]=="inspected" for x in results):
        raise SystemExit("No PRCP annotations readable: engineering gate blocked.")

if __name__=="__main__":
    main()
