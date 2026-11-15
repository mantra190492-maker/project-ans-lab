"""ANS-001 cohort feasibility: reproducible, device-matched, age-stratified PhysioNet sample.

Fixed selection (seed 20261115): 5 records from each of four age strata, 20 total.
Uses a comparable 5-minute supine rest window beginning 60 seconds into recording.
Does NOT establish an age-biomarker, clinical benefit, or longevity prediction.
"""
import csv
import json
import random
import statistics
import tempfile
from collections import Counter
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import numpy as np
import requests
import wfdb

from anslab.physio_qc import analyze_signals

BASE = "https://physionet.org/files/autonomic-aging-cardiovascular/1.0.0/"
OUT = Path("reports")
SEED = 20261115
PER_GROUP = 5
FIRST_SECOND = 60
WINDOW_SECONDS = 300
MAX_FILE_BYTES = 32 * 1024 * 1024
STRATA = {
    "18-34": (1, 4),
    "35-49": (5, 7),
    "50-64": (8, 10),
    "65+": (11, 15),
}
AGE_RANGES = {
    1:"18-19",2:"20-24",3:"25-29",4:"30-34",5:"35-39",
    6:"40-44",7:"45-49",8:"50-54",9:"55-59",10:"60-64",
    11:"65-69",12:"70-74",13:"75-79",14:"80-84",15:"85-92",
}

def download(url, destination):
    error = None
    for attempt in range(3):
        try:
            with requests.get(url, stream=True, timeout=90,
                              headers={"User-Agent":"ProjectANS-Lab/0.2"}) as response:
                response.raise_for_status()
                size = 0
                with destination.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 512):
                        size += len(chunk)
                        if size > MAX_FILE_BYTES:
                            raise ValueError("Recording exceeded download cap")
                        f.write(chunk)
            return
        except (requests.RequestException, OSError) as exc:
            error = exc
            destination.unlink(missing_ok=True)
            if attempt < 2:
                import time
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Download failure after 3 attempts: {error}")

def read_subjects():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "subject-info.csv"
        download(BASE + "subject-info.csv", path)
        text = path.read_text(encoding="utf-8-sig")
    result = []
    for row in csv.DictReader(StringIO(text)):
        try:
            code = int(float(row["Age_group"]))
            if code not in AGE_RANGES:
                continue
            result.append({
                "record": row["ID"].strip().zfill(4),
                "age_group": code,
                "age_range": AGE_RANGES[code],
                "sex_code": int(row["Sex"]),
                "bmi": float(row["BMI"]) if row["BMI"].strip().lower() != "nan" else None,
                "device_code": int(row["Device"]),
                "length_min": float(row["Length"]),
            })
        except (ValueError, TypeError, KeyError):
            continue
    if len(result) < 50:
        raise ValueError("Participant metadata unavailable or parsing failed")
    return result

