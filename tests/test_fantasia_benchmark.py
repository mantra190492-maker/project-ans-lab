import numpy as np
import pytest
from scripts.fantasia_benchmark import match_peaks

def test_perfect_annotations():
    m=match_peaks([100,200,300],[100,200,300],5)
    assert m["f1"]==1
    assert m["false_positive"]==0
    assert m["false_negative"]==0

def test_duplicate_detection_not_double_counted():
    m=match_peaks([100,101,200],[100,200],5)
    assert m["true_positive"]==2
    assert m["false_positive"]==1
    assert m["false_negative"]==0

def test_disjoint_beat_series_rejected():
    m=match_peaks([100,200],[400,500],5)
    assert m["f1"]==0
    assert m["median_abs_timing_error_ms"] is None

def test_timing_tolerance_is_bounded():
    a=match_peaks([100,200],[103,203],2)
    b=match_peaks([100,200],[103,203],3)
    assert a["f1"]==0
    assert b["f1"]==1
