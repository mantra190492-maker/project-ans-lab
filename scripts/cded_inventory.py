"""CDED-ANS-001 stage 1: map the open CDED dataset before any biomarker analysis.

Dataset: PhysioNet "Cerebromicrovascular Disease in Elderly with Diabetes" (CDED) v1.0.1,
DOI 10.13026/00bm-0x81, CC BY 4.0, open access. Adults aged 55-75 with and without
type 2 diabetes; baseline (visit 2) and two-year (visit 8) lab protocols with Valsalva,
supine rest, hyperventilation, CO2 rebreathing and head-up tilt; 24-hour ECG at 1000 Hz.

Why this dataset: it is the only open dataset found so far with standard autonomic
reflex tests repeated two years apart in the high-risk (diabetes) population, plus a
high-resolution passive ECG. That is the minimum needed to test early detection.

This stage is deliberately blind to associations. It reports ONLY structure:
file inventory, record types, channel names, sampling rates, durations, how many
participants have both visits, and which summary-table variables exist with
non-missing counts. No participant-level values and no outcome statistics.
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://physionet.org/files/cded/1.0.1/"
UA = {"User-Agent": "ProjectANS-Lab/0.6 (research; open data inventory)"}
_B = r"(?<![a-z])"   # letter boundaries, so HR_supine matches but 'error' does not
_E = r"(?![a-z])"
KEYWORDS = re.compile(r"valsalva|tilt|orthostat|sit.?to.?stand|heart.?rate|autonom|neuropath|vagal|"
                      r"baroreflex|blood.?pressure|a1c|diabet|beta.?block|"
                      + "|".join(_B + k + _E for k in ("hrv", "rr", "hr", "sbp", "dbp", "bp")), re.I)
MAX_TEXT_BYTES = 5_000_000


def fetch_text(path, session=requests):
    resp = session.get(BASE + path, headers=UA, timeout=60)
    resp.raise_for_status()
    if len(resp.content) > MAX_TEXT_BYTES:
        raise ValueError(f"Unexpectedly large text file: {path}")
    return resp.content.decode("utf-8-sig", errors="replace")


def parse_sha256sums(text):
    paths = []
    for line in text.splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            paths.append(parts[1].lstrip("*").strip())
    return paths


def classify_record(name):
    low = name.lower()
    if re.search(r"db-v2$", low):
        return "labview_visit2"
    if re.search(r"db-v8$", low):
        return "labview_visit8"
    if "ecg" in low or "holter" in low or "me6000" in low:
        return "ecg_24h"
    return "other"


def subject_id(name):
    match = re.search(r"s(\d{3,5})", Path(name).name, re.I)
    return match.group(1) if match else None


def parse_header(text):
    """Minimal WFDB header parse: record line + signal descriptions (no samples)."""
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    first = lines[0].split()
    record = {"multi_segment": "/" in first[0], "n_signals": int(first[1]) if len(first) > 1 else None,
              "fs": None, "n_samples": None, "channels": []}
    if len(first) > 2:
        record["fs"] = float(first[2].split("/")[0])
    if len(first) > 3 and first[3].isdigit():
        record["n_samples"] = int(first[3])
    if not record["multi_segment"]:
        for ln in lines[1:1 + (record["n_signals"] or 0)]:
            fields = ln.split()
            if len(fields) >= 9:
                record["channels"].append(" ".join(fields[8:]))
    return record


def summarize_csv(text):
    reader = csv.DictReader(io.StringIO(text))
    columns = reader.fieldnames or []
    nonmissing = Counter()
    n = 0
    for row in reader:
        n += 1
        for col in columns:
            v = (row.get(col) or "").strip()
            if v and v.upper() not in {"NA", "NAN", "N/A", "."}:
                nonmissing[col] += 1
    return {"rows": n, "columns": [{"name": c, "nonmissing": nonmissing[c]} for c in columns]}


def main(out_dir="reports"):
    session = requests.Session()
    sha_paths = parse_sha256sums(fetch_text("SHA256SUMS.txt", session))
    extensions = Counter(Path(p).suffix.lower() or "(none)" for p in sha_paths)
    records = [r.strip() for r in fetch_text("RECORDS", session).splitlines() if r.strip()]
    kinds = Counter(classify_record(r) for r in records)

    headers = defaultdict(list)
    failures = []
    for rec in records:
        try:
            headers[classify_record(rec)].append(parse_header(fetch_text(rec + ".hea", session)))
        except Exception as err:  # noqa: BLE001 - reported, never hidden
            failures.append({"record_type": classify_record(rec), "error": type(err).__name__})

    def header_summary(items):
        fs = Counter(h["fs"] for h in items)
        chans = Counter(c for h in items for c in h["channels"])
        mins = [h["n_samples"] / h["fs"] / 60 for h in items if h["n_samples"] and h["fs"]]
        return {"n": len(items), "sampling_hz": {str(k): v for k, v in fs.items()},
                "channel_names": dict(chans.most_common()),
                "multi_segment": sum(h["multi_segment"] for h in items),
                "duration_min": {"min": round(min(mins), 1), "median": round(sorted(mins)[len(mins) // 2], 1),
                                 "max": round(max(mins), 1)} if mins else None}

    by_subject = defaultdict(set)
    for rec in records:
        sid = subject_id(rec)
        if sid:
            by_subject[sid].add(classify_record(rec))
    both_visits = sum({"labview_visit2", "labview_visit8"} <= v for v in by_subject.values())
    with_ecg_and_v2 = sum({"labview_visit2", "ecg_24h"} <= v for v in by_subject.values())
    with_all_three = sum({"labview_visit2", "labview_visit8", "ecg_24h"} <= v for v in by_subject.values())

    tables = {}
    for p in sha_paths:
        if p.startswith("Data_Description/") and p.lower().endswith(".csv"):
            try:
                tables[p] = summarize_csv(fetch_text(p.replace(" ", "%20"), session))
            except Exception as err:  # noqa: BLE001
                tables[p] = {"error": type(err).__name__}

    autonomic_vars = sorted({c["name"] for t in tables.values() for c in t.get("columns", [])
                             if KEYWORDS.search(c["name"])})
    annotation_like = sorted({Path(p).suffix for p in sha_paths
                              if Path(p).suffix.lower() not in {".dat", ".hea", ".csv", ".pdf", ".txt", ""}})

    payload = {
        "study": "CDED-ANS-001 stage 1 inventory", "dataset": BASE, "doi": "10.13026/00bm-0x81",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_files": len(sha_paths), "file_extensions": dict(extensions),
        "n_records": len(records), "record_types": dict(kinds),
        "header_summary": {k: header_summary(v) for k, v in headers.items()},
        "header_failures": failures,
        "subjects_with_records": len(by_subject),
        "subjects_with_visit2_and_visit8_lab": both_visits,
        "subjects_with_24h_ecg_and_visit2_lab": with_ecg_and_v2,
        "subjects_with_24h_ecg_visit2_and_visit8": with_all_three,
        "possible_annotation_extensions": annotation_like,
        "summary_tables": tables,
        "candidate_autonomic_variables": autonomic_vars,
        "scope": "Structure only. No participant values, no associations, no outcome statistics.",
    }
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "CDED_INVENTORY.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = ["# CDED-ANS-001 stage 1 — dataset structure (no outcome analysis)", "",
             f"Generated UTC: {payload['generated_utc']}  ", f"Source: {BASE} (CC BY 4.0, DOI 10.13026/00bm-0x81)", "",
             f"- Files: {len(sha_paths)}; WFDB records: {len(records)} ({dict(kinds)})",
             f"- Participants with any record: {len(by_subject)}",
             f"- **Both lab visits (baseline + 2 years): {both_visits}**",
             f"- 24-h ECG + baseline lab: {with_ecg_and_v2}; 24-h ECG + both lab visits: {with_all_three}",
             f"- Non-WFDB/annotation-like extensions: {annotation_like or 'none'}",
             f"- Header read failures: {len(failures)}", "", "## Record types", ""]
    for kind, summary in payload["header_summary"].items():
        lines += [f"### {kind} (n={summary['n']})", "",
                  f"- Sampling rates: {summary['sampling_hz']}; multi-segment headers: {summary['multi_segment']}",
                  f"- Duration (min): {summary['duration_min']}",
                  f"- Channels: {', '.join(f'{k} ({v})' for k, v in list(summary['channel_names'].items())[:30])}", ""]
    lines += ["## Summary-table variables matching autonomic/diabetes keywords", ""]
    lines += [f"- {v}" for v in autonomic_vars] or ["- none found"]
    lines += ["", "## Stage 2 gate", "",
              "Stage 2 (the biomarker test) is frozen in docs/CDED_ANS_001_PLAN.md and runs only after this report "
              "confirms: (1) Valsalva and tilt segments can be located in the lab records, (2) ECG and continuous BP "
              "exist at both visits, (3) at least ~35 participants have both visits plus a baseline 24-h ECG."]
    (out / "CDED_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main()
