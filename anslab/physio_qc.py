"""Exploratory ECG/BP feature extraction with explicit quality gates.

A second detector agreement is a *consistency check*, not independent ground truth.
No output from this module is a validated clinical measurement.
"""
import numpy as np
from scipy.ndimage import uniform_filter1d, median_filter
from scipy.signal import butter, find_peaks, sosfiltfilt

def _bandpass(x, fs):
    return sosfiltfilt(butter(3, [5, 22], btype="bandpass", fs=fs, output="sos"), x)

def detect_ecg_rpeaks(ecg, fs):
    x = np.asarray(ecg, dtype=float)
    if len(x) < fs * 120 or not np.all(np.isfinite(x)) or np.ptp(x) < 0.005:
        raise ValueError("ECG missing, nonfinite, too short or near-flat")
    filtered = _bandpass(x, fs)
    primary_env = np.abs(filtered)
    threshold = max(float(np.percentile(primary_env, 97)) * 0.48,
                    float(np.median(primary_env)) * 3.0)
    p1, _ = find_peaks(primary_env, distance=int(0.4 * fs), prominence=threshold)
    # Separate, derivative-energy-based candidate detector (NOT ground truth).
    derivative = np.diff(filtered, prepend=filtered[0])
    energy = uniform_filter1d(derivative ** 2, size=max(3, int(fs * 0.10)))
    threshold2 = max(float(np.percentile(energy, 92)) * 0.45,
                     float(np.median(energy)) * 3.0)
    p2, _ = find_peaks(energy, distance=int(0.4 * fs), prominence=threshold2)
    if len(p1) < 100:
        raise ValueError("Too few primary ECG peaks")
    return p1, p2, filtered

def detector_agreement(primary, secondary, fs, tolerance_s=0.18):
    if not len(primary) or not len(secondary):
        return 0.0
    matched = 0
    used = set()
    for beat in primary:
        j = int(np.searchsorted(secondary, beat))
        candidates = [k for k in (j - 1, j) if 0 <= k < len(secondary)
                      and k not in used and abs(int(secondary[k])-int(beat)) <= tolerance_s * fs]
        if candidates:
            best = min(candidates, key=lambda k: abs(int(secondary[k])-int(beat)))
            used.add(best)
            matched += 1
    return float(2 * matched / (len(primary) + len(secondary)))

def hrv_proxy(rpeaks, fs):
    rr = np.diff(rpeaks) / float(fs)
    if len(rr) < 100:
        raise ValueError("Insufficient RR intervals")
    plausible = (rr >= 0.4) & (rr <= 1.5)
    reference = median_filter(rr, size=11, mode="nearest")
    clean = plausible & (np.abs(rr - reference) <= np.maximum(0.12, 0.20 * reference))
    cleaned = rr[clean]
    successive = np.diff(rr)[clean[:-1] & clean[1:]]
    if len(cleaned) < 100 or len(successive) < 80:
        raise ValueError("Insufficient artifact-screened RR intervals")
    return {
        "ecg_beats": int(len(rpeaks)),
        "rr_plausible_fraction": float(np.mean(plausible)),
        "rr_clean_fraction": float(np.mean(clean)),
        "heart_rate_bpm": float(60.0 / np.mean(cleaned)),
        "sdnn_ms": float(np.std(cleaned, ddof=1) * 1000),
        "rmssd_ms": float(np.sqrt(np.mean(successive ** 2)) * 1000),
        "caveat": "Automated RR screening; not manually verified normal-to-normal intervals"
    }

def bp_and_brs(bp, rpeaks, fs, eligible):
    if not np.all(np.isfinite(bp)):
        raise ValueError("Nonfinite blood pressure")
    smooth = sosfiltfilt(butter(2, 8, btype="lowpass", fs=fs, output="sos"), bp)
    peaks, _ = find_peaks(smooth, distance=int(fs * 0.4), prominence=8)
    sbp = {}
    for i, beat in enumerate(rpeaks[:-1]):
        possible = peaks[(peaks >= beat + int(fs * 0.08)) &
                         (peaks <= beat + int(fs * 0.60))]
        if len(possible) == 1 and 60 <= smooth[possible[0]] <= 250:
            sbp[i] = float(smooth[possible[0]])
    slopes = []
    i = 0
    while i + 4 < len(rpeaks):
        if all(k in sbp for k in (i, i + 1, i + 2)):
            x = np.array([sbp[i+k] for k in range(3)])
            y = np.array([(rpeaks[i+k+2]-rpeaks[i+k+1])*1000/fs
                          for k in range(3)])
            dx, dy = np.diff(x), np.diff(y)
            direction = (np.all(dx >= 1) and np.all(dy >= 5)) or (
                         np.all(dx <= -1) and np.all(dy <= -5))
            if direction and np.std(x) > 0 and np.std(y) > 0:
                corr = float(np.corrcoef(x, y)[0, 1])
                slope = float(np.polyfit(x, y, 1)[0])
                if corr >= 0.85 and slope > 0:
                    slopes.append(slope)
                    i += 3  # prevent overlapping accepted sequences
                    continue
        i += 1
    matched_fraction = float(len(sbp) / max(len(rpeaks) - 1, 1))
    # Strict reporting gate: no quantitative BRS for poor ECG quality or sparse sequences.
    can_report = eligible and matched_fraction >= 0.85 and len(slopes) >= 5
    return {
        "bp_rpeak_match_fraction": matched_fraction,
        "brs_sequences_nonoverlapping": len(slopes),
        "brs_ms_per_mmHg_exploratory": float(np.median(slopes)) if can_report else None,
        "brs_status": "unvalidated_exploratory" if can_report else "withheld_quality_or_sequences",
        "bp_systolic_peak_count": int(len(peaks))
    }, peaks

def analyze_signals(ecg, bp, fs):
    if fs < 50:
        raise ValueError("Sampling frequency too low")
    if len(ecg) != len(bp) or len(ecg) < fs * 120:
        raise ValueError("ECG/BP signals not synchronized or insufficient length")
    p1, p2, filtered = detect_ecg_rpeaks(ecg, fs)
    rr = hrv_proxy(p1, fs)
    agreement = detector_agreement(p1, p2, fs)
    # Explicit QA of timing and plausible beats; NOT a gold-standard validation.
    eligible = (rr["rr_plausible_fraction"] >= 0.95 and
                rr["rr_clean_fraction"] >= 0.90 and
                agreement >= 0.85 and
                40 <= rr["heart_rate_bpm"] <= 140)
    brs, bp_peaks = bp_and_brs(np.asarray(bp, dtype=float), p1, fs, eligible)
    metrics = {**rr, "qrs_detector_agreement_f1": agreement,
               "automatic_ecg_qc": "pass" if eligible else "review_required", **brs}
    return metrics, (p1, bp_peaks)
