"""CDED-ANS-001: plots of NON-CARDIAC channels only, for blind protocol segmentation.

Per Amendment 1, segmentation may use airflow / CO2 / O2 / marker only. This script
plots those channels (never ECG, arterial pressure or TCD) for a fixed sample of
lab records so segment boundaries can be designed and reviewed without seeing any
heart-rate or blood-pressure information.
"""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import numpy as np
import requests

from scripts.cded_inventory import BASE, classify_record, fetch_text
from scripts.cded_segments import download

CHANNELS = ("marker", "thermst", "flow_rate", "o2", "co2")
PLOT_HZ = 10


def load_resp(rec_path, session):
    import wfdb
    with tempfile.TemporaryDirectory() as tmp:
        name, directory = Path(rec_path).name, str(Path(rec_path).parent)
        for ext in (".hea", ".dat"):
            download(f"{directory}/{name}{ext}", Path(tmp) / f"{name}{ext}", session)
        header = wfdb.rdheader(str(Path(tmp) / name))
        idx = [i for i, n in enumerate(header.sig_name) if n.lower() in CHANNELS]
        rec = wfdb.rdrecord(str(Path(tmp) / name), channels=idx)
        step = int(round(rec.fs / PLOT_HZ))
        n = (rec.p_signal.shape[0] // step) * step
        data = np.nanmean(rec.p_signal[:n].reshape(-1, step, len(idx)), axis=1)
        return {rec.sig_name[j].lower(): data[:, j] for j in range(len(idx))}


def plot(rec_path, sig, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = [c for c in CHANNELS if c in sig]
    t = np.arange(len(sig[names[0]])) / PLOT_HZ / 60
    fig, axes = plt.subplots(len(names), 1, figsize=(15, 8), sharex=True)
    for ax, name in zip(axes, names):
        ax.plot(t, sig[name], linewidth=0.4)
        ax.set_ylabel(name)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("minutes")
    axes[-1].set_xticks(np.arange(0, t[-1] + 1, 2))
    fig.suptitle(f"{Path(rec_path).name} — non-cardiac channels only")
    fig.tight_layout()
    fig.savefig(Path(out_dir) / f"{Path(rec_path).name}.png", dpi=70)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-visit", type=int, default=5)
    parser.add_argument("--out", default="qc")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    records = [r.strip() for r in fetch_text("RECORDS", session).splitlines() if r.strip()]
    sample = ([r for r in records if classify_record(r) == "labview_visit2"][:args.per_visit]
              + [r for r in records if classify_record(r) == "labview_visit8"][:args.per_visit])
    for rec in sample:
        try:
            plot(rec, load_resp(rec, session), out)
            print("ok", rec, flush=True)
        except Exception as err:  # noqa: BLE001
            print("fail", rec, type(err).__name__, flush=True)


if __name__ == "__main__":
    main()
