import numpy as np
import pytest
from scripts.fantasia_hrf_pilot import annotation_intervals

def test_normal_beats_make_valid_consecutive_intervals():
    rr,valid=annotation_intervals([0,250,500,750],["N"]*4,250)
    assert np.all(rr==1000)
    assert np.all(valid)

def test_abnormal_beat_does_not_bridge_gap():
    rr,valid=annotation_intervals([0,250,500,750,1000],
                                  ["N","N","V","N","N"],250)
    assert valid.tolist()==[True,False,False,True]

def test_label_count_mismatch_fails():
    with pytest.raises(ValueError,match="mismatch"):
        annotation_intervals([0,250,500],["N","N"],250)
