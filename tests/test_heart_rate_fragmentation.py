import numpy as np
import pytest
from anslab.heart_rate_fragmentation import fragmentation_features


def test_constant_clean_sinus_has_no_fragmentation():
    result = fragmentation_features([1000.0] * 300, validated_sinus=True)
    assert result["pip_percent"] == 0.0
    assert result["w1_percent"] == 0.0
    assert result["rmssd_ms"] == pytest.approx(0.0)
    assert result["heart_rate_bpm"] == pytest.approx(60.0)


def test_alternating_nn_intervals_have_full_inflection():
    nn = 1000 + np.where(np.arange(300) % 2 == 0, 0, 10)
    result = fragmentation_features(nn, validated_sinus=True, quantization_ms=5)
    assert result["pip_percent"] == pytest.approx(100)
    # Each 4-symbol word has 3 transitions, never exactly 1.
    assert result["w1_percent"] == pytest.approx(0)


def test_quantization_sensitivity_explicit():
    nn = 1000 + np.where(np.arange(300) % 2 == 0, 0, 4)
    loose = fragmentation_features(nn, validated_sinus=True, quantization_ms=5)
    strict = fragmentation_features(nn, validated_sinus=True, quantization_ms=2)
    assert loose["pip_percent"] == 0
    assert strict["pip_percent"] == 100


def test_mask_prevents_cross_gap_artifacts():
    nn = 1000 + np.where(np.arange(300) % 2 == 0, 0, 10)
    mask = np.ones(300, dtype=bool)
    mask[100] = False
    result = fragmentation_features(nn, validated_sinus=True, valid_mask=mask)
    assert result["n_clean_intervals"] == 299
    assert result["n_contiguous_triplets"] == 300 - 2 - 3
    assert result["n_valid_4symbol_words"] == 300 - 4 - 5
    assert result["pip_percent"] == pytest.approx(100)


def test_reject_unverified_rhythm():
    with pytest.raises(ValueError, match="Confirmed sinus"):
        fragmentation_features([1000] * 300)


def test_reject_ectopy_contamination():
    mask = np.ones(300, dtype=bool)
    mask[:30] = False
    with pytest.raises(ValueError, match="Insufficient quality"):
        fragmentation_features([1000.0] * 300, validated_sinus=True, valid_mask=mask)


def test_reject_invalid_threshold():
    with pytest.raises(ValueError, match="quantization"):
        fragmentation_features([1000.0] * 300, validated_sinus=True, quantization_ms=-1)


def test_no_gap_compression_and_nan_masked():
    nn = np.full(300, 1000.0)
    nn[150] = np.nan
    result = fragmentation_features(nn, validated_sinus=True)
    assert result["n_clean_intervals"] == 299
    assert result["n_contiguous_triplets"] == 300 - 2 - 3


def test_explain_data_requirement():
    result = fragmentation_features([1000.0] * 300, validated_sinus=True)
    assert "not a prognostic" in result["scope"]
