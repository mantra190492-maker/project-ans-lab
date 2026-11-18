"""DIAB-PIP-001 preparation: structure only. Reads NO ECG and NO blood pressure.

For CDED visit 2 (cded/1.0.1) and GE-75 (cerebral-perfusion-diabetes/1.0.1):
  - summary-table column NAMES with non-missing counts, and group-label counts
  - documentation rows describing the lab protocol
  - participant-ID overlap between the datasets and with GE-71 (already analysed)
  - a CO2-only search for a quiet-breathing window early in each lab record

Nothing here compares any ECG-derived value between groups.
"""
from __future__ import annotations

import csv
import io
import json
import re
import tempfile
import time
from collections import Counter
from pathlib import Path

import numpy as np
import requests

from scripts.cded_inventory import parse_sha256sums
from scripts.ge71_analysis import ENV_HZ, window_qc
from scripts.ge71_prepare import envelope

UA = {"User-Agent": "ProjectANS-Lab/0.9"}
ROOTS = ("https://physionet-open.s3.amazonaws.com/", "https://physionet.org/files/")
DATASETS = {
    "CDED": {"project": "cded/1.0.1/", "match": re.compile(r"db-v2\.hea$", re.I)},
    "GE75": {"project": "cerebral-perfusion-diabetes/1.0.1/", "match": re.compile(r"head-up-tilt/.*\.hea$", re.I)},
}
GE71 = "cerebral-vasoreg-diabetes/1.0.0/"
WIN_S, STEP_S, FIRST_S, LAST_S = 240, 10, 30, 900
MISSING = {"", "NA", "NAN", "N/A", ".", "-", "NONE", "NULL"}
DOC_KEYS = re.compile(r"tilt|baseline|supine|valsalva|hypervent|rebreath|marker|rest", re.I)


def fetch(project, path, session, tries=3):
    last = None
    for attempt in range(tries):
        for root in ROOTS:
            try:
                r = session.get(root + project + path.replace(" ", "%20"), headers=UA, timeout=180)
                r.raise_for_status()
                return r.content
            except requests.RequestException as err:
                last = err
        time.sleep(8 * (attempt + 1))
    raise last


def subject_key(text):
    m = re.search(r"(\d{1,5})", text or "")
    return f"s{int(m.group(1)):04d}" if m else None


def earliest_quiet_window(co2_env, hz=ENV_HZ, win_s=WIN_S, step_s=STEP_S, first_s=FIRST_S, last_s=LAST_S):
    """Earliest window of quiet, stable breathing judged from CO2 only. Returns (start_s or None, n_passing)."""
    x = np.asarray(co2_env, dtype=float)
    passing = []
    for start in range(first_s, last_s - win_s + 1, step_s):
        seg = x[start * hz:(start + win_s) * hz]
        if len(seg) == win_s * hz and window_qc(seg, hz) == "ok":
            passing.append(start)
    return (passing[0] if passing else None), len(passing)


def table_columns(text):
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip() for h in rows[0]]
    out = []
    for c, name in enumerate(header):
        k = sum(1 for r in rows[1:] if c < len(r) and r[c].strip().upper() not in MISSING)
        out.append((c, name, k))
    return header, rows[1:], out


def find_col(header, patterns):
    for pat in patterns:
        for i, h in enumerate(header):
            if re.fullmatch(pat, h.strip(), re.I):
                return i
    return None


def demographics(header, rows):
    idc = find_col(header, [r"subject number", r"patient id", r"subject id", r"subject"])
    agec = find_col(header, [r"age", r"age \(years\)", r"age at .*"])
    sexc = find_col(header, [r"gender", r"sex"])
    grpc = find_col(header, [r"group"])
    people = {}
    for r in rows:
        if idc is None or len(r) <= idc:
            continue
        k = subject_key(r[idc])
        if not k:
            continue
        get = lambda c: r[c].strip() if c is not None and c < len(r) else ""  # noqa: E731
        people[k] = {"age": get(agec), "sex": get(sexc).lower()[:1], "group": get(grpc).lower()}
    cols = {"id": header[idc] if idc is not None else None, "age": header[agec] if agec is not None else None,
            "sex": header[sexc] if sexc is not None else None, "group": header[grpc] if grpc is not None else None}
    return people, cols


