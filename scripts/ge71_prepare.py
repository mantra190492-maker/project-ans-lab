"""GE71-ANS-001 preparation: summary-table column names and blind rest-window detection.

Reads NO ECG and NO blood pressure. Uses only the CO2 (capnography) and marker
channels of the Day-2 lab records to find the quiet supine rest period that precedes
the first Valsalva (mask-off gap), and lists summary-table column NAMES with
non-missing counts (no values). Output feeds the frozen analysis plan.
"""
from __future__ import annotations

import csv
import io
import json
import re
import tempfile
from pathlib import Path

import numpy as np
import requests

from scripts.cded_inventory import UA, parse_sha256sums
from scripts.dataset_structure import get_text

BASE = "https://physionet.org/files/cerebral-vasoreg-diabetes/1.0.0/"
SUMMARY = "Data_Description/GE-71_Data_Summary_Table.csv"
ENV_HZ = 10
MISSING = {"", "NA", "NAN", "N/A", ".", "-", "NONE", "NULL"}


def rest_window(co2, hz=ENV_HZ, settle_s=30, guard_s=15, max_s=300, min_s=180):
    """Quiet-breathing window before the first sustained no-breathing gap, from CO2 only.

    Returns dict(status, start_s, end_s, gap_s, breaths_per_min).
    """
    x = np.asarray(co2, dtype=float)
    win = 10 * hz
    if len(x) < 4 * 60 * hz:
        return {"status": "too_short"}
    # rolling 10-s range (breathing swings CO2 between ~0 and end-tidal each breath)
    n = len(x) - win + 1
    shape = (n, win)
    strides = (x.strides[0], x.strides[0])
    view = np.lib.stride_tricks.as_strided(x, shape=shape, strides=strides)
    rng = view.max(axis=1) - view.min(axis=1)
    typical = float(np.percentile(rng[: min(n, 5 * 60 * hz)], 75))
    if not np.isfinite(typical) or typical <= 0:
        return {"status": "no_capnogram"}
    breathing = rng >= 0.5 * typical
    if not breathing.any():
        return {"status": "no_capnogram"}
    t0 = int(np.argmax(breathing))                      # breathing established
    quiet = rng < 0.2 * typical
    after = np.flatnonzero(quiet[t0 + 60 * hz:])
    if len(after) == 0:
        return {"status": "no_gap_found", "breathing_from_s": t0 / hz}
    gap = t0 + 60 * hz + int(after[0])
    end = gap - guard_s * hz
    start = max(t0 + settle_s * hz, end - max_s * hz)
    if end - start < min_s * hz:
        return {"status": "rest_too_short", "gap_s": gap / hz, "available_s": max(0, (end - start) / hz)}
    seg = x[start:end]
    thr = seg.min() + 0.5 * (seg.max() - seg.min())
    crossings = np.flatnonzero((seg[1:] >= thr) & (seg[:-1] < thr))
    bpm = len(crossings) / ((end - start) / hz / 60)
    status = "ok" if 6 <= bpm <= 30 else "breathing_rate_out_of_range"
    return {"status": status, "start_s": start / hz, "end_s": end / hz, "gap_s": gap / hz,
            "breaths_per_min": round(float(bpm), 1)}


def marker_times(marker, fs, min_gap_s=1.0):
    m = np.asarray(marker, dtype=float)
    level = np.nanmax(np.abs(m))
    if not np.isfinite(level) or level < 0.05:
        return []
    on = np.abs(m) > 0.3 * level
    edges = (np.flatnonzero(on[1:] & ~on[:-1]) + 1) / fs
    out = []
    for t in edges:
        if not out or t - out[-1] >= min_gap_s:
            out.append(float(t))
    return out


