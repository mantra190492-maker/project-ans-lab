"""CDED-ANS-001 stage 1b: decode protocol segments (structure only, no outcomes).

Stage 1 found that every lab record (500 Hz) carries a 'marker' channel plus ecg, abp,
breathing and TCD channels. Before any outcome is computed we need to know how the
Valsalva, supine-rest and tilt segments are marked.

This script:
  1. Publishes the dataset's own channel documentation (GE-79_Files_and_Channels.csv).
  2. Reads ONLY the marker channel (plus a flat-line check on ecg/abp) from a fixed
     sample of lab records (first 12 of each visit in RECORDS order) and reports marker
     values, run lengths and event timing.

No heart-rate, blood-pressure or Valsalva values are computed or reported.
"""
from __future__ import annotations

import csv
import io
import json
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

from scripts.cded_inventory import BASE, UA, classify_record, fetch_text

SAMPLE_PER_VISIT = 12
MAX_DAT_BYTES = 300 * 1024 * 1024


def download(path, dest, session):
    with session.get(BASE + path, headers=UA, timeout=120, stream=True) as resp:
        resp.raise_for_status()
        size = 0
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(1 << 20):
                size += len(chunk)
                if size > MAX_DAT_BYTES:
                    raise ValueError("record larger than cap")
                fh.write(chunk)


def run_lengths(values, fs, min_seconds=0.5):
    """Collapse a marker trace into (value, start_s, duration_s) runs."""
    v = np.round(np.asarray(values, dtype=float), 2)
    edges = np.flatnonzero(np.diff(v) != 0) + 1
    starts = np.concatenate([[0], edges])
    ends = np.concatenate([edges, [len(v)]])
    runs = [(float(v[s]), s / fs, (e - s) / fs) for s, e in zip(starts, ends)]
    return [r for r in runs if r[2] >= min_seconds] or runs[:1]


def summarize_record(rec_path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(rec_path).name
        directory = str(Path(rec_path).parent)
        for ext in (".hea", ".dat"):
            download(f"{directory}/{name}{ext}", Path(tmp) / f"{name}{ext}", session)
        header = wfdb.rdheader(str(Path(tmp) / name))
        names = [n.lower() for n in header.sig_name]
        want = [i for i, n in enumerate(names) if n in ("marker", "ecg", "abp")]
        rec = wfdb.rdrecord(str(Path(tmp) / name), channels=want)
        sig = {rec.sig_name[j].lower(): rec.p_signal[:, j] for j in range(len(want))}
        fs = float(rec.fs)
        runs = run_lengths(sig["marker"], fs)
        flat = {k: bool(np.nanstd(sig[k]) < 1e-6) for k in ("ecg", "abp") if k in sig}
        return {"record": rec_path, "fs": fs, "duration_min": round(len(sig["marker"]) / fs / 60, 1),
                "marker_distinct_values": sorted({r[0] for r in runs}),
                "marker_runs": [{"value": r[0], "start_s": round(r[1], 1), "duration_s": round(r[2], 1)} for r in runs][:80],
                "n_marker_runs": len(runs), "flat_channels": flat}


def main(out_dir="reports"):
    session = requests.Session()
    channels_csv = fetch_text("Data_Description/GE-79_Files_and_Channels.csv", session)
    doc_rows = [r for r in csv.reader(io.StringIO(channels_csv)) if any(c.strip() for c in r)]

    records = [r.strip() for r in fetch_text("RECORDS", session).splitlines() if r.strip()]
    sample = ([r for r in records if classify_record(r) == "labview_visit2"][:SAMPLE_PER_VISIT]
              + [r for r in records if classify_record(r) == "labview_visit8"][:SAMPLE_PER_VISIT])
    results, failures = [], []
    for rec in sample:
        try:
            results.append(summarize_record(rec, session))
            print("ok", rec, flush=True)
        except Exception as err:  # noqa: BLE001
            failures.append({"record": rec, "error": f"{type(err).__name__}: {str(err)[:150]}"})

    value_counts = Counter(v for r in results for v in r["marker_distinct_values"])
    patterns = Counter(tuple(x["value"] for x in r["marker_runs"]) for r in results)
    payload = {"study": "CDED-ANS-001 stage 1b segment decoding", "generated_utc": datetime.now(timezone.utc).isoformat(),
               "files_and_channels_doc": doc_rows, "sampled_records": len(sample), "decoded": len(results),
               "failures": failures, "marker_value_record_counts": {str(k): v for k, v in value_counts.items()},
               "marker_patterns": [{"sequence": list(k), "n_records": v} for k, v in patterns.most_common(10)],
               "records": results, "scope": "Marker structure and channel documentation only; no physiological values."}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "CDED_SEGMENTS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = ["# CDED-ANS-001 stage 1b — protocol segment decoding (structure only)", "",
             f"Generated UTC: {payload['generated_utc']}", "",
             f"Decoded {len(results)} of {len(sample)} sampled lab records ({SAMPLE_PER_VISIT} per visit). "
             f"Failures: {len(failures)}.", "",
             "## Dataset channel documentation (GE-79_Files_and_Channels.csv)", "", "```"]
    lines += [" | ".join(c.strip() for c in r if c is not None)[:220] for r in doc_rows[:120]]
    lines += ["```", "", "## Marker values across records", ""]
    lines += [f"- value {k}: present in {v} records" for k, v in sorted(value_counts.items())]
    lines += ["", "## Most common marker sequences (values in time order)", ""]
    lines += [f"- {p['n_records']} records: {p['sequence'][:30]}" for p in payload["marker_patterns"]]
    lines += ["", "## Example records", ""]
    for r in results[:4]:
        lines.append(f"### {r['record']} ({r['duration_min']} min, flat channels: {r['flat_channels']})")
        lines += [f"- {x['value']} at {x['start_s']} s for {x['duration_s']} s" for x in r["marker_runs"][:25]]
        lines.append("")
    (out / "CDED_SEGMENTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
