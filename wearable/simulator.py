"""Wrist acquisition proxy (L1/L2). NOT a Samsung device firmware emulator.

All inputs must be recorded wrist streams from ONE participant or explicit synthetic
streams. Never manufacture ANS disease labels or merge people into 'patients'.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import json

import numpy as np
from scipy.signal import resample_poly

PROFILE_PATH = Path(__file__).resolve().parent / "profiles" / "galaxy_watch8_research.json"
TARGET_HZ = {"ppg": 25, "acc": 25, "eda": 1}


@dataclass(frozen=True)
class Stream:
    hz: float
    samples: np.ndarray
    source_hz: float
    origin: str
    metadata: dict

    @property
    def coverage(self) -> float:
        return float(np.isfinite(self.samples).mean()) if self.samples.size else 0.0


@dataclass(frozen=True)
class WatchStreams:
    streams: dict[str, Stream]
    duration_seconds: float
    mode: str
    warnings: tuple[str, ...]


def load_profile() -> dict:
    with PROFILE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def downsample_recording(samples, source_hz: float, target_hz: float):
    """Anti-alias resample of a continuous recording, preserving channel axes.

    No claim is made that 25-Hz WESAD BVP matches Samsung optical hardware.
    Missing data must be resolved in the *source* with QC before resampling; this
    function refuses to interpolate NaN artifacts into apparently valid signals.
    """
    x = np.asarray(samples, dtype=float)
    if x.ndim not in (1, 2) or len(x) < 4:
        raise ValueError("Expected nonempty one- or multi-channel time series")
    if not np.isfinite(x).all():
        raise ValueError("Source contains missing/nonfinite values; QC before resampling")
    if not (np.isfinite(source_hz) and np.isfinite(target_hz) and 0 < target_hz <= source_hz):
        raise ValueError("This proxy supports downsampling only; cannot recover higher-frequency data")
    if x.ndim == 2 and x.shape[1] > 8:
        raise ValueError("Too many channels for this wrist proxy")
    fraction = Fraction(float(target_hz) / float(source_hz)).limit_denominator(10000)
    y = resample_poly(x, fraction.numerator, fraction.denominator, axis=0)
    count = int(np.floor(len(x) / source_hz * target_hz + 1e-8))
    return np.asarray(y[:count], dtype=float)


def _motion_index(acc: np.ndarray) -> np.ndarray:
    """Dimensionless normalized movement intensity; not a validated artifact label."""
    a = np.asarray(acc, dtype=float)
    if a.ndim != 2 or a.shape[1] != 3:
        raise ValueError("Three-axis ACC required")
    jerk = np.linalg.norm(np.diff(a, axis=0, prepend=a[:1]), axis=1)
    # Avoid converting arbitrary raw accelerometer units to g.
    scale = max(float(np.percentile(jerk, 95)), 1e-12)
    return np.clip(jerk / scale, 0, 2)


def _motion_to_ppg(motion: np.ndarray, ppg_length: int, acc_hz: float, ppg_hz: float) -> np.ndarray:
    acc_t = np.arange(len(motion)) / acc_hz
    ppg_t = np.arange(ppg_length) / ppg_hz
    return np.interp(ppg_t, acc_t, motion, left=motion[0], right=motion[-1])


def simulate_continuous(
    source: dict[str, tuple[np.ndarray, float]],
    *,
    seed: int = 20261115,
    ppg_noise_fraction: float = 0.02,
    ppg_motion_fraction: float = 0.25,
    dropout_probability: float = 0.01,
    temperature_output_hz: float | None = None,
) -> WatchStreams:
    """Convert a synchronized, same-person wrist recording into constrained streams.

    Required: ppg, acc, eda. Temperature optional; its cadence must be explicitly
    chosen as a modeling assumption, not claimed to be Samsung's real rate.

    No ECG or processed Samsung IBI stream is synthesized. Those channels are
    unavailable until recorded by actual hardware or a verified reference.
    """
    for name in TARGET_HZ:
        if name not in source:
            raise ValueError(f"Missing required same-person wrist stream: {name}")
    if not (0 <= dropout_probability < 1):
        raise ValueError("dropout_probability must lie in [0,1)")
    if min(ppg_noise_fraction, ppg_motion_fraction) < 0:
        raise ValueError("Noise scale cannot be negative")
    if "temperature" in source and temperature_output_hz is None:
        raise ValueError("Temperature cadence must be declared; vendor source has no fixed Hz")
    if "temperature" not in source and temperature_output_hz is not None:
        raise ValueError("Temperature cadence specified without temperature source")
    rng = np.random.default_rng(seed)
    durations = {}
    for name, (samples, hz) in source.items():
        if name not in (*TARGET_HZ, "temperature"):
            raise ValueError(f"Unknown continuous modality: {name}")
        x = np.asarray(samples)
        if x.ndim not in (1, 2) or hz <= 0:
            raise ValueError("Invalid stream or sampling rate")
        durations[name] = len(x) / hz
    common_duration = min(durations.values())
    if max(durations.values()) - common_duration > .5:
        raise ValueError("Source streams are not time-aligned: unequal durations")
    if common_duration < 20.0:
        raise ValueError("At least 20 seconds of simultaneous wrist data required")

    result = {}
    rates = {**TARGET_HZ}
    if temperature_output_hz is not None:
        rates["temperature"] = temperature_output_hz
    for name, target_hz in rates.items():
        samples, source_hz = source[name]
        count = int(common_duration * source_hz)
        x = np.asarray(samples, dtype=float)[:count]
        y = downsample_recording(x, source_hz, target_hz)
        result[name] = Stream(target_hz, y, float(source_hz), "wrist_source", {
            "downsampling": "polyphase anti-alias", "vendor_emulation": False,
            "sensor_equivalence": "NOT established", "clock_alignment": "assumed by input contract",
        })
    if result["acc"].samples.ndim != 2 or result["acc"].samples.shape[1] != 3:
        raise ValueError("ACC must be 3-axis")
    if result["ppg"].samples.ndim != 1 or result["eda"].samples.ndim != 1:
        raise ValueError("PPG and EDA must be single channel")
    motion = _motion_to_ppg(
        _motion_index(result["acc"].samples), len(result["ppg"].samples),
        result["acc"].hz, result["ppg"].hz,
    )
    ppg = result["ppg"]
    amplitude = max(float(np.std(ppg.samples)), 1e-9)
    # Motion-correlated additive interference: an explicit scenario assumption.
    contaminated = (ppg.samples + amplitude * (
        ppg_noise_fraction * rng.normal(size=len(ppg.samples))
        + ppg_motion_fraction * motion * rng.normal(size=len(ppg.samples))
    ))
    missing = rng.random(len(contaminated)) < dropout_probability
    contaminated[missing] = np.nan
    result["ppg"] = Stream(ppg.hz, contaminated, ppg.source_hz, ppg.origin, {
        **ppg.metadata, "noise_fraction_of_ppg_std": ppg_noise_fraction,
        "motion_artifact_fraction_of_ppg_std": ppg_motion_fraction,
        "dropout_probability": dropout_probability,
        "model_seed": seed,
    })
    return WatchStreams(result, common_duration, "continuous_only", (
        "On-demand ECG is NOT available in this continuous session.",
        "Processed Samsung HR/IBI are NOT simulated from raw BVP.",
        "No blood pressure, pupil, QSART, or ANS diagnosis available.",
        "All artifacts are assumed scenarios; hardware transfer not calibrated.",
    ))


def qc_and_features(session: WatchStreams, min_valid_ppg: float = .95) -> dict:
    """Descriptive, domain-labelled engineering values only. No diagnostic score."""
    streams = session.streams
    ppg = streams["ppg"]
    eda = streams["eda"]
    acc = streams["acc"]
    if not 0 < min_valid_ppg <= 1:
        raise ValueError("Invalid PPG quality threshold")
    ppg_pass = ppg.coverage >= min_valid_ppg
    # No pulse peaks, PTT, HRV or clinical functional diagnosis inferred here.
    result = {
        "duration_seconds": session.duration_seconds,
        "ppg_sample_count": len(ppg.samples),
        "eda_sample_count": len(eda.samples),
        "acc_sample_count": len(acc.samples),
        "ppg_coverage": ppg.coverage,
        "eda_coverage": eda.coverage,
        "ppg_qc": "pass_coverage_only_not_beat_validation" if ppg_pass else "withheld_insufficient_coverage",
        "eda_range_source_units": float(np.ptp(eda.samples)),
        "relative_motion_change": float(np.median(_motion_index(acc.samples))),
        "temperature_median_source_units": float(np.median(streams["temperature"].samples)) if "temperature" in streams else None,
        "beat_detection_validated": False,
        "heart_rate_bpm": None,
        "pulse_hrv": None,
        "autonomic_dysfunction_probability": None,
        "diagnostic_accuracy": None,
        "independent_clinical_labels_available": False,
        "limitations": "Coverage/QC and descriptive signal values only; clinical ANS performance unmeasured",
    }
    return result
