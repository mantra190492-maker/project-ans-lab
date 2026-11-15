"""LEGACY/PROVISIONAL heart-rate fragmentation symbolic measurement.\n\n**NOT numerically equivalent to Costa 2024 official PIP.**\nFor reference-comparable PIP use `anslab.hrf_costa_reference.costa_fragmentation_from_peaks`\nwith original R-peak timestamps and beat-level rhythm labels.

Research basis: Costa et al., Front Physiol 2018, DOI 10.3389/fphys.2018.01117.
PIP counts transitions between ternary successive NN-difference symbols.
No clinical cutoffs, prognostic interpretation or autonomous arrhythmia screening.
"""
from __future__ import annotations

import numpy as np


def fragmentation_features(
    nn_ms,
    *,
    validated_sinus: bool = False,
    valid_mask=None,
    quantization_ms: float = 5.0,
    min_clean_intervals: int = 200,
    min_clean_fraction: float = 0.95,
):
    """Return PIP / W1 descriptive markers on beat-aligned, screened NN intervals.

    IMPORTANT:
    - Inputs are consecutive time-ordered intervals, not a gap-compressed
      concatenation of 'good' intervals.
    - valid_mask=False identifies a bad interval but PRESERVES its original index.
      Adjacent differences and words crossing a gap are excluded.
    - validated_sinus=True is an explicit *upstream* annotation/QC declaration,
      not a test or proof of sinus rhythm.
    - Quantization resolution MUST be recorded; MESA used 4 ms at 256 Hz.
      MUSIC Holter recordings nominally sample at 200 Hz (5 ms/sample).
      Do not compare cohort PIP without a sensitivity analysis.
    """
    if validated_sinus is not True:
        raise ValueError("Confirmed sinus-rhythm NN input is required; raw/AF/paced RR forbidden")
    arr = np.asarray(nn_ms, dtype=float)
    if arr.ndim != 1 or len(arr) < max(5, min_clean_intervals):
        raise ValueError("Insufficient or non-one-dimensional NN data")
    if not np.isfinite(quantization_ms) or quantization_ms <= 0 or quantization_ms > 25:
        raise ValueError("Invalid NN difference quantization threshold")
    if not 0.5 <= min_clean_fraction <= 1.0:
        raise ValueError("Invalid minimum clean fraction")
    if valid_mask is None:
        # Only acceptable if upstream really has confirmed *all* beats clean.
        ok = np.ones(len(arr), dtype=bool)
    else:
        ok = np.asarray(valid_mask)
        if ok.ndim != 1 or len(ok) != len(arr) or ok.dtype.kind != "b":
            raise ValueError("valid_mask must be a 1D boolean array aligned to NN intervals")
        ok = ok.copy()
    # Apply plausibility limits without interpolating or splicing separated runs.
    ok &= np.isfinite(arr) & (arr >= 300) & (arr <= 2000)
    clean_count = int(ok.sum())
    clean_fraction = float(clean_count / len(arr))
    if clean_count < min_clean_intervals or clean_fraction < min_clean_fraction:
        raise ValueError("Insufficient quality-screened sinus NN intervals")

    delta = np.diff(arr)
    # Acceleration = NN shortens, deceleration = NN lengthens, stable = 0.
    symbols = np.zeros(len(delta), dtype=np.int8)
    symbols[delta < -quantization_ms] = -1
    symbols[delta > quantization_ms] = 1

    # An inflection needs 3 physically adjacent, individually valid NN intervals.
    triple_valid = ok[:-2] & ok[1:-1] & ok[2:]
    transitions = symbols[1:] != symbols[:-1]
    eligible = int(triple_valid.sum())
    if eligible < max(50, min_clean_intervals // 2):
        raise ValueError("Insufficient contiguous triplets for PIP")
    pip_percent = float(100.0 * transitions[triple_valid].mean())

    # W1: among windows of 4 NN-difference symbols (5 NN intervals),
    # percent with exactly one ternary transition.
    five_valid = ok[:-4] & ok[1:-3] & ok[2:-2] & ok[3:-1] & ok[4:]
    n_words = int(five_valid.sum())
    if n_words < 50:
        raise ValueError("Insufficient five-interval windows for W1")
    ternary_transition = symbols[1:] != symbols[:-1]
    words_inflections = (
        ternary_transition[:-2].astype(int)
        + ternary_transition[1:-1].astype(int)
        + ternary_transition[2:].astype(int)
    )
    w1_percent = float(100.0 * np.mean(words_inflections[five_valid] == 1))

    clean_pairs = ok[:-1] & ok[1:]
    pair_differences = delta[clean_pairs]
    rmssd = float(np.sqrt(np.mean(pair_differences**2)))
    hr = float(60000.0 / np.mean(arr[ok]))
    return {
        "pip_percent": pip_percent,
        "w1_percent": w1_percent,
        "rmssd_ms": rmssd,
        "heart_rate_bpm": hr,
        "quantization_ms": float(quantization_ms),
        "n_total_intervals": int(len(arr)),
        "n_clean_intervals": clean_count,
        "clean_fraction": clean_fraction,
        "n_contiguous_triplets": eligible,
        "n_valid_4symbol_words": n_words,
        "input_assumption": "Upstream verified sinus NN labels and beat QC required",
        "method_status": "LEGACY_PROVISIONAL_NOT_COSTA_REFERENCE_EQUIVALENT",\n        "reference_equivalent": False,\n        "scope": "Research-only symbolic features; not a prognostic or longevity score; NOT Costa 2024 reference PIP",
    }
