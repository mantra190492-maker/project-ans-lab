"""HRF-RES-001: is Costa-reference PIP stable when ECG resolution drops from 250 Hz to 125 Hz?

Why: SHHS visit-1 ECG was mostly recorded at 125 Hz (8 ms grid), visit 2 at 250 Hz.
SHHS-HRF-001 uses visit-1 PIP as its predictor, so PIP must survive 125 Hz.

Method: take human-annotated R peaks recorded at 250 Hz, compute PIP on the native
grid, re-grid the SAME beats to the nearest 8 ms sample (best case for a 125 Hz
detector: quantization only, no extra detector jitter), recompute, and compare.

Pre-specified decision rule (fixed in code BEFORE the first run on real data):
  PASS only if ALL hold for the primary metric (Costa PIP):
    1. Spearman rho(PIP_250, PIP_125) >= 0.90 across recordings
    2. |mean shift (PIP_125 - PIP_250)| <= 2.0 percentage points
    3. |Spearman rho(shift, log RMSSD)| <= 0.30  (bias must not depend on HRV level)
  Otherwise FAIL: 125 Hz PIP is not interchangeable with 250 Hz PIP.
The same rule is reported, unchanged, for the hard-inflection-only rate.

Data sources (public, no restricted data):
  gudb     - Glasgow University ECG database (Howell & Porr), 25 healthy adults,
             250 Hz, chest-strap R-peak annotations, CC BY 3.0,
             DOI 10.5281/zenodo.10925419. Fetched from the GitHub mirror.
  fantasia - PhysioNet Fantasia v1.0.0 (250 Hz, reviewed beat annotations).
             Requires physionet.org network access (e.g. GitHub Actions).

Scope: measurement robustness only. Not a clinical, ageing or outcome result.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

from anslab.hrf_costa_reference import costa_fragmentation_from_peaks

NATIVE_HZ = 250.0
LOW_HZ = 125.0
RULE = {"min_spearman": 0.90, "max_abs_mean_shift_pp": 2.0, "max_abs_shift_rmssd_rho": 0.30}
GUDB_RAW = "https://raw.githubusercontent.com/berndporr/ECG-GUDB/master/docs/experiment_data/"
GUDB_TASKS = ("sitting", "maths")  # low-motion tasks only
FANTASIA = "https://physionet.org/files/fantasia/1.0.0/"
FANTASIA_RECORDS = [f"f{g}{a}{i:02d}" for g in (1, 2) for a in ("y", "o") for i in range(1, 11)]
FANTASIA_WINDOW_S = (60, 60 + 30 * 60)  # 30 minutes after the first minute


TIE_RULES = ("random", "floor", "half_even")


def regrid(times_s, hz, tie="random", seed=0):
    """Snap peak times to the nearest sample of a coarser ECG grid.

    Every odd 250 Hz sample sits exactly halfway between two 125 Hz samples, so the
    tie rule matters. A real 125 Hz detector picks whichever neighbour has the larger
    amplitude, which is effectively random; 'floor' and 'half_even' (Python round)
    are reported as sensitivity analyses.
    """
    rng = np.random.default_rng(seed)
    out = []
    for t in times_s:
        x = t * hz
        lo = math.floor(x + 1e-9)
        frac = x - lo
        if abs(frac - 0.5) < 1e-6:
            if tie == "floor":
                k = lo
            elif tie == "half_even":
                k = lo if lo % 2 == 0 else lo + 1
            else:
                k = lo + int(rng.random() < 0.5)
        else:
            k = round(x)
        out.append(k / hz)
    return out


def rmssd_ms(times_s, labels):
    rr = [(times_s[i] - times_s[i - 1], labels[i - 1] == 1 and labels[i] == 1)
          for i in range(1, len(times_s))]
    diffs = [1000 * (rr[i][0] - rr[i - 1][0]) for i in range(1, len(rr))
             if rr[i][1] and rr[i - 1][1] and 0.3 < rr[i][0] < 1.8 and 0.3 < rr[i - 1][0] < 1.8]
    if len(diffs) < 30:
        raise ValueError("Too few sinus NN pairs for RMSSD")
    return math.sqrt(sum(d * d for d in diffs) / len(diffs))


def hrf(times_s, labels, hz):
    out = costa_fragmentation_from_peaks(times_s, labels, sampling_hz=hz)
    windows = out["n_valid_three_interval_windows"]
    return {
        "pip": out["pip_percent"],
        "hard_rate": 100.0 * out["n_hard_inflections"] / windows if windows else float("nan"),
        "soft_share": 100.0 * out["n_soft_inflections"] / out["n_inflection_points"],
    }


def compare(record_id, times_s, labels, meta=None, tie="random"):
    native = hrf(times_s, labels, NATIVE_HZ)
    low = hrf(regrid(times_s, LOW_HZ, tie=tie, seed=zlib.crc32(record_id.encode())), labels, LOW_HZ)
    return {
        "record": record_id, **(meta or {}),
        "n_beats": len(times_s),
        "rmssd_ms": rmssd_ms(times_s, labels),
        "pip_250": native["pip"], "pip_125": low["pip"],
        "pip_shift_pp": low["pip"] - native["pip"],
        "hard_250": native["hard_rate"], "hard_125": low["hard_rate"],
        "hard_shift_pp": low["hard_rate"] - native["hard_rate"],
        "soft_share_250": native["soft_share"], "soft_share_125": low["soft_share"],
    }


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def evaluate(rows, a, b, shift):
    x = [r[a] for r in rows]
    y = [r[b] for r in rows]
    s = [r[shift] for r in rows]
    lr = [math.log(r["rmssd_ms"]) for r in rows]
    result = {
        "n_recordings": len(rows),
        "spearman_250_vs_125": spearman(x, y),
        "mean_shift_pp": statistics.fmean(s),
        "sd_shift_pp": statistics.stdev(s) if len(s) > 1 else float("nan"),
        "min_shift_pp": min(s), "max_shift_pp": max(s),
        "spearman_shift_vs_log_rmssd": spearman(s, lr),
    }
    result["checks"] = {
        "rank_agreement": result["spearman_250_vs_125"] >= RULE["min_spearman"],
        "small_mean_shift": abs(result["mean_shift_pp"]) <= RULE["max_abs_mean_shift_pp"],
        "shift_independent_of_hrv": abs(result["spearman_shift_vs_log_rmssd"]) <= RULE["max_abs_shift_rmssd_rho"],
    }
    result["decision"] = "PASS" if all(result["checks"].values()) else "FAIL"
    return result


def artifact_labels(times_s, tolerance=0.30, half_window=5):
    rr = np.diff(np.asarray(times_s, dtype=float))
    labels = [1] * len(times_s)
    for i, value in enumerate(rr):
        lo, hi = max(0, i - half_window), min(len(rr), i + half_window + 1)
        ref = float(np.median(rr[lo:hi]))
        if abs(value - ref) > tolerance * ref:
            labels[i + 1] = 3
    return labels


def load_gudb(local_dir=None):
    rows, skipped = [], []
    for subject in range(25):
        for task in GUDB_TASKS:
            rid = f"gudb_s{subject:02d}_{task}"
            text = None
            for ann in ("annotation_cs.tsv", "annotation_cables.tsv"):
                rel = f"subject_{subject:02d}/{task}/{ann}"
                try:
                    if local_dir:
                        path = Path(local_dir) / rel
                        if path.exists():
                            text = path.read_text()
                    else:
                        resp = requests.get(GUDB_RAW + rel, timeout=30)
                        if resp.status_code == 200:
                            text = resp.text
                except requests.RequestException:
                    text = None
                if text:
                    source = ann
                    break
            if not text:
                skipped.append({"record": rid, "reason": "no annotation file"})
                continue
            samples = sorted({int(float(v)) for v in text.split() if v.strip()})
            times = [s / NATIVE_HZ for s in samples]
            # GUDB annotates R peaks without beat typing. Flag beats ending an interval
            # >30% away from the local median (missed/extra beat or ectopy) as non-sinus,
            # so the reference algorithm breaks segments there. Identical labels are used
            # at both resolutions, so this cannot bias the paired comparison.
            labels = artifact_labels(times)
            rows.append((rid, times, labels, {"task": task, "annotation": source,
                                              "flagged_beats": labels.count(3)}))
    return rows, skipped


FANTASIA_LABELS = {"N": 1, "V": 2}
FANTASIA_BEATS = set("NLRBAaJSVreEj/FfQ")


def parse_wfdb_annotation(samples, symbols, fs):
    pairs = [(int(s), sym) for s, sym in zip(samples, symbols) if sym in FANTASIA_BEATS]
    times = [s / fs for s, _ in pairs]
    labels = [FANTASIA_LABELS.get(sym, 3) for _, sym in pairs]
    return times, labels


def load_fantasia():
    import wfdb
    rows, skipped = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for rec in FANTASIA_RECORDS:
            try:
                for ext in (".hea", ".ecg"):
                    resp = requests.get(FANTASIA + rec + ext, timeout=60)
                    resp.raise_for_status()
                    if len(resp.content) > 2_000_000:
                        raise ValueError("Annotation larger than expected")
                    (Path(tmp) / (rec + ext)).write_bytes(resp.content)
                header = wfdb.rdheader(str(Path(tmp) / rec))
                if float(header.fs) != NATIVE_HZ:
                    raise ValueError(f"Unexpected sampling rate {header.fs}")
                ann = wfdb.rdann(str(Path(tmp) / rec), "ecg")
                lo, hi = (int(x * NATIVE_HZ) for x in FANTASIA_WINDOW_S)
                keep = [(s, sym) for s, sym in zip(ann.sample, ann.symbol) if lo <= s < hi]
                times, labels = parse_wfdb_annotation([s for s, _ in keep], [y for _, y in keep], NATIVE_HZ)
                age = "young_21_34" if "y" in rec else "older_68_85"
                rows.append((rec, times, labels, {"age_group": age}))
            except Exception as err:  # noqa: BLE001 - every exclusion is reported
                skipped.append({"record": rec, "reason": f"{type(err).__name__}: {str(err)[:160]}"})
    return rows, skipped


def render(source, by_tie, skipped, overall):
    rows = by_tie["random"]["rows"]
    lines = [
        f"# HRF-RES-001 — PIP stability from 250 Hz to 125 Hz ({source})", "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}", "",
        "**Question:** SHHS visit-1 ECG was mostly 125 Hz. Is Costa-reference PIP measured at 125 Hz "
        "interchangeable with PIP at 250 Hz on the same heartbeats?", "",
        "Same human-annotated beats, re-gridded to the nearest 8 ms sample. This is the BEST case "
        "for a 125 Hz recording: no extra R-peak detection jitter is added.", "",
        "Pre-specified rule: PASS only if Spearman ≥ 0.90, |mean shift| ≤ 2.0 pp and "
        "|Spearman(shift, log RMSSD)| ≤ 0.30. Beats exactly between two 125 Hz samples need a tie rule; "
        "a metric passes overall only if it passes under all three rules.", "",
        f"**Overall: Costa PIP {overall['primary']}; hard-inflection rate {overall['hard']}.**", "",
        "| Metric | Tie rule | Recordings | Spearman 250 vs 125 | Mean shift (pp) | Shift range (pp) | Shift vs log RMSSD (ρ) | Decision |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for key, name in (("primary", "Costa PIP"), ("hard", "Hard-inflection rate")):
        for tie in TIE_RULES:
            r = by_tie[tie][key]
            lines.append(
                f"| {name} | {tie} | {r['n_recordings']} | {r['spearman_250_vs_125']:.2f} | {r['mean_shift_pp']:+.1f} "
                f"| {r['min_shift_pp']:+.1f} to {r['max_shift_pp']:+.1f} | {r['spearman_shift_vs_log_rmssd']:+.2f} | {r['decision']} |")
    lines += ["", "Mean share of inflections that are 'soft' (a zero NN change): "
              f"{statistics.fmean(r['soft_share_250'] for r in rows):.1f}% at 250 Hz → "
              f"{statistics.fmean(r['soft_share_125'] for r in rows):.1f}% at 125 Hz.", ""]
    lines += ["## Per recording (random tie rule)", "",
              "| Record | Beats | RMSSD (ms) | PIP 250 | PIP 125 | Shift | Hard 250 | Hard 125 |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['record']} | {r['n_beats']} | {r['rmssd_ms']:.1f} | {r['pip_250']:.1f} | {r['pip_125']:.1f} "
                     f"| {r['pip_shift_pp']:+.1f} | {r['hard_250']:.1f} | {r['hard_125']:.1f} |")
    if skipped:
        lines += ["", "## Excluded (reported, not hidden)", ""] + [f"- {s['record']}: {s['reason']}" for s in skipped]
    lines += ["", "## Limits", "",
              "- Quantization only; a real 125 Hz detector adds timing jitter, so real-world shifts are likely larger.",
              "- GUDB windows are 2 minutes (~140 beats), so absolute PIP is noisy; the comparison is paired on identical beats.",
              "- GUDB beats are not rhythm-typed; the reference algorithm's NN bounds are the only beat filter.",
              "- Healthy adults only. Not a clinical, ageing or outcome result."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("gudb", "fantasia"), default="gudb")
    parser.add_argument("--local-dir", help="Local GUDB experiment_data directory (optional)")
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()
    raw, skipped = load_gudb(args.local_dir) if args.source == "gudb" else load_fantasia()
    by_tie = {}
    for tie in TIE_RULES:
        rows = []
        for rid, times, labels, meta in raw:
            try:
                rows.append(compare(rid, times, labels, meta, tie=tie))
            except ValueError as err:
                if tie == TIE_RULES[0]:
                    skipped.append({"record": rid, "reason": str(err)})
        if len(rows) < 10:
            raise SystemExit(f"Too few usable recordings: {len(rows)}")
        by_tie[tie] = {"rows": rows,
                       "primary": evaluate(rows, "pip_250", "pip_125", "pip_shift_pp"),
                       "hard": evaluate(rows, "hard_250", "hard_125", "hard_shift_pp")}
    overall = {m: ("PASS" if all(by_tie[t][m]["decision"] == "PASS" for t in TIE_RULES) else "FAIL")
               for m in ("primary", "hard")}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"HRF_RESOLUTION_GATE_{args.source.upper()}"
    payload = {"study": "HRF-RES-001", "source": args.source, "rule": RULE,
               "overall_decision_all_tie_rules": overall,
               "by_tie_rule": {t: {"primary_costa_pip": v["primary"], "hard_inflection_rate": v["hard"]}
                               for t, v in by_tie.items()},
               "records_random_tie": by_tie["random"]["rows"], "excluded": skipped,
               "generated_utc": datetime.now(timezone.utc).isoformat()}
    (out / f"{stem}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out / f"{stem}.md").write_text(render(args.source, by_tie, skipped, overall), encoding="utf-8")
    print(json.dumps(payload["by_tie_rule"], indent=1)[:3000])
    print("OVERALL", overall)


if __name__ == "__main__":
    main()