def load_channels(path, names, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            for attempt in range(4):
                r = session.get(BASE + path + ext, headers=UA, timeout=300)
                if r.status_code == 200:
                    break
            r.raise_for_status()
            (Path(tmp) / (name + ext)).write_bytes(r.content)
        header = wfdb.rdheader(str(Path(tmp) / name))
        idx = [i for i, n in enumerate(header.sig_name) if n.lower() in names]
        rec = wfdb.rdrecord(str(Path(tmp) / name), channels=idx)
        return {rec.sig_name[j].lower(): rec.p_signal[:, j] for j in range(len(idx))}, float(rec.fs)


def envelope(x, fs, hz=ENV_HZ):
    step = int(round(fs / hz))
    n = (len(x) // step) * step
    return np.nanmean(np.asarray(x[:n], dtype=float).reshape(-1, step), axis=1)


def summary_columns(text):
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip() for h in rows[0]]
    counts = []
    for c, name in enumerate(header):
        k = sum(1 for r in rows[1:] if c < len(r) and r[c].strip().upper() not in MISSING)
        counts.append((c, name, k))
    ids = [r[0].strip() for r in rows[1:] if r and re.fullmatch(r"[sS]\d{3,5}", r[0].strip())]
    return counts, ids, len(rows) - 1


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    session = requests.Session()
    out = Path("reports/explore")
    out.mkdir(parents=True, exist_ok=True)
    qc = Path("qc")
    qc.mkdir(exist_ok=True)

    counts, ids, nrows = summary_columns(get_text(BASE + SUMMARY, session))
    lines = ["# GE-71 summary table — column names and non-missing counts (no values)", "",
             f"Data rows: {nrows}; rows whose first cell looks like a subject ID: {len(ids)}", "",
             "| # | column | non-missing |", "|---:|---|---:|"]
    lines += [f"| {c} | {name[:80]} | {k} |" for c, name, k in counts]
    (out / "GE71_SUMMARY_COLUMNS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    paths = parse_sha256sums(get_text(BASE + "SHA256SUMS.txt", session))
    day2 = sorted(p[:-4] for p in paths if "head-up-tilt_day2" in p.lower() and p.lower().endswith(".hea"))
    results, traces = [], []
    for p in day2:
        rid = Path(p).name
        try:
            sig, fs = load_channels(p, ("co2", "marker"), session)
            env = envelope(sig["co2"], fs)
            res = rest_window(env)
            marks = marker_times(sig.get("marker", []), fs) if "marker" in sig else []
            res.update({"record": rid, "fs": fs, "duration_min": round(len(env) / ENV_HZ / 60, 1),
                        "n_markers": len(marks), "marker_times_s": [round(t, 1) for t in marks[:25]]})
            if res.get("gap_s") is not None and marks:
                res["gap_to_nearest_marker_s"] = round(min(abs(res["gap_s"] - t) for t in marks), 1)
            traces.append((rid, env[: 15 * 60 * ENV_HZ], res, marks))
        except Exception as err:  # noqa: BLE001
            res = {"record": rid, "status": f"load_failed:{type(err).__name__}"}
        results.append(res)
        print(rid, res.get("status"), flush=True)

    status = {}
    for r in results:
        status[r["status"]] = status.get(r["status"], 0) + 1
    with_ids = {i.lower() for i in ids}
    ok_in_table = sum(1 for r in results if r["status"] == "ok" and r["record"][:5].lower() in with_ids)
    (out / "GE71_REST_WINDOWS.json").write_text(json.dumps(
        {"study": "GE71-ANS-001 preparation", "n_day2_records": len(day2), "status_counts": status,
         "ok_and_in_summary_table": ok_in_table, "windows": results}, indent=1) + "\n", encoding="utf-8")

    for sheet in range(0, len(traces), 30):
        chunk = traces[sheet:sheet + 30]
        fig, axes = plt.subplots(5, 6, figsize=(24, 14))
        for ax, (rid, env, res, marks) in zip(axes.ravel(), chunk):
            t = np.arange(len(env)) / ENV_HZ / 60
            ax.plot(t, env, linewidth=0.3, color="k")
            if res.get("start_s") is not None:
                ax.axvspan(res["start_s"] / 60, res["end_s"] / 60, color="green", alpha=0.3)
            if res.get("gap_s") is not None:
                ax.axvline(res["gap_s"] / 60, color="red", linewidth=1)
            for m in marks:
                if m / 60 <= 15:
                    ax.axvline(m / 60, color="blue", linewidth=0.5, ymax=0.15)
            ax.set_title(f"{rid} {res['status']}", fontsize=8)
            ax.set_xlim(0, 15)
            ax.tick_params(labelsize=6)
        for ax in axes.ravel()[len(chunk):]:
            ax.axis("off")
        fig.suptitle("GE-71 Day 2: CO2 only. Green = rest window, red = first no-breathing gap, blue ticks = markers")
        fig.tight_layout()
        fig.savefig(qc / f"ge71_rest_windows_{sheet // 30 + 1}.png", dpi=60)
        plt.close(fig)


if __name__ == "__main__":
    main()
