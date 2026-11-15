"""Synthetic-only, reproducible demonstration of watch sensor-rate/QC constraints.

Usage: python -m wearable.experiments.watch_sim_001
This does NOT use patient data, a real Galaxy Watch, or disease labels.
"""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import numpy as np

from wearable.simulator import simulate_continuous, qc_and_features, load_profile


def synthetic_wesad_shaped_inputs(duration_seconds: int = 180) -> dict:
    """Generate fake wrist signals with WESAD input rates (no real subject data)."""
    ppg_t = np.arange(64 * duration_seconds) / 64
    eda_t = np.arange(4 * duration_seconds) / 4
    temp_t = np.arange(4 * duration_seconds) / 4
    acc_t = np.arange(32 * duration_seconds) / 32
    rng = np.random.default_rng(34)
    # Arbitrary waveform, not simulated clinical pathology or faithful device optics.
    ppg = .8 * np.sin(2 * np.pi * 1.2 * ppg_t) + .2 * np.sin(2 * np.pi * 2.4 * ppg_t)
    eda = 1.5 + .15 * np.sin(2 * np.pi * .012 * eda_t) + .45 * np.exp(-np.maximum(eda_t-80,0)/12) * (eda_t>=80)
    temp = 33 + .08 * np.sin(2 * np.pi * .002 * temp_t)
    acc = np.column_stack((.01*rng.normal(size=len(acc_t)), .01*rng.normal(size=len(acc_t)),
                           1+.01*rng.normal(size=len(acc_t))))
    # Synthetic movement during two periods, exaggerated for artifact demo.
    move = ((acc_t > 40) & (acc_t < 55)) | ((acc_t > 130) & (acc_t < 145))
    acc[move,:2] += .35*rng.normal(size=(int(move.sum()),2))
    return {"ppg":(ppg,64), "eda":(eda,4), "acc":(acc,32), "temperature":(temp,4)}


def run() -> dict:
    profile = load_profile()
    session=simulate_continuous(synthetic_wesad_shaped_inputs(),temperature_output_hz=1,seed=100,
                                dropout_probability=.015,ppg_motion_fraction=.25)
    result = qc_and_features(session)
    # Do not serialize raw traces, and do not make up HRV, CASS or disease labels.
    return {"experiment_id":"WATCH-SIM-001", "date_utc":datetime.now(timezone.utc).isoformat(),
            "input":"DETERMINISTIC_SYNTHETIC_WRIST_CHANNELS_ONLY", "device_profile":profile["name"],
            "vendor_equivalence_tested":False,"independent_clinical_reference":False,
            "recorded_subjects_used":0,"watch_devices_used":0,"results":result,
            "warnings":session.warnings}


def main():
    payload=run()
    root=Path(__file__).resolve().parents[1]/"reports"
    root.mkdir(parents=True,exist_ok=True)
    (root/"WATCH_SIM_001.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2))


if __name__=="__main__":
    main()
