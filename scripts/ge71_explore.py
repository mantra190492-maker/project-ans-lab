"""GE-71 (PhysioNet 'Cerebral Vasoregulation in Diabetes' v1.0.0) documentation and marker structure.

Structure only: channel documentation, marker-table column names with aggregate
ranges (to learn units), data-dictionary rows about autonomic variables, and
non-cardiac channel plots of a few Day-2 records. No ECG/BP values, no outcomes.
DOI 10.13026/m40k-4758, CC BY 4.0.
"""
from __future__ import annotations

import csv
import io
import re
import statistics
import tempfile
from pathlib import Path

import numpy as np
import requests

from scripts.cded_inventory import UA, parse_sha256sums
from scripts.dataset_structure import get_text

BASE = "https://physionet.org/files/cerebral-vasoreg-diabetes/1.0.0/"
DOC_KEYS = re.compile(r"autonom|neuropath|valsalva|orthostat|tilt|\bOH\b|marker|baseline|hypervent|rebreath", re.I)
CHANNELS = ("marker", "thermst", "flow_rate", "o2", "co2")


def table_stats(text, max_cols=30):
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[:3]
    out = []
    width = max(len(r) for r in rows)
    for c in range(min(width, max_cols)):
        vals = []
        for r in rows[1:]:
            if c < len(r):
                try:
                    vals.append(float(r[c]))
                except ValueError:
                    pass
        if len(vals) >= 5:
            out.append((c, len(vals), min(vals), statistics.median(vals), max(vals)))
        else:
            out.append((c, len(vals), None, None, None))
    return header, out, len(rows)


def plot_record(path, out_dir, session):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            r = session.get(BASE + path + ext, headers=UA, timeout=180)
            r.raise_for_status()
            (Path(tmp) / (name + ext)).write_bytes(r.content)
        header = wfdb.rdheader(str(Path(tmp) / name))
        idx = [i for i, n in enumerate(header.sig_name) if n.lower() in CHANNELS]
        rec = wfdb.rdrecord(str(Path(tmp) / name), channels=idx)
        step = int(round(rec.fs / 10))
        n = (rec.p_signal.shape[0] // step) * step
        data = np.nanmean(rec.p_signal[:n].reshape(-1, step, len(idx)), axis=1)
        t = np.arange(data.shape[0]) / 10 / 60
        fig, axes = plt.subplots(len(idx), 1, figsize=(15, 8), sharex=True)
        for j, ax in enumerate(axes):
            ax.plot(t, data[:, j], linewidth=0.4)
            ax.set_ylabel(rec.sig_name[j])
            ax.grid(alpha=0.3)
        axes[-1].set_xticks(np.arange(0, t[-1] + 1, 1))
        fig.suptitle(f"GE-71 {name} — non-cardiac channels only")
        fig.tight_layout()
        fig.savefig(Path(out_dir) / f"ge71_{name}.png", dpi=70)
        plt.close(fig)


def main():
    session = requests.Session()
    out = Path("reports/explore")
    out.mkdir(parents=True, exist_ok=True)
    qc = Path("qc")
    qc.mkdir(exist_ok=True)
    paths = parse_sha256sums(get_text(BASE + "SHA256SUMS.txt", session))
    lines = ["# GE-71 documentation and marker structure (no outcomes)", ""]
    for p in paths:
        low = p.lower()
        if "markers_per_subject" in low:
            header, stats, n = table_stats(get_text(BASE + p.replace(" ", "%20"), session))
            lines += [f"## {p} ({n} rows)", "", "Header rows:", "```"]
            lines += [" | ".join(h)[:900] for h in header[:2]]
            lines += ["```", "", "| column index | numeric values | min | median | max |", "|---:|---:|---:|---:|---:|"]
            lines += [f"| {c} | {k} | {a} | {m} | {b} |" for c, k, a, m, b in stats]
            lines.append("")
        elif "file_and_channels" in low or "files_and_channels" in low:
            rows = [r for r in csv.reader(io.StringIO(get_text(BASE + p.replace(" ", "%20"), session))) if any(c.strip() for c in r)]
            lines += [f"## {p}", "", "```"] + [" | ".join(c.strip() for c in r if c.strip())[:260] for r in rows[:110]] + ["```", ""]
        elif "data_dictionary" in low:
            rows = [r for r in csv.reader(io.StringIO(get_text(BASE + p.replace(" ", "%20"), session)))]
            hits = [" | ".join(c.strip() for c in r if c.strip())[:240] for r in rows if DOC_KEYS.search(" ".join(r))]
            lines += [f"## {p} — rows mentioning autonomic/protocol terms ({len(hits)})", "", "```"] + hits[:90] + ["```", ""]
    day2 = sorted(p[:-4] for p in paths if "head-up-tilt_day2" in p.lower() and p.lower().endswith(".hea"))
    day1 = sorted(p[:-4] for p in paths if "head-up-tilt_day1" in p.lower() and p.lower().endswith(".hea"))
    lines += [f"Day-2 record names (first 5): {[Path(p).name for p in day2[:5]]}",
              f"Day-1 record names (first 5): {[Path(p).name for p in day1[:5]]}"]
    for p in day2[:4] + day1[:2]:
        try:
            plot_record(p, qc, session)
        except Exception as err:  # noqa: BLE001
            lines.append(f"plot failed {Path(p).name}: {type(err).__name__}")
    (out / "GE71_DOCS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
