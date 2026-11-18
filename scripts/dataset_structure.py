"""Structure-only map of an open PhysioNet dataset (no participant values, no associations).

Used to decide, BEFORE any outcome is computed, whether a dataset can serve as a
discovery or replication set: which record groups exist, channels, sampling rates,
durations, how many participants per group, and which summary-table variables exist.

Example:
  python -m scripts.dataset_structure --slug cerebral-perfusion-diabetes/1.0.1 --name CPD
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

from scripts.cded_inventory import KEYWORDS, UA, parse_header, parse_sha256sums, summarize_csv

ROOT = "https://physionet.org/files/"


def get_text(url, session, tries=4):
    last = None
    for attempt in range(tries):
        try:
            resp = session.get(url, headers=UA, timeout=60)
            if resp.status_code in (502, 503, 504, 429):
                raise requests.HTTPError(f"{resp.status_code}")
            resp.raise_for_status()
            return resp.content.decode("utf-8-sig", errors="replace")
        except requests.RequestException as err:
            last = err
            time.sleep(1.5 * (attempt + 1))
    raise last


def subject_of(path):
    match = re.search(r"[sS](\d{3,5})", Path(path).name)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()
    base = ROOT + args.slug.strip("/") + "/"
    session = requests.Session()
    paths = parse_sha256sums(get_text(base + "SHA256SUMS.txt", session))
    ext = Counter(Path(p).suffix.lower() or "(none)" for p in paths)
    headers = [p[:-4] for p in paths if p.lower().endswith(".hea")]

    groups = defaultdict(list)
    failures = 0
    for rec in headers:
        try:
            h = parse_header(get_text(base + rec.replace(" ", "%20") + ".hea", session))
            h["subject"] = subject_of(rec)
            h["name"] = Path(rec).name
            groups[str(Path(rec).parent)].append(h)
        except Exception:  # noqa: BLE001 - counted and reported
            failures += 1

    group_summary = {}
    subjects_by_group = {}
    for g, items in sorted(groups.items()):
        mins = sorted(h["n_samples"] / h["fs"] / 60 for h in items if h["n_samples"] and h["fs"])
        subs = {h["subject"] for h in items if h["subject"]}
        subjects_by_group[g] = subs
        suffixes = Counter(re.sub(r"^[sS]\d{3,5}", "", h["name"]) for h in items)
        group_summary[g] = {
            "records": len(items), "participants": len(subs),
            "sampling_hz": dict(Counter(str(h["fs"]) for h in items)),
            "duration_min": {"min": round(mins[0], 1), "median": round(mins[len(mins) // 2], 1),
                             "max": round(mins[-1], 1)} if mins else None,
            "channels": dict(Counter(c for h in items for c in h["channels"]).most_common(20)),
            "name_suffixes": dict(suffixes.most_common(8)),
        }
    overlap = {}
    keys = list(subjects_by_group)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            n = len(subjects_by_group[a] & subjects_by_group[b])
            if n:
                overlap[f"{a} & {b}"] = n

    tables = {}
    for p in paths:
        if p.lower().endswith(".csv") and "summary" in p.lower() or "description" in str(Path(p).parent).lower() and p.lower().endswith(".csv"):
            try:
                tables[p] = summarize_csv(get_text(base + p.replace(" ", "%20"), session))
            except Exception as err:  # noqa: BLE001
                tables[p] = {"error": type(err).__name__}
    auton = sorted({c["name"].strip() for t in tables.values() for c in t.get("columns", [])
                    if c["name"] and KEYWORDS.search(c["name"])})

    payload = {"dataset": base, "name": args.name, "generated_utc": datetime.now(timezone.utc).isoformat(),
               "n_files": len(paths), "extensions": dict(ext), "n_headers": len(headers),
               "header_failures": failures, "groups": group_summary, "participant_overlap": overlap,
               "tables": {k: {"rows": v.get("rows"), "n_columns": len(v.get("columns", []))} for k, v in tables.items()},
               "candidate_autonomic_variables": auton,
               "scope": "Structure only. No participant values, no associations."}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"STRUCTURE_{args.name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [f"# Structure map — {args.name} (no outcome analysis)", "", f"Source: {base}  ",
             f"Generated UTC: {payload['generated_utc']}", "",
             f"Files: {len(paths)} {dict(ext)}; WFDB headers: {len(headers)}; header failures: {failures}", "",
             "| Record group | Records | People | Hz | Minutes (min/median/max) | Channels |", "|---|---:|---:|---|---|---|"]
    for g, s in group_summary.items():
        d = s["duration_min"] or {}
        lines.append(f"| {g} | {s['records']} | {s['participants']} | {', '.join(s['sampling_hz'])} | "
                     f"{d.get('min')}/{d.get('median')}/{d.get('max')} | {', '.join(list(s['channels'])[:12])} |")
    lines += ["", "## Participant overlap between groups", ""] + [f"- {k}: {v}" for k, v in overlap.items()]
    lines += ["", "## Summary tables", ""] + [f"- {k}: {v['rows']} rows × {v['n_columns']} columns" for k, v in payload["tables"].items()]
    lines += ["", "## Variables matching autonomic/diabetes keywords", ""] + [f"- {v}" for v in auton[:120]]
    (out / f"STRUCTURE_{args.name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:30]))


if __name__ == "__main__":
    main()
