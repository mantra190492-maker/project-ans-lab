"""Shared, outcome-blind signal functions for the Valsalva-ratio work (POOL-VR-001).

Beat detection over whole records, ECG template quality, mask-off gap detection from
CO2, and the automated Valsalva ratio. No statistics here.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt

from anslab.physio_qc import detect_ecg_rpeaks
from scripts.ge71_analysis import refine_peaks

ENV_HZ = 10


def detect_all_beats(ecg, fs, chunk_s=120, step_s=110):
    """R-peak sample indices for a whole record, detector thresholds adapted per 2-minute chunk."""
    x = np.asarray(ecg, dtype=float)
    x = np.nan_to_num(x - np.nanmedian(x))
    n, chunk, step = len(x), int(chunk_s * fs), int(step_s * fs)
    if n < chunk:
        return np.array([], dtype=int)
    peaks = []
    starts = list(range(0, n - chunk + 1, step))
    if starts[-1] + chunk < n:
        starts.append(n - chunk)
    for k, s in enumerate(starts):
        seg = x[s:s + chunk]
        scale = np.percentile(np.abs(seg), 99)
        if scale <= 0:
            continue
        try:
            p1, _, _ = detect_ecg_rpeaks(seg / scale, fs)
            p = refine_peaks(seg, p1, fs) + s
        except ValueError:
            continue
        hi = starts[k + 1] if k + 1 < len(starts) else n
        peaks.extend(int(v) for v in p if s <= v < hi)
    peaks = np.array(sorted(set(peaks)), dtype=int)
    if len(peaks) < 2:
        return peaks
    keep = [0]
    for i in range(1, len(peaks)):
        if peaks[i] - peaks[keep[-1]] >= 0.25 * fs:
            keep.append(i)
    return peaks[keep]


def template_quality(ecg, peaks, fs, half_ms=60):
    """Fraction of beats whose shape correlates >= 0.8 with the median beat (outcome-blind ECG QC)."""
    if len(peaks) < 20:
        return 0.0
    x = sosfiltfilt(butter(2, [1, 40], btype="bandpass", fs=fs, output="sos"), np.nan_to_num(np.asarray(ecg, dtype=float)))
    half = int(round(half_ms * fs / 1000))
    beats = np.array([x[p - half:p + half + 1] for p in peaks if p - half >= 0 and p + half + 1 <= len(x)])
    if len(beats) < 20:
        return 0.0
    template = np.median(beats, axis=0)
    t = template - template.mean()
    b = beats - beats.mean(axis=1, keepdims=True)
    denom = np.sqrt((b ** 2).sum(axis=1) * (t ** 2).sum()) + 1e-12
    return float(np.mean((b @ t) / denom >= 0.8))


def mask_off_gaps(co2_env, hz=ENV_HZ, min_s=8, max_s=150, first_s=60, tail_s=35):
    """(start_s, end_s) runs where CO2 stays below 25% of typical end-tidal: mask off for a Valsalva."""
    x = np.asarray(co2_env, dtype=float)
    if len(x) < 3 * 60 * hz or not np.any(np.isfinite(x)):
        return []
    x = np.nan_to_num(x)
    base = np.percentile(x, 2)
    etco2 = np.percentile(x[: min(len(x), 5 * 60 * hz)], 90) - base
    if etco2 <= 0:
        return []
    low = (x - base) < 0.25 * etco2
    gaps, start = [], None
    for i, flag in enumerate(low):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            gaps.append([start, i])
            start = None
    if start is not None:
        gaps.append([start, len(x)])
    merged = []
    for g in gaps:                                   # ordinary inspirations are short runs; merge only real neighbours
        if (g[1] - g[0]) / hz < 3:
            continue
        if merged and (g[0] - merged[-1][1]) / hz < 5:
            merged[-1][1] = g[1]
        else:
            merged.append(g)
    out = []
    for s, e in merged:
        dur = (e - s) / hz
        if min_s <= dur <= max_s and s / hz >= first_s and e / hz <= len(x) / hz - tail_s:
            out.append((s / hz, e / hz))
    return out


def median3(v):
    v = np.asarray(v, dtype=float)
    if len(v) < 3:
        return v.copy()
    out = v.copy()
    out[1:-1] = np.median(np.column_stack([v[:-2], v[1:-1], v[2:]]), axis=1)
    return out


def valsalva_ratio(beat_times, strain_lo, strain_hi, recover_s=30, min_beats=15):
    """Longest RR within recover_s after the shortest RR found in [strain_lo, strain_hi]; None if unusable."""
    t = np.asarray(beat_times, dtype=float)
    sel = (t >= strain_lo - 2) & (t <= strain_hi + recover_s + 2)
    t = t[sel]
    if len(t) < min_beats:
        return None
    rr = median3(np.diff(t))
    rt = t[1:]
    ok = (rr > 0.3) & (rr < 2.0)
    strain = ok & (rt >= strain_lo) & (rt <= strain_hi)
    if strain.sum() < 5:
        return None
    i_min = np.flatnonzero(strain)[np.argmin(rr[strain])]
    after = ok & (rt > rt[i_min]) & (rt <= rt[i_min] + recover_s)
    if after.sum() < 5:
        return None
    return float(rr[after].max() / rr[i_min])


def gap_based_vr(beat_times, gaps):
    """Largest Valsalva ratio over mask-off gaps (shortest RR from 10 s before to 10 s after each gap)."""
    values = [valsalva_ratio(beat_times, s - 10, e + 10) for s, e in gaps]
    values = [v for v in values if v is not None]
    return (max(values), len(values)) if values else (None, 0)
