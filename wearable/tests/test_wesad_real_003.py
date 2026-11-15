"""Deterministic artificial timing fixtures; NEVER WESAD patient data."""
import numpy as np
import pytest
from wearable.experiments.wesad_real_003 import (
    aggregate, calibrate_lag, find_ecg_beats, find_pulse_beats,
    get_sync_arrays, match_peaks, process_subject, select_condition_window,
)


def fake_source(seconds=420):
    ecg_t=np.arange(700*seconds)/700
    ppg_t=np.arange(64*seconds)/64
    centers=list(np.arange(.5,209,60/72))+list(np.arange(210.5,seconds-1,60/96))
    ek=np.zeros(len(ecg_t));bp=np.zeros(len(ppg_t))
    for c in centers:
        i=int(c*700)
        if 8<=i<len(ek)-8:
            w=np.arange(-8,9)
            ek[i+w]+=1.6*np.exp(-(w/3)**2)
        j=int((c+.24)*64)
        if 12<=j<len(bp)-13:
            w=np.arange(-12,13)
            bp[j+w]+=.75*np.exp(-(w/5)**2)
    ek+=.008*np.sin(ecg_t*.3)
    bp+=.01*np.sin(ppg_t*.11)
    lab=np.ones(len(ek),dtype=np.int8)
    lab[int(210*700):]=2
    return {"signal":{"chest":{"ECG":ek},"wrist":{"BVP":bp}},"label":lab}


def test_source_alignment_enforced():
    a=fake_source()
    ecg,bvp,labels=get_sync_arrays(a)
    assert len(ecg)/700==420 and len(bvp)/64==420 and len(labels)==len(ecg)
    a["signal"]["wrist"]["BVP"]=bvp[:2000]
    with pytest.raises(ValueError,match="durations disagree"):get_sync_arrays(a)


def test_disjoint_condition_segments_never_stitched():
    labels=np.r_[np.ones(700*95),np.zeros(700*15),np.ones(700*100)]
    with pytest.raises(ValueError,match="contiguous"):
        select_condition_window(labels,1,segment_seconds=180,skip_seconds=20)


def test_held_out_agreement_on_artificial_reference():
    out=process_subject(fake_source())
    for name in ("baseline","stress"):
        state=out[name]
        assert state.get("data_type"),state
        assert state["raw_wrist_bvp_64hz"]["f1"]>.90
        assert state["watch_rate_bvp_25hz"]["f1"]>.85
        assert state["ecg_beat_f1_vs_manual"] is None


def test_calibrated_pulse_delay_and_held_out_matching():
    ref=np.arange(1,101,.8);pulses=ref+.24
    lag=calibrate_lag(ref,pulses)
    assert abs(lag-.24)<.015
    assert match_peaks(ref[ref>=60],pulses[pulses>=60],lag)["f1"]>.98
    assert match_peaks(ref[ref>=60],pulses[pulses>=60],-.15)["f1"]<.10


def test_flat_signals_rejected_instead_of_artificial_beats():
    with pytest.raises(ValueError,match="Flat"):find_ecg_beats(np.ones(700*180))
    with pytest.raises(ValueError,match="Flat"):find_pulse_beats(np.zeros(64*180),64)


def test_aggregate_does_not_invent_clinical_results_or_real_data_provenance():
    result=aggregate([process_subject(fake_source())])
    assert result["subjects_attempted"]==1
    assert result["status"]=="unverified_source_not_claimed_as_real_data"
    assert result["clinical_diagnosis"]=="none"
    assert result["early_ANS_detection_accuracy"] is None
    assert not result["per_subject_data_committed"]
    assert "record" not in str(result["results"]).lower()
    assert not result["source_verified_original_archive"]
