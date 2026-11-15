"""Four-record annotated-NN ECG pilot: compare Costa-reference PIP and legacy PIP.

Downloads only small public Fantasia beat-annotation and header files.
Does NOT use restricted SHHS data or make clinical progression claims.
"""
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
import wfdb

from anslab.heart_rate_fragmentation import fragmentation_features as legacy_fragmentation
from anslab.hrf_costa_reference import costa_fragmentation_from_peaks

BASE="https://physionet.org/files/fantasia/1.0.0/"
RECORDS=("f1y01","f1o01","f2y01","f2o01")
BEAT_SYMBOLS=set("NLRBAaJSVreEj/FfQ")
OUT=Path("reports")
START_S=60
DURATION_S=300
MIN_NORMAL_RR_FRACTION=.95


def annotation_intervals(samples,symbols,fs):
    """NN interval candidates, retaining ectopy gaps at their true positions."""
    samples=np.asarray(samples,dtype=np.int64)
    if len(samples)!=len(symbols):
        raise ValueError("Beat samples and types length mismatch")
    rr_ms=np.diff(samples)*(1000.0/fs)
    sinus=np.asarray([s=="N" for s in symbols],dtype=bool)
    valid=sinus[:-1]&sinus[1:]
    return rr_ms,valid


def fetch(url,destination):
    r=requests.get(url,timeout=40,headers={"User-Agent":"ProjectANS-Lab/0.5"})
    r.raise_for_status()
    if len(r.content)>100_000:
        raise ValueError("Expected small annotation/header, not raw ECG waveform")
    destination.write_bytes(r.content)


