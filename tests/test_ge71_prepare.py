import numpy as np

from scripts.ge71_prepare import marker_times, rest_window, summary_columns


def _capnogram(minutes, hz=10, period_s=4.0):
    t = np.arange(int(minutes * 60 * hz)) / hz
    return 20 + 19 * np.sign(np.sin(2 * np.pi * t / period_s))


def test_rest_window_ends_before_first_mask_off_gap():
    hz = 10
    co2 = np.concatenate([_capnogram(6), np.zeros(40 * hz), _capnogram(3)])
    res = rest_window(co2, hz=hz)
    assert res["status"] == "ok"
    assert 345 <= res["gap_s"] <= 362
    assert res["end_s"] <= res["gap_s"] - 15
    assert 180 <= res["end_s"] - res["start_s"] <= 300
    assert 12 <= res["breaths_per_min"] <= 18


def test_rest_window_rejects_short_rest_and_missing_capnogram():
    hz = 10
    short = np.concatenate([_capnogram(2), np.zeros(60 * hz), _capnogram(4)])
    assert rest_window(short, hz=hz)["status"] == "rest_too_short"
    assert rest_window(np.zeros(6 * 60 * hz), hz=hz)["status"] == "no_capnogram"


def test_marker_times_merge_double_pulses():
    fs = 100.0
    m = np.zeros(6000)
    for s in (500, 520, 3000):
        m[s:s + 10] = 1.0
    assert marker_times(m, fs) == [5.0, 30.0]


def test_summary_columns_report_names_and_counts_only():
    counts, ids, n = summary_columns("Subject ID,RATIO VALSALVA,Age\nS0030,1.5,60\nS0044,,70\n")
    assert n == 2 and ids == ["S0030", "S0044"]
    assert counts[1] == (1, "RATIO VALSALVA", 1)
