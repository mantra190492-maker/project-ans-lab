"""DIAB-PIP-001 preparation, part 2: covariate availability and identity linkage.

Tables and WFDB header TEXT only. Reads no signal of any kind.

Questions answered (all needed before the plan can be frozen):
  1. Does CDED publish age and sex anywhere (tables, data dictionary, header comments)?
  2. Marginal label counts for the columns the plan may use (never broken down by group).
  3. Are IDs shared between datasets the same person (height, race, group agree)?
  4. For how many CDED people could age and sex be recovered through a shared ID?
"""
from __future__ import annotations

import csv
import io
import json
import re
from collections import Counter
from pathlib import Path

import requests

from scripts.cded_inventory import parse_sha256sums
from scripts.diab_prepare import DATASETS, GE71, MISSING, fetch, find_col, subject_key

AGE_SEX = re.compile(r"\b(age|sex|gender|birth|dob|male|female)\b", re.I)
LABEL_COLUMNS = [r"group", r"study", r"visit", r"dm, non-dm, stroke", r"sex", r"gender", r"htn or not", r"beta blockers"]
ID_PATTERNS = [r"subject number", r"patient id", r"subject id", r"subject"]


def read_table(text):
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    return [h.strip() for h in rows[0]], rows[1:]


def cell(row, c):
    return row[c].strip() if c is not None and c < len(row) else ""


def label_counts(header, rows, pattern, keep_ids=None, max_labels=12):
    """Marginal label counts for one column; one row per participant (first non-missing)."""
    c, idc = find_col(header, [pattern]), find_col(header, ID_PATTERNS)
    if c is None or idc is None:
        return None
    first = {}
    for r in rows:
        k = subject_key(cell(r, idc))
        v = cell(r, c)
        if k and (keep_ids is None or k in keep_ids) and v.upper() not in MISSING:
            first.setdefault(k, v.lower())
    counts = Counter(first.values())
    if len(counts) > max_labels:
        return {"distinct_values": len(counts), "participants": len(first)}
    return dict(sorted(counts.items()))


def person_table(header, rows, columns):
    """{subject: {field: first non-missing value}} for the named column patterns."""
    idc = find_col(header, ID_PATTERNS)
    cols = {f: find_col(header, pats) for f, pats in columns.items()}
    out = {}
    for r in rows:
        k = subject_key(cell(r, idc))
        if not k:
            continue
        slot = out.setdefault(k, {f: "" for f in columns})
        for f, c in cols.items():
            v = cell(r, c)
            if not slot[f] and v.upper() not in MISSING:
                slot[f] = v.lower()
    return out, {f: (header[c] if c is not None else None) for f, c in cols.items()}


def as_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def linkage(a, b):
    """Agreement of height (within 0.03 m), race and group for IDs present in both tables."""
    shared = sorted(set(a) & set(b))
    res = {"shared_ids": len(shared), "height_comparable": 0, "height_within_3cm": 0,
           "race_comparable": 0, "race_same": 0, "group_comparable": 0, "group_same": 0}
    for k in shared:
        ha, hb = as_float(a[k].get("height")), as_float(b[k].get("height"))
        if ha and hb:
            res["height_comparable"] += 1
            res["height_within_3cm"] += int(abs(ha - hb) <= 0.03)
        for f in ("race", "group"):
            if a[k].get(f) and b[k].get(f):
                res[f + "_comparable"] += 1
                res[f + "_same"] += int(a[k][f][:2] == b[k][f][:2])
    return res


def header_comment_keys(text):
    keys = Counter()
    for line in text.splitlines():
        if line.startswith("#"):
            body = line.lstrip("# ").strip()
            keys[re.split(r"[:=]", body, maxsplit=1)[0][:30].strip().lower() or "(blank)"] += 1
    return keys


PERSON_COLUMNS = {"height": [r"height \(m\)"], "race": [r"race"], "group": [r"group"],
                  "age": [r"age"], "sex": [r"sex", r"gender"]}


