import numpy as np

from scripts.vr_core import detect_all_beats, gap_based_vr, mask_off_gaps, median3, template_quality, valsalva_ratio
from scripts.vr_validate import agreement, marker_based_vr
from tests.test_ge71_analysis import _synthetic_ecg


def _valsalva_beats(strain_start=120.0, strain_s=15.0, rest_rr=0.9, min_rr=0.6, max_rr=1.2, total=240.0):
    t, times = 0.0, []
    while t < total:
        times.append(t)
        if strain_start <= t < strain_start + strain_s:          # tachycardia builds during strain
            frac = (t - strain_start) / strain_s
            rr = rest_rr - (rest_rr - min_rr) * frac
        elif strain_start + strain_s <= t < strain_start + strain_s + 12:   # overshoot bradycardia after release
            frac = (t - strain_start - strain_s) / 12
            rr = min_rr + (max_rr - min_rr) * min(1.0, frac * 2) if frac < 0.5 else max_rr - (max_rr - rest_rr) * (frac - 0.5) * 2
        else:
            rr = rest_rr
        t += rr
    return np.array(times)


def _capno_with_gap(gap=(118.0, 140.0), total=240.0, hz=10):
    t = np.arange(int(total * hz)) / hz
    x = 2 + 36 * (np.sin(2 * np.pi * t / 4.0) > 0)
    x[(t >= gap[0]) & (t < gap[1])] = 1.0
    return x


def test_mask_off_gap_found_and_ordinary_breaths_ignored():
    gaps = mask_off_gaps(_capno_with_gap())
    assert len(gaps) == 1 and abs(gaps[0][0] - 118) < 3 and abs(gaps[0][1] - 140) < 3
    assert mask_off_gaps(_capno_with_gap(gap=(500, 501))) == []
    assert mask_off_gaps(_capno_with_gap(gap=(20, 45))) == []            # mask placement in first minute
    assert mask_off_gaps(_capno_with_gap(gap=(215, 240))) == []          # mask off at the end of the record


def test_valsalva_ratio_from_gap_matches_construction():
    beats = _valsalva_beats()
    vr, used = gap_based_vr(beats, mask_off_gaps(_capno_with_gap()))
    assert used == 1 and 1.7 <= vr <= 2.05                              # true 1.2 / 0.6 = 2.0, slightly smoothed
    flat = np.arange(0, 240, 0.9)
    vr0, _ = gap_based_vr(flat, [(118.0, 140.0)])
    assert abs(vr0 - 1.0) < 1e-6
    assert valsalva_ratio(flat[:5], 0, 3) is None


def test_median3_removes_ectopic_pair_but_keeps_trend():
    rr = np.array([0.9, 0.9, 0.5, 1.3, 0.9, 0.9])
    assert np.allclose(median3(rr)[2:4], [0.9, 0.9])
    ramp = np.linspace(0.6, 1.2, 9)
    assert np.allclose(median3(ramp)[1:-1], ramp[1:-1])


def test_marker_based_ratio_uses_table_ordinals():
    beats = _valsalva_beats()
    pulses = [5.0, 60.0, 90.0, 120.0, 135.0]
    assert 1.7 <= marker_based_vr(beats, pulses, [(4, 5), (0, 0), (0, 0)]) <= 2.05
    assert marker_based_vr(beats, pulses, [(9, 10)]) is None


def test_whole_record_detection_and_template_quality():
    ecg, truth = _synthetic_ecg(seconds=260)
    peaks = detect_all_beats(ecg, 1000)
    assert abs(len(peaks) - len(truth)) <= 3
    assert template_quality(ecg, peaks, 1000) > 0.95
    noise = np.random.default_rng(0).normal(size=len(ecg))
    assert template_quality(noise, peaks, 1000) < 0.5


def test_agreement_reports_rank_correlation():
    a = [1.1, 1.3, 1.5, 1.7, 1.9, 2.0, 1.2, 1.4, None]
    b = [1.0, 1.2, 1.6, 1.6, 2.0, 2.1, 1.3, 1.5, 1.4]
    out = agreement(a, b)
    assert out["n"] == 8 and out["spearman"] > 0.9
