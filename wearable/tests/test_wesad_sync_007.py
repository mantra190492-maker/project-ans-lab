"""Synthetic alignment and QC invariants only, no real WESAD traces."""
import numpy as np
import pytest
from wearable.experiments.wesad_sync_007 import (
    aggregate,find_clock_shift,match_peaks,ppg_epoch_quality,within
)


def shifted_beat_arrays(lag=2.34,seed=777):
    rng=np.random.default_rng(seed)
    rr=.8+.11*np.sin(np.arange(280)*.73)+.055*np.sin(np.arange(280)*1.21)
    e=np.cumsum(rr)
    p=e+lag+rng.normal(0,.008,size=len(e))
    return e,p


def test_clock_shift_from_training_and_confirmation_not_evaluation():
    e,p=shifted_beat_arrays(lag=2.34)
    c=find_clock_shift(e,p)
    assert c["train_pass"] and c["confirmation_pass"],c
    assert abs(c["lag_seconds"]-2.34)<.10,c
    assert c["lag_in_nominal_pulse_transit_window"] is False
    # Changing all test-window pulses must not affect the trained offset.
    p_changed=p.copy()
    p_changed[p_changed>70]+=3.5
    c2=find_clock_shift(e,p_changed)
    assert c["lag_seconds"]==c2["lag_seconds"]
    a=within(e,70,170)
    b=within(p,70+c["lag_seconds"],170+c["lag_seconds"])
    assert match_peaks(a,b,c["lag_seconds"],tol=.15)["f1"]>.95


def test_zero_offset_and_positive_pulse_delay_separate():
    e,p=shifted_beat_arrays(lag=.25)
    c=find_clock_shift(e,p)
    assert c["train_pass"] and c["confirmation_pass"]
    assert abs(c["lag_seconds"]-.25)<.10


def test_bad_or_missing_calibration_is_rejected():
    e,p=shifted_beat_arrays()
    with pytest.raises(ValueError,match="Too few calibration"):
        find_clock_shift(e[:7],p[:7])


def test_quality_passes_periodic_signal_and_rejects_flat_noise():
    fs=64
    t=np.arange(20*fs)/fs
    pulse=1.5*np.sin(2*np.pi*1.2*t)+.1*np.sin(2*np.pi*2.4*t)
    times=np.arange(.2,20,1/1.2)
    good=ppg_epoch_quality(pulse,times)
    assert good["passed"],good
    bad=ppg_epoch_quality(np.zeros_like(pulse),times)
    assert not bad["passed"]


def test_quality_rejects_unreliable_irregular_detected_peaks():
    fs=64
    t=np.arange(20*fs)/fs
    pulse=np.sin(2*np.pi*1.2*t)
    too_few=np.array([1,5,12,19])
    bad=ppg_epoch_quality(pulse,too_few)
    assert not bad["passed"]


def test_report_exposes_coverage_and_diagnostic_limits():
    exemplar={
        "lag":{"lag_seconds":2.34,"train_fraction":.8,
               "confirmation_fraction":.75,"train_pass":True,
               "confirmation_pass":True,"ambiguous_offset":True,
               "lag_in_nominal_pulse_transit_window":False},
        "quality_epochs_accepted":3,"quality_epochs_total":5,
        "median_f1_on_accepted_epochs":.75,
        "median_shifted_negative_control_f1":.35,
        "median_PPG_autocorr":.72,
        "source":"synthetic",
    }
    report=aggregate([{"baseline":exemplar,"stress":{"withheld_reason":"ECG gate failed"}}],
                     offset=0,rate=64)
    assert report["results"]["baseline"]["epoch_coverage"]==.6
    assert report["results"]["baseline"]["n_ambiguous_lag"]==1
    assert report["results"]["stress"]["n_wholly_withheld"]==1
    assert report["results"]["stress"]["heldout_f1_per_subject_median"] is None
    assert report["clinical_accuracy"] is None
    assert report["physical_pulse_transit_time_estimated"] is False
    assert report["ecg_reference_manually_verified"] is False
    assert not report["source_data_published"]
