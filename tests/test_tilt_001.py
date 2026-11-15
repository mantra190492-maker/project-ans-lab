import numpy as np

from scripts.tilt_001 import BASES, MIN_TEMPLATE, predictors_for
from tests.test_ge71_analysis import _capno, _synthetic_ecg


def test_mirror_is_tried_first_and_threshold_is_fixed():
    assert BASES[0].startswith("https://physionet-open.s3.amazonaws.com/") and BASES[1].startswith("https://physionet.org/files/")
    assert MIN_TEMPLATE == 0.90


def test_predictors_from_clean_window_and_rejections():
    ecg, _ = _synthetic_ecg(seconds=240)
    co2 = np.repeat(_capno(240), 100)                      # 10 Hz capnogram held at 1000 Hz
    status, m = predictors_for(ecg, co2, 1000.0)
    assert status == "ok" and 55 < m["hr"] < 75 and 0 < m["pip"] < 100
    gap = co2.copy(); gap[60_000:80_000] = 0.0
    assert predictors_for(ecg, gap, 1000.0) == ("no_breathing_gap", None)
    noise = np.random.default_rng(0).normal(size=len(ecg))
    assert predictors_for(noise, co2, 1000.0)[1] is None
