"""Synthetic pulse generator only; no WESAD waveform or clinical labels."""
import numpy as np
import pytest
from scipy.signal import resample_poly
from wearable.signal_processing import extract_wrist_pulse_times,count_based_pulse_rate_bpm


def artificial_bvp(fs, seconds=180, heart_rate=72):
    time=np.arange(int(fs*seconds))/fs
    phase=(time*heart_rate/60)%1
    pulse=np.exp(-.5*((phase-.24)/.11)**2)
    return pulse+.008*np.sin(2*np.pi*.08*time)


def test_ppg_processing_supports_both_sampling_rates_without_relabeling_time():
    v64=artificial_bvp(64)
    v25=resample_poly(v64,25,64)
    t64=extract_wrist_pulse_times(v64,64)
    t25=extract_wrist_pulse_times(v25,25)
    assert np.all(np.diff(t64)>0)
    assert np.all(np.diff(t25)>0)
    hr64=count_based_pulse_rate_bpm(v64,64)
    hr25=count_based_pulse_rate_bpm(v25,25)
    assert abs(hr64-72)<6
    assert abs(hr25-72)<6
    assert abs(hr25-hr64)<4


def test_reject_invalid_signal_or_unstudied_rate():
    with pytest.raises(ValueError,match="25Hz or 64Hz"):
        extract_wrist_pulse_times(artificial_bvp(64),100)
    with pytest.raises(ValueError,match="invalid or flat"):
        extract_wrist_pulse_times(np.zeros(180*64),64)
    with pytest.raises(ValueError,match="at least 20s"):
        extract_wrist_pulse_times(np.zeros(64*10),64)


def test_reject_window_outside_observation():
    x=artificial_bvp(64)
    with pytest.raises(ValueError,match="outside measured"):
        count_based_pulse_rate_bpm(x,64,170,190)
    with pytest.raises(ValueError,match="increasing"):
        count_based_pulse_rate_bpm(x,64,170,160)