def same_person_evidence(a, b):
    shared = sorted(set(a) & set(b))
    match = 0
    comparable = 0
    for k in shared:
        try:
            age_a, age_b = float(a[k]["age"]), float(b[k]["age"])
        except ValueError:
            continue
        if a[k]["sex"] and b[k]["sex"]:
            comparable += 1
            match += int(a[k]["sex"] == b[k]["sex"] and abs(age_a - age_b) <= 3)
    return {"shared_ids": len(shared), "comparable": comparable, "same_sex_and_age_within_3y": match}


def load_co2(project, path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            (Path(tmp) / (name + ext)).write_bytes(fetch(project, path + ext, session))
        header = wfdb.rdheader(str(Path(tmp) / name))
        names = [n.lower() for n in header.sig_name]
        fs = float(header.fs)
        stop = min(header.sig_len, int((LAST_S + 5) * fs))
        rec = wfdb.rdrecord(str(Path(tmp) / name), sampfrom=0, sampto=stop, channels=[names.index("co2")])
        return rec.p_signal[:, 0], fs, header.sig_len / fs / 60


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    session = requests.Session()
    out, qc = Path("reports/explore"), Path("qc")
    out.mkdir(parents=True, exist_ok=True)
    qc.mkdir(exist_ok=True)
    lines = ["# DIAB-PIP-001 preparation — structure only (no ECG, no blood pressure)", ""]
    summary = {}
    people = {}

    # ---- tables and documentation ----
    for name, cfg in DATASETS.items():
        paths = parse_sha256sums(fetch(cfg["project"], "SHA256SUMS.txt", session).decode("utf-8", errors="replace"))
        cfg["records"] = sorted(p[:-4] for p in paths if cfg["match"].search(p))
        tables = [p for p in paths if p.lower().endswith(".csv") and "summary" in p.lower()]
        docs = [p for p in paths if p.lower().endswith(".csv") and "files_and_channels" in p.lower().replace(" ", "_")]
        lines += [f"## {name}: {len(cfg['records'])} lab records", ""]
        merged = {}
        colfile = [f"# {name} summary-table columns (names and non-missing counts only)", ""]
        for t in tables:
            header, rows, cols = table_columns(fetch(cfg["project"], t, session).decode("utf-8-sig", errors="replace"))
            ppl, found = demographics(header, rows)
            for k, v in ppl.items():
                slot = merged.setdefault(k, {"age": "", "sex": "", "group": ""})
                for f in ("age", "sex", "group"):
                    slot[f] = slot[f] or v[f]
            colfile += [f"## {t} ({len(rows)} rows)", ""] + [f"- {c} | {n[:90]} | {k}" for c, n, k in cols] + [""]
            lines.append(f"- table `{t}`: {len(rows)} rows, {len(header)} columns; id/age/sex/group columns found: {found}")
        (out / f"DIAB_PREP_{name}_COLUMNS.md").write_text("\n".join(colfile) + "\n", encoding="utf-8")
        people[name] = merged
        rec_ids = {subject_key(Path(p).name) for p in cfg["records"]}
        with_rec = {k: v for k, v in merged.items() if k in rec_ids}
        groups = Counter(v["group"] or "(blank)" for v in with_rec.values())
        sexes = Counter(v["sex"] or "(blank)" for v in with_rec.values())
        n_age = sum(1 for v in with_rec.values() if re.fullmatch(r"\d+(\.\d+)?", v["age"] or ""))
        summary[name] = {"records": len(cfg["records"]), "records_in_tables": len(with_rec), "group_counts": dict(groups),
                         "sex_counts": dict(sexes), "with_age": n_age}
        lines += [f"- people with a lab record and a table row: {len(with_rec)}; group labels: {dict(groups)}; sex labels: {dict(sexes)}; with age: {n_age}", ""]
        for d in docs[:1]:
            rows = [r for r in csv.reader(io.StringIO(fetch(cfg["project"], d, session).decode("utf-8-sig", errors="replace"))) if any(c.strip() for c in r)]
            hits = [" | ".join(c.strip() for c in r if c.strip())[:300] for r in rows if DOC_KEYS.search(" ".join(r))]
            lines += [f"Documentation rows from `{d}` mentioning the protocol:", "", "```"] + hits[:25] + ["```", ""]

    # ---- overlap ----
    ge71_table = fetch(GE71, "Data_Description/GE-71_Data_Summary_Table.csv", session).decode("utf-8-sig", errors="replace")
    h71, r71, _ = table_columns(ge71_table)
    people["GE71"], _ = demographics(h71, r71)
    overlap = {"CDED_vs_GE75": same_person_evidence(people["CDED"], people["GE75"]),
               "CDED_vs_GE71": same_person_evidence(people["CDED"], people["GE71"]),
               "GE75_vs_GE71": same_person_evidence(people["GE75"], people["GE71"])}
    summary["id_overlap"] = overlap
    lines += ["## Participant-ID overlap (same number in two datasets; age and sex compared to judge whether it is the same person)", ""]
    lines += [f"- {k}: {v}" for k, v in overlap.items()] + [""]

    # ---- CO2-only quiet window ----
    lines += [f"## CO2-only search: earliest {WIN_S}-s quiet-breathing window starting {FIRST_S}–{LAST_S - WIN_S} s", ""]
    for name, cfg in DATASETS.items():
        starts, status, traces = [], Counter(), []
        for p in cfg["records"]:
            try:
                co2, fs, minutes = load_co2(cfg["project"], p, session)
                env = envelope(co2, fs, ENV_HZ)
                start, n_pass = earliest_quiet_window(env)
                status["window_found" if start is not None else "no_window"] += 1
                if start is not None:
                    starts.append(start)
                traces.append((Path(p).name, env, start))
            except Exception as err:  # noqa: BLE001
                status[f"error_{type(err).__name__}"] += 1
            print(name, Path(p).name, flush=True)
        q = [float(np.percentile(starts, v)) for v in (10, 25, 50, 75, 90)] if starts else None
        summary[name]["rest_window"] = {"status": dict(status), "start_s_p10_25_50_75_90": q}
        lines += [f"- {name}: {dict(status)}; window start (s) 10/25/50/75/90th percentile: {q}"]
        for sheet in range(0, min(len(traces), 60), 30):
            chunk = traces[sheet:sheet + 30]
            fig, axes = plt.subplots(5, 6, figsize=(24, 14))
            for ax, (rid, env, start) in zip(axes.ravel(), chunk):
                t = np.arange(len(env)) / ENV_HZ / 60
                ax.plot(t, env, linewidth=0.3, color="k")
                if start is not None:
                    ax.axvspan(start / 60, (start + WIN_S) / 60, color="green", alpha=0.3)
                ax.set_title(f"{rid} {'ok' if start is not None else 'none'}", fontsize=8)
                ax.set_xlim(0, LAST_S / 60)
                ax.tick_params(labelsize=6)
            for ax in axes.ravel()[len(chunk):]:
                ax.axis("off")
            fig.suptitle(f"{name}: CO2 only, first 15 min. Green = earliest quiet-breathing window")
            fig.tight_layout()
            fig.savefig(qc / f"diab_prep_{name}_{sheet // 30 + 1}.png", dpi=55)
            plt.close(fig)

    (out / "DIAB_PREP.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    (out / "DIAB_PREP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines)[:3000])


if __name__ == "__main__":
    main()
