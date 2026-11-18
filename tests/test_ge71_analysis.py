import math

import numpy as np

from anslab.physio_qc import detect_ecg_rpeaks
from scripts.ge71_analysis import (
    beat_labels, deceleration_capacity, fit_marker, grid_half_up, hrv_metrics,
    is_candidate, refine_peaks, subject_key, window_qc,
)


def _capno(seconds, hz=10, period=4.0, top=38.0):
    t = np.arange(int(seconds * hz)) / hz
    return 2 + (top - 2) * (np.sin(2 * np.pi * t / period) > 0)


def test_window_qc_accepts_quiet_breathing_and_rejects_gap_and_hyperventilation():
    assert window_qc(_capno(240)) == "ok"
    gap = _capno(240).copy(); gap[600:800] = 0.0
    assert window_qc(gap) == "no_breathing_gap"
    hyper = _capno(240).copy(); hyper[1200:1800] = _capno(60, period=1.5, top=20.0)
    assert window_qc(hyper) == "etco2_unstable"
    assert window_qc(np.zeros(2400)) == "no_capnogram"
    assert window_qc(_capno(100)) == "too_short"


def _synthetic_ecg(fs=1000, seconds=240, seed=1, inverted=False):
    rng = np.random.default_rng(seed)
    times, t = [], 0.6
    i = 0
    while t < seconds - 1:
        times.append(t)
        t += 0.9 + 0.03 * math.sin(2 * math.pi * i / 4.5) + rng.normal(0, 0.004)
        i += 1
    x = np.arange(int(seconds * fs)) / fs
    ecg = rng.normal(0, 0.01, len(x))
    for bt in times:
        lo, hi = int((bt - 0.3) * fs), int((bt + 0.5) * fs)
        seg = x[max(lo, 0):hi]
        ecg[max(lo, 0):hi] += np.exp(-0.5 * ((seg - bt) / 0.010) ** 2) - 0.25 * np.exp(-0.5 * ((seg - bt - 0.03) / 0.012) ** 2) \
            + 0.2 * np.exp(-0.5 * ((seg - bt - 0.25) / 0.04) ** 2)
    return (-ecg if inverted else ecg), np.array(times)


def test_refined_peaks_recover_true_beat_times_within_2ms_for_both_polarities():
    for inverted in (False, True):
        ecg, truth = _synthetic_ecg(inverted=inverted)
        p1, _, _ = detect_ecg_rpeaks(ecg, 1000)
        found = refine_peaks(ecg, p1, 1000) / 1000.0
        assert abs(len(found) - len(truth)) <= 2
        err = [min(abs(truth - f)) for f in found]
        assert np.percentile(err, 95) <= 0.002


def test_hrv_metrics_and_ectopy_labels():
    _, truth = _synthetic_ecg()
    m = hrv_metrics(truth)
    assert m["status"] == "ok" and 60 < m["hr"] < 72 and 20 < m["pip"] < 90 and np.isfinite(m["dc"])
    early = truth.copy(); early[100] -= 0.35           # premature beat
    labels = beat_labels(early)
    assert labels[100] == 3 and labels[101] == 3 and labels.count(3) <= 3
    assert hrv_metrics(truth[:60])["status"] == "ecg_qc_fail"


def test_grid_half_up_and_subject_key():
    assert grid_half_up([0.002, 0.0019, 0.006]) == [0.004, 0.0, 0.008]
    assert subject_key("S0030") == "s0030" and subject_key("s0044DB") == "s0044" and subject_key("") is None


def test_deceleration_capacity_positive_for_smooth_rsa():
    i = np.arange(600)
    rr = 900 + 40 * np.sin(2 * np.pi * i / 5.0)
    assert deceleration_capacity(rr, np.ones(len(rr), dtype=bool)) > 5


def test_fit_marker_detects_real_effect_and_not_noise():
    rng = np.random.default_rng(5)
    n = 45
    covs = [rng.normal(size=n) for _ in range(5)]
    marker = rng.normal(size=n)
    y = 1.5 - 0.15 * marker + 0.05 * covs[0] + rng.normal(0, 0.12, n)
    res = fit_marker(y, marker, covs)
    assert res["beta_per_sd"] < 0 and is_candidate(res)
    hits = 0
    for seed in range(40):
        r = np.random.default_rng(100 + seed)
        res0 = fit_marker(r.normal(size=n), r.normal(size=n), [r.normal(size=n) for _ in range(5)])
        hits += is_candidate(res0)
    assert hits <= 4
