import pytest
from anslab.physiology import rr_features,sequence_brs,compare_age_association

def test_constant_rr_has_zero_variability():
    r=rr_features([1.0]*40)
    assert r["mean_hr_bpm"]==60
    assert r["rmssd_ms"]==0
    assert r["sdnn_ms"]==0

def test_bad_rr_rejected():
    with pytest.raises(ValueError):
        rr_features([1.0]*29)

def test_no_sequences_is_reported_not_invented():
    result=sequence_brs([120.0]*30,[1.0]*30)
    assert result["brs_ms_per_mmHg"] is None
    assert result["quality"]=="insufficient_sequences"

def test_age_comparison_not_falsely_implemented():
    with pytest.raises(NotImplementedError):
        compare_age_association([],[],[])
