"""POOL-VR-001 stage A: does an automated Valsalva ratio agree with the lab's values in GE-71?

Outcome-vs-outcome only: no fragmentation or HRV marker is computed here.
Aggregates and anonymous scatter plots only.
"""
from __future__ import annotations

import csv
import io
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from scipy import stats

from scripts.cded_inventory import UA, parse_sha256sums
from scripts.dataset_structure import get_text
from scripts.ge71_analysis import number, subject_key
from scripts.ge71_prepare import BASE, SUMMARY, envelope, marker_times
from scripts.vr_core import ENV_HZ, detect_all_beats, gap_based_vr, mask_off_gaps, template_quality, valsalva_ratio

MARKERS_DAY1 = "Data_Description/GE-71_Head-up-tilt-Day1_Markers_per_subject.csv"
PASS_RHO, PASS_N = 0.60, 20


def load_record(path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name = Path(path).name
        for ext in (".hea", ".dat"):
            for _ in range(4):
                r = session.get(BASE + path + ext, headers=UA, timeout=300)
                if r.status_code == 200:
                    break
            r.raise_for_status()
            (Path(tmp) / (name + ext)).write_bytes(r.content)
        header = wfdb.rdheader(str(Path(tmp) / name))
        names = [n.lower() for n in header.sig_name]
        want = [names.index(c) for c in ("ecg", "co2", "marker") if c in names]
        rec = wfdb.rdrecord(str(Path(tmp) / name), channels=want)
        return {names[i]: rec.p_signal[:, j] for j, i in enumerate(want)}, float(rec.fs)


def marker_based_vr(beat_times, pulses, ordinals):
    values = []
    for a, b in ordinals:
        if a and b and 1 <= a <= len(pulses) and 1 <= b <= len(pulses) and pulses[b - 1] > pulses[a - 1]:
            v = valsalva_ratio(beat_times, pulses[a - 1], pulses[b - 1] + 5)
            if v is not None:
                values.append(v)
    return max(values) if values else None


def agreement(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 8:
        return {"n": len(pairs)}
    x, y = np.array(pairs).T
    rho, p = stats.spearmanr(x, y)
    return {"n": len(pairs), "spearman": float(rho), "p": float(p), "median_abs_diff": float(np.median(np.abs(x - y))),
            "bias_auto_minus_ref": float(np.mean(x - y))}


def main():
    session = requests.Session()
    out, qc = Path("reports/explore"), Path("qc")
    out.mkdir(parents=True, exist_ok=True)
    qc.mkdir(exist_ok=True)

    table = list(csv.reader(io.StringIO(get_text(BASE + SUMMARY, session))))
    header = [h.strip() for h in table[0]]
    lab = {}
    for r in table[1:]:
        k = subject_key(r[header.index("SUBJECT NUMBER")])
        if k:
            lab[k] = (number(r[header.index("VM RATIO")]), number(r[header.index("VMRatio2")]))
    mk = list(csv.reader(io.StringIO(get_text(BASE + MARKERS_DAY1, session))))
    ordinals = {}
    for r in mk[1:]:
        k = subject_key(r[0]) if r else None
        if k:
            vals = [int(number(c) or 0) for c in r[2:13]] + [0] * 11
            ordinals[k] = [(vals[3], vals[4]), (vals[5], vals[6]), (vals[7], vals[8])]

    paths = parse_sha256sums(get_text(BASE + "SHA256SUMS.txt", session))
    res = {}
    stats_rows = []
    for day, tag in (("day1", "head-up-tilt_day1"), ("day2", "head-up-tilt_day2")):
        for p in sorted(x[:-4] for x in paths if tag in x.lower() and x.lower().endswith(".hea")):
            k = subject_key(Path(p).name)
            entry = res.setdefault(k, {})
            try:
                sig, fs = load_record(p, session)
                peaks = detect_all_beats(sig["ecg"], fs)
                tq = template_quality(sig["ecg"], peaks, fs)
                beats = peaks / fs
                gaps = mask_off_gaps(envelope(sig["co2"], fs, ENV_HZ)) if "co2" in sig else []
                vr, n_used = gap_based_vr(beats, gaps) if tq >= 0.8 else (None, 0)
                entry[f"gap_{day}"] = vr
                stats_rows.append({"day": day, "template_quality": tq, "n_gaps": len(gaps), "n_gaps_used": n_used,
                                   "n_beats": int(len(beats))})
                if day == "day1" and "marker" in sig and k in ordinals and tq >= 0.8:
                    entry["marker_day1"] = marker_based_vr(beats, marker_times(sig["marker"], fs), ordinals[k])
                status = "ok"
            except Exception as err:  # noqa: BLE001
                status = f"error_{type(err).__name__}"
            print(day, Path(p).name, status, flush=True)

    keys = sorted(res)
    col = lambda name: [res[k].get(name) for k in keys]  # noqa: E731
    lab1 = [lab.get(k, (None, None))[0] if (lab.get(k, (None, None))[0] or 0) >= 0.9 else None for k in keys]
    lab2 = [lab.get(k, (None, None))[1] if (lab.get(k, (None, None))[1] or 0) >= 0.9 else None for k in keys]
    comp = {
        "gap_day2_vs_lab_VM_RATIO": agreement(col("gap_day2"), lab1),
        "gap_day1_vs_lab_VM_RATIO": agreement(col("gap_day1"), lab1),
        "marker_day1_vs_lab_VM_RATIO": agreement(col("marker_day1"), lab1),
        "gap_day2_vs_lab_VMRatio2": agreement(col("gap_day2"), lab2),
        "marker_day1_vs_lab_VMRatio2": agreement(col("marker_day1"), lab2),
        "lab_VM_RATIO_vs_lab_VMRatio2": agreement(lab1, lab2),
        "gap_day2_vs_marker_day1": agreement(col("gap_day2"), col("marker_day1")),
        "gap_day1_vs_marker_day1": agreement(col("gap_day1"), col("marker_day1")),
    }
    def passes(c):
        return c.get("n", 0) >= PASS_N and c.get("spearman", -1) >= PASS_RHO
    gap_pass = passes(comp["gap_day2_vs_lab_VM_RATIO"]) or passes(comp["gap_day1_vs_lab_VM_RATIO"])
    q = lambda v: [round(float(np.percentile(v, p)), 2) for p in (10, 25, 50, 75, 90)] if len(v) else None  # noqa: E731
    desc = {}
    for day in ("day1", "day2"):
        rows = [s for s in stats_rows if s["day"] == day]
        desc[day] = {"records": len(rows), "template_quality_p10_25_50_75_90": q([s["template_quality"] for s in rows]),
                     "records_with_gap": sum(s["n_gaps"] > 0 for s in rows), "gaps_per_record_quantiles": q([s["n_gaps"] for s in rows]),
                     "records_with_vr": sum(s["n_gaps_used"] > 0 for s in rows)}
    desc["value_quantiles"] = {name: q([v for v in col(name) if v is not None]) for name in ("gap_day1", "gap_day2", "marker_day1")}
    desc["value_quantiles"]["lab_VM_RATIO"] = q([v for v in lab1 if v is not None])
    payload = {"study": "POOL-VR-001 stage A", "generated_utc": datetime.now(timezone.utc).isoformat(),
               "pass_rule": {"spearman_min": PASS_RHO, "n_min": PASS_N}, "gap_based_validated": bool(gap_pass),
               "agreement": comp, "descriptive": desc}
    (out / "POOL_VR_001_STAGE_A.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    lines = ["# POOL-VR-001 stage A — automated vs lab Valsalva ratio (GE-71)", "", f"Generated UTC: {payload['generated_utc']}", "",
             f"**Gap-based automated ratio validated: {'YES' if gap_pass else 'NO'}** (rule: Spearman ≥ {PASS_RHO} in ≥ {PASS_N} people)", "",
             "| Comparison | n | Spearman | Median abs diff | Bias |", "|---|---:|---:|---:|---:|"]
    for name, c in comp.items():
        lines.append(f"| {name.replace('_', ' ')} | {c.get('n')} | {c.get('spearman', float('nan')):.2f} | "
                     f"{c.get('median_abs_diff', float('nan')):.2f} | {c.get('bias_auto_minus_ref', float('nan')):+.2f} |")
    lines += ["", "```", json.dumps(desc, indent=1), "```"]
    (out / "POOL_VR_001_STAGE_A.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (name, ref, label) in zip(axes, (("gap_day2", lab1, "lab VM RATIO"), ("marker_day1", lab1, "lab VM RATIO"),
                                             ("gap_day2", col("marker_day1"), "marker-based day 1"))):
        pairs = [(a, b) for a, b in zip(col(name), ref) if a is not None and b is not None]
        if pairs:
            a, b = np.array(pairs).T
            ax.scatter(b, a, s=22)
            lim = [0.9, max(a.max(), b.max()) + 0.1]
            ax.plot(lim, lim, "k--", linewidth=0.6)
        ax.set_xlabel(label); ax.set_ylabel(f"automated: {name}")
    fig.tight_layout()
    fig.savefig(qc / "pool_vr_stage_a.png", dpi=80)
    print(json.dumps({"validated": gap_pass, "agreement": comp}, indent=1))


if __name__ == "__main__":
    main()