def one_record(name,directory):
    for ext in (".hea",".ecg"):
        fetch(BASE+name+ext,directory/(name+ext))
    record=str(directory/name)
    header=wfdb.rdheader(record)
    fs=float(header.fs)
    annotations=wfdb.rdann(record,"ecg")
    lo,hi=int(START_S*fs),int((START_S+DURATION_S)*fs)
    pairs=[(int(sample),str(symbol))
           for sample,symbol in zip(annotations.sample,annotations.symbol)
           if lo<=sample<hi and symbol in BEAT_SYMBOLS]
    if len(pairs)<240:
        raise ValueError(f"Too few annotated beats in five minutes: {len(pairs)}")
    times=[sample for sample,_ in pairs]
    labels=[symbol for _,symbol in pairs]
    rr,valid=annotation_intervals(times,labels,fs)
    plausible=np.isfinite(rr)&(rr>=300)&(rr<=2000)
    clean=valid&plausible
    clean_fraction=float(np.mean(clean))
    diagnostics={
        "record":name,"age_band":"21-34" if "y" in name else "68-85",
        "sampling_hz":fs,"window_s":DURATION_S,
        "annotated_beats":len(pairs),
        "non_normal_beat_annotations":int(sum(x!="N" for x in labels)),
        "intervals_with_normal_beat_endpoints":int(valid.sum()),
        "physiologically_plausible_intervals":int(plausible.sum()),
        "intervals_passing_all_checks":int(clean.sum()),
        "preflight_clean_fraction":round(clean_fraction,4),
    }

    # Clinical rhythm QC is upstream and must remain stricter than reference
    # software's output ability. In particular, do not rescue f2o01 by allowing
    # unrelated gaps or a lower quality threshold.
    if clean_fraction<MIN_NORMAL_RR_FRACTION or clean.sum()<200:
        return {**diagnostics,"status":"qc_excluded",
                "qc_exclusion_reason":"Fewer than 95% valid normal-to-normal intervals or fewer than 200 clean intervals",
                "reference_pip_percent":None,
                "clinical_validation":"none; preflight QC withheld"}

    try:
        author=costa_fragmentation_from_peaks(
            [s/fs for s in times],
            [1 if symbol=="N" else (3 if symbol in ("A","a","S") else 2)
             for symbol in labels],
            sampling_hz=fs,
        )
        old=legacy_fragmentation(rr,validated_sinus=True,valid_mask=valid,
                                 quantization_ms=4.0,min_clean_intervals=200)
    except ValueError as error:
        return {**diagnostics,"status":"qc_excluded",
                "qc_exclusion_reason":str(error),
                "reference_pip_percent":None,
                "clinical_validation":"none; excluded after method-level QC"}

    return {
        **diagnostics,
        "status":"processed",
        "reference_pip_percent":round(author["pip_percent"],3),
        "reference_pnnss_percent":round(author["pnnss_percent"],3),
        "reference_pnnls_percent":round(author["pnnls_percent"],3),
        "reference_n_inflection_points":author["n_inflection_points"],
        "reference_pip_denominator":author["n_author_eligible_nn"],
        "reference_n_hard_inflections":author["n_hard_inflections"],
        "reference_n_soft_inflections":author["n_soft_inflections"],
        "legacy_provisional_pip_percent":round(old["pip_percent"],3),
        "legacy_vs_reference_pip_difference_pp":round(old["pip_percent"]-author["pip_percent"],3),
        "reference_sampling_hz":fs,
        "reference_source_version":"Costa 2024 PhysioNet AWK 1.0.0; independently ported; three reference fixtures exact",
        "candidate_rmssd_ms":round(old["rmssd_ms"],3),
        "candidate_mean_hr_bpm":round(old["heart_rate_bpm"],3),
        "clinical_validation":"none; annotated healthy adults only",
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
                        "error_type":type(exc).__name__,"error":str(exc)[:250]}
            results.append(result)
            print(name,result["status"],result.get("reference_pip_percent"),flush=True)
    payload={
        "study":"ANS-001 Fantasia corrected author-reference HRF measurement comparison",
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "source":BASE,"doi":"10.13026/C2RG61",
        "method":"Corrected Costa 2024 author-equivalent PIP and earlier provisional ternary PIP side by side",
        "records":results,
        "constraints":"Healthy annotated beat pilot, no longitudinal outcomes, no ANS disease labels."
    }
    (OUT/"fantasia_hrf_pilot.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    lines=["# ANS-001 — Fantasia revised HRF pilot (Costa-reference PIP)","",
        "Dataset: [Fantasia v1.0.0](https://physionet.org/content/fantasia/1.0.0/), DOI 10.13026/C2RG61.",
        f"Generated UTC: {payload['generated_utc']}","",
        "**The original pilot's provisional PIP is NOT the author's official PIP definition.**",
        "Corrected PIP follows an independently written implementation that matched Costa's",
        "three official test cases in PIP, PNNSS and PNNLS integer counts.",
        "This does NOT validate physiological interpretation, clinical autonomic deterioration, or disease detection.","",
        "| Record | Age band | Annotated beats | QC normal NN | Costa-style PIP | Old provisional PIP | Difference (pp) | Status |",
        "|---|---|---:|---:|---:|---:|---:|---|"]
    for r in results:
        if r["status"]=="processed":
            lines.append(f"| {r['record']} | {r['age_band']} | {r['annotated_beats']} | {r['preflight_clean_fraction']:.1%} | {r['reference_pip_percent']:.2f}% ({r['reference_n_inflection_points']}/{r['reference_pip_denominator']}) | {r['legacy_provisional_pip_percent']:.2f}% | {r['legacy_vs_reference_pip_difference_pp']:+.2f} | Processed |")
        elif r["status"]=="qc_excluded":
            lines.append(f"| {r['record']} | {r['age_band']} | {r['annotated_beats']} | {r['preflight_clean_fraction']:.1%} | — | — | — | QC withheld |")
        else:
            lines.append(f"| {r['record']} | — | — | — | — | — | — | Failure: {r['error_type']} |")
    lines+=["","## Gate decisions","",
        "- **Primary reference:** the corrected Costa-style PIP, conditional on external sinus beat annotations and preserved QC.",
        "- **Legacy candidate:** prior symbol-transition PIP; retained for transparent difference reporting only, NOT used as official method.",
        "- Excluded records stay excluded: no retroactive relaxation of 95% normal-NN quality.",
        "- ECG sampling frequency is explicitly recorded; 125 versus 250 Hz longitudinal SHHS runs cannot be naively compared.",
        "- Costa's official source uses strict NN bounds (0.3, 1.8) seconds; previous candidate's bound reached 2.0 seconds.",
        "- Real Fantasia pilot is NOT author source differential proof on clinical populations and not ANS diagnosis.",
        "- No restricted data, future outcomes, or individual clinical records have been accessed.",
        "","[Official Costa differential numerical test](HRF_DIFFERENTIAL_TEST.md)."]
    (OUT/"FANTASIA_HRF_PILOT.md").write_text("\n".join(lines)+"\n")
    if sum(r["status"]=="processed" for r in results)<2:
        raise SystemExit("Fewer than two annotated recordings were comparable to official PIP")


if __name__=="__main__":
    main()