def main():
    session = requests.Session()
    out = Path("reports/explore")
    out.mkdir(parents=True, exist_ok=True)
    lines = ["# DIAB-PIP-001 preparation, part 2 — covariates and identity linkage (tables and header text only)", ""]
    summary, people, record_ids = {}, {}, {}

    for name, cfg in DATASETS.items():
        paths = parse_sha256sums(fetch(cfg["project"], "SHA256SUMS.txt", session).decode("utf-8", errors="replace"))
        records = sorted(p[:-4] for p in paths if cfg["match"].search(p))
        ids = {subject_key(Path(p).name) for p in records}
        record_ids[name] = ids
        tables = [p for p in paths if p.lower().endswith(".csv") and "summary" in p.lower()]
        dictionary = [p for p in paths if p.lower().endswith(".csv") and "dictionary" in p.lower()]
        merged, labels, found_cols = {}, {}, {}
        for t in tables:
            header, rows = read_table(fetch(cfg["project"], t, session).decode("utf-8-sig", errors="replace"))
            ppl, found = person_table(header, rows, PERSON_COLUMNS)
            for f, col in found.items():
                if col and f not in found_cols:
                    found_cols[f] = f"{col} ({Path(t).name})"
            for k, v in ppl.items():
                slot = merged.setdefault(k, {f: "" for f in PERSON_COLUMNS})
                for f in PERSON_COLUMNS:
                    slot[f] = slot[f] or v[f]
            for pat in LABEL_COLUMNS:
                got = label_counts(header, rows, pat, keep_ids=ids)
                if got is not None and pat not in labels:
                    labels[pat] = got
        people[name] = merged
        with_rec = {k: v for k, v in merged.items() if k in ids}
        avail = {f: sum(1 for v in with_rec.values() if v[f]) for f in PERSON_COLUMNS}
        dict_hits = []
        for d in dictionary[:1]:
            _, drows = read_table(fetch(cfg["project"], d, session).decode("utf-8-sig", errors="replace"))
            for r in drows:
                hit = [c.strip()[:80] for c in r[:3] if AGE_SEX.search(c)]
                if hit:
                    dict_hits.append(" | ".join(hit))
        comment_keys, n_with_comments = Counter(), 0
        for p in records:
            keys = header_comment_keys(fetch(cfg["project"], p + ".hea", session).decode("utf-8", errors="replace"))
            n_with_comments += int(bool(keys))
            comment_keys.update(keys.keys())
        summary[name] = {"lab_records": len(records), "ids_without_table_row": len(ids - set(merged)),
                         "columns_found": found_cols, "available_among_lab_record_people": avail,
                         "label_counts_among_lab_record_people": labels,
                         "data_dictionary_rows_mentioning_age_or_sex": dict_hits[:12],
                         "headers_with_comment_lines": n_with_comments, "header_comment_keys": dict(comment_keys.most_common(12))}
        lines += [f"## {name}: {len(records)} lab records; {len(ids - set(merged))} without a table row", "",
                  f"- columns found: {found_cols}",
                  f"- non-missing among people with a lab record (n={len(with_rec)}): {avail}",
                  f"- data-dictionary rows mentioning age or sex: {dict_hits[:12] or 'none'}",
                  f"- headers with comment lines: {n_with_comments}; comment keys: {dict(comment_keys.most_common(12)) or 'none'}", "",
                  "Marginal label counts among people with a lab record (never split by group):", ""]
        lines += [f"- `{k}`: {v}" for k, v in labels.items()] + [""]

    h71, r71 = read_table(fetch(GE71, "Data_Description/GE-71_Data_Summary_Table.csv", session).decode("utf-8-sig", errors="replace"))
    people["GE71"], _ = person_table(h71, r71, PERSON_COLUMNS)
    link = {"CDED_vs_GE75": linkage(people["CDED"], people["GE75"]),
            "CDED_vs_GE71": linkage(people["CDED"], people["GE71"]),
            "GE75_vs_GE71": linkage(people["GE75"], people["GE71"])}
    cded_rec = record_ids["CDED"]
    recover = {"cded_lab_people": len(cded_rec),
               "also_in_GE75_table": len(cded_rec & set(people["GE75"])),
               "also_in_GE75_lab_records": len(cded_rec & record_ids["GE75"]),
               "also_in_GE71_table": len(cded_rec & set(people["GE71"])),
               "age_and_sex_recoverable_via_shared_id": sum(
                   1 for k in cded_rec if any(people[d].get(k, {}).get("age") and people[d].get(k, {}).get("sex") for d in ("GE75", "GE71")))}
    summary["linkage"], summary["cded_age_sex_recovery"] = link, recover
    lines += ["## Are shared IDs the same person?", ""] + [f"- {k}: {v}" for k, v in link.items()] + [""]
    lines += ["## CDED people whose age and sex exist in another dataset under the same ID", "", f"- {recover}", ""]
    (out / "DIAB_PREP2.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (out / "DIAB_PREP2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