def choose_subjects(subjects, per_group=PER_GROUP, seed=SEED):
    if not 1 <= per_group <= 5:
        raise ValueError("Pilot cap: 1-5 participants per age stratum")
    selected = []
    for ordinal, (stratum, (minimum, maximum)) in enumerate(STRATA.items()):
        pool = [r for r in subjects if minimum <= r["age_group"] <= maximum
                and r["device_code"] == 0 and r["length_min"] >= 8
                and r["sex_code"] in (0, 1)]
        rng = random.Random(seed + ordinal)
        male = [r for r in pool if r["sex_code"] == 0]
        female = [r for r in pool if r["sex_code"] == 1]
        rng.shuffle(male)
        rng.shuffle(female)
        chosen = male[:per_group//2] + female[:per_group//2]
        leftovers = [x for x in pool if x["record"] not in {y["record"] for y in chosen}]
        rng.shuffle(leftovers)
        chosen = (chosen + leftovers)[:per_group]
        if len(chosen) != per_group:
            raise ValueError(f"Insufficient qualifying records in {stratum}")
        selected.extend([{**item, "age_stratum":stratum} for item in chosen])
    if len({r["record"] for r in selected}) != len(selected):
        raise ValueError("Duplicate participant selection")
    return selected

def get_record_window(identifier, folder):
    for ext in (".hea",):
        download(BASE + identifier + ext, folder / (identifier + ext))
    header = wfdb.rdheader(str(folder / identifier))
    fs = float(header.fs)
    from_sample, to_sample = int(FIRST_SECOND * fs), int((FIRST_SECOND + WINDOW_SECONDS) * fs)
    if header.sig_len < to_sample:
        raise ValueError("Recording shorter than standardized analysis window")
    download(BASE + identifier + ".dat", folder / (identifier + ".dat"))
    record = wfdb.rdrecord(str(folder / identifier), sampfrom=from_sample, sampto=to_sample)
    names = [s.upper() for s in record.sig_name]
    ecg_idx = next((i for i, s in enumerate(names) if "ECG" in s), None)
    bp_idx = next((i for i, s in enumerate(names) if "BP" in s), None)
    if ecg_idx is None or bp_idx is None:
        raise ValueError(f"Required ECG/BP signals missing: {record.sig_name}")
    return (np.asarray(record.p_signal[:,ecg_idx], dtype=float),
            np.asarray(record.p_signal[:,bp_idx], dtype=float), fs)

def save_plot(item, ecg, bp, fs, positions):
    # Waveforms and detections are plotted only for visual QA, not validated here.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rpeaks, bppeaks = positions
    n = min(len(ecg), int(fs * 10))
    t = np.arange(n) / fs
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    axes[0].plot(t, ecg[:n], linewidth=0.8)
    rp = rpeaks[rpeaks < n]
    axes[0].scatter(rp/fs, ecg[rp], s=14, marker="x")
    axes[0].set_ylabel("ECG (raw units)")
    axes[1].plot(t, bp[:n], linewidth=0.8)
    sp = bppeaks[bppeaks < n]
    axes[1].scatter(sp/fs, bp[sp], s=14, marker="x")
    axes[1].set_ylabel("BP (mmHg)")
    axes[1].set_xlabel("Seconds within standardized window")
    fig.suptitle(f"Record {item['record']} · {item['age_stratum']} · automated peaks (unverified)")
    fig.tight_layout()
    name = f"cohort_qc_{item['age_stratum'].replace('+','plus').replace('-','to')}.png"
    fig.savefig(OUT/name, dpi=120)
    plt.close(fig)
    return name

def build_report(results):
    finished = [r for r in results if r["status"] == "processed"]
    passed = [r for r in finished if r["automatic_ecg_qc"] == "pass"]
    lines = [
        "# ANS-001 — 20-participant age-stratified waveform feasibility",
        "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Participants selected: {len(results)}",
        f"Recordings computationally processed: {len(finished)}",
        f"Automatic ECG consistency checks passed: {len(passed)}",
        f"Exploratory BRS values allowed past quality gate: {sum(r.get('brs_ms_per_mmHg_exploratory') is not None for r in results)}",
        "",
        "> **Exploratory engineering output. No manual ECG or BP annotation audit, clinical validation, longitudinal outcomes, or established ageing biomarker.**",
        "",
        "Five minutes of resting data per participant, beginning one minute after recording start.",
        "Participants selected with a fixed random seed from four age strata; device 0 only.",
        "Sex partially balanced; BMI not matched. This sample is NOT representative.",
        "",
        "| Age band | Selected | Processed | Automatic ECG-QC pass | Median screened RMSSD (ms)* |",
        "|---|---:|---:|---:|---:|"
    ]
    for band in STRATA:
        all_records = [r for r in results if r["age_stratum"] == band]
        process = [r for r in all_records if r["status"] == "processed"]
        quality = [r for r in process if r["automatic_ecg_qc"] == "pass"]
        values = [r["rmssd_ms"] for r in quality]
        median = f"{statistics.median(values):.1f}" if values else "NA"
        lines.append(f"| {band} | {len(all_records)} | {len(process)} | {len(quality)} | {median} |")
    lines += [
        "",
        "*Descriptive pilot values only; the estimator is not independently validated.",
        "",
        "## Individual processing log",
        "",
        "| ID | Age group | Sex (coded) | Status | ECG QC | HRV RMSSD | BRS sequence count |",
        "|---|---|---|---|---|---:|---:|"
    ]
    for r in results:
        rmssd = f"{r['rmssd_ms']:.1f}" if r.get("rmssd_ms") is not None else "NA"
        lines.append(f"| {r['record']} | {r['age_range']} | {r['sex_code']} | {r['status']} | {r.get('automatic_ecg_qc','NA')} | {rmssd} | {r.get('brs_sequences_nonoverlapping','NA')} |")
    lines += [
        "", "## Method limitations and interpretation",
        "",
        "- Detector agreement is a consistency check between two algorithms, **not ground truth**.",
        "- RR screening does not prove intervals are normal-to-normal; automated HRV is provisional.",
        "- BRS is deliberately withheld when recording quality or sequences are insufficient.",
        "- BP alignment and systolic detection must be verified manually before any BRS use.",
        "- Different age strata can differ in BMI, sex, medications or other unmeasured factors.",
        "- No inferential age association, age prediction or clinical claim is generated at this gate.",
        "- The dataset's original authors already reported HRV-age patterns; replication is not novelty.",
        "",
        "Source: https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/",
        "Citation: Schumann & Bär (2021), DOI 10.13026/2hsy-t491.",
        "", "Raw QC diagnostics and four representative 10-second plots are in the Actions artifact.",
    ]
    (OUT/"COHORT_001_SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subjects = read_subjects()
    selection = choose_subjects(subjects)
    results = []
    plotted = set()
    for person in selection:
        item = dict(person)
        try:
            with tempfile.TemporaryDirectory() as dirname:
                ecg, bp, fs = get_record_window(item["record"], Path(dirname))
                metrics, positions = analyze_signals(ecg, bp, fs)
                item.update(metrics)
                item["status"] = "processed"
                item["sampling_hz"] = fs
                if item["age_stratum"] not in plotted:
                    item["qc_plot"] = save_plot(item, ecg, bp, fs, positions)
                    plotted.add(item["age_stratum"])
        except Exception as exc:
            item["status"] = "failed"
            item["error_type"] = type(exc).__name__
            item["error"] = str(exc)[:400]
        results.append(item)
        print(f"{item['record']} ({item['age_stratum']}): {item['status']} / {item.get('automatic_ecg_qc','NA')}", flush=True)
    (OUT/"physionet_cohort.json").write_text(json.dumps({
        "study": "ANS-001 cohort feasibility v1", "seed": SEED,
        "dataset": "PhysioNet Autonomic Aging 1.0.0",
        "window_start_s": FIRST_SECOND,"window_duration_s": WINDOW_SECONDS,
        "device_filter": 0,"records":results,
        "limitations":"Automatic waveform processing, not validated HRV/BRS or an ageing biomarker"
    }, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    keys = ["record","age_stratum","age_group","age_range","sex_code","bmi","device_code",
            "status","automatic_ecg_qc","qrs_detector_agreement_f1",
            "rr_clean_fraction","heart_rate_bpm","sdnn_ms","rmssd_ms",
            "bp_rpeak_match_fraction","brs_sequences_nonoverlapping",
            "brs_ms_per_mmHg_exploratory","error"]
    with (OUT/"physionet_cohort.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    build_report(results)
    print(f"Processed {sum(r['status']=='processed' for r in results)}/{len(results)} records.")
    if not any(r["status"] == "processed" for r in results):
        raise SystemExit("FAIL: No physiological recording processed")

if __name__ == "__main__":
    main()
