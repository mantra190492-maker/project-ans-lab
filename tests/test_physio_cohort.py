import numpy as np
import pytest
from anslab.physio_qc import detector_agreement, hrv_proxy, analyze_signals
from scripts.physionet_cohort import choose_subjects, STRATA

def test_detector_agreement_perfect_and_mismatched():
    x=np.array([1000,2000,3000,4000])
    assert detector_agreement(x,x,1000)==pytest.approx(1.0)
    assert detector_agreement(x,x+400,1000)==0.0

def test_clean_rr_variability():
    r=np.arange(0,160)*250
    out=hrv_proxy(r,250)
    assert out["heart_rate_bpm"]==pytest.approx(60.0)
    assert out["sdnn_ms"]==pytest.approx(0.0)
    assert out["rmssd_ms"]==pytest.approx(0.0)
    assert out["rr_clean_fraction"]==pytest.approx(1.0)

def test_rr_rejects_implausible_artifact():
    r=np.arange(0,160)*250
    r[70]=r[69]+20
    out=hrv_proxy(r,250)
    assert out["rr_clean_fraction"]<1.0

def test_stratified_sample_deterministic_and_distinct():
    subjects=[]
    for minimum, maximum in STRATA.values():
        for n in range(14):
            subjects.append({
                "record":f"{minimum:02d}{n:02d}",
                "age_group":minimum,
                "sex_code":n%2,
                "device_code":0 if n<12 else 1,
                "length_min":15,
            })
    a=choose_subjects(subjects)
    b=choose_subjects(subjects)
    assert a==b
    assert len(a)==20
    assert len({s["record"] for s in a})==20
    assert all(s["device_code"]==0 for s in a)
    assert all(sum(r["age_stratum"]==band for r in a)==5 for band in STRATA)

def test_overlarge_cohort_prevented():
    with pytest.raises(ValueError):
        choose_subjects([],per_group=50)

def test_synthetic_ecg_bp_is_not_claimed_validated():
    fs=250
    t=np.arange(0,180,1/fs)
    ecg=np.zeros(len(t))
    bp=np.full(len(t),75.)
    # Simplified impulses; this is a deterministic software integration test,
    # not a physiologically realistic beat-detector benchmark.
    for second in range(1,179):
        ecg += np.exp(-0.5*((t-second)/0.015)**2)
        bp += 40*np.exp(-0.5*((t-second-0.2)/0.075)**2)
    results,_=analyze_signals(ecg,bp,fs)
    assert results["ecg_beats"]>100
    assert 40<results["heart_rate_bpm"]<140
    assert results["brs_ms_per_mmHg_exploratory"] is None
    assert "unvalidated" in results["caveat"].lower() or "not manually verified" in results["caveat"].lower()
