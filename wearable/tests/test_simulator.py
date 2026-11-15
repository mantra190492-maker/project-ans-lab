import numpy as np
import pytest

from wearable.experiments.watch_sim_001 import synthetic_wesad_shaped_inputs, run
from wearable.simulator import (
    downsample_recording, simulate_continuous, qc_and_features, load_profile
)


def test_profile_documents_wearable_capabilities_without_clinical_claim():
    p=load_profile()
    assert p['continuous']['ppg']['hz']==25
    assert p['continuous']['acc']['hz']==25
    assert p['continuous']['eda']['hz']==1
    assert p['continuous']['temperature']['hz'] is None
    assert p['on_demand']['ecg']['hz']==500
    assert 'validated orthostatic BP' in p['not_measured']


def test_explicit_antialias_and_sample_rates():
    src=synthetic_wesad_shaped_inputs(duration_seconds=20)
    sess=simulate_continuous(src,dropout_probability=0,temperature_output_hz=1)
    assert len(sess.streams['ppg'].samples)==500
    assert len(sess.streams['acc'].samples)==500
    assert len(sess.streams['eda'].samples)==20
    assert len(sess.streams['temperature'].samples)==20
    assert sess.mode=='continuous_only'
    assert set(sess.streams)=={'ppg','acc','eda','temperature'}


def test_low_pass_suppresses_alias_of_high_frequency_source():
    t=np.arange(64*20)/64
    x=np.sin(2*np.pi*20*t)   # above target Nyquist 12.5 Hz
    y=downsample_recording(x,64,25)
    assert len(y)==500
    assert np.std(y[50:-50]) < .05


def test_cannot_upsample_25hz_data_to_claim_500hz_ecg():
    with pytest.raises(ValueError,match='downsampling only'):
        downsample_recording(np.ones(250),25,500)


def test_temperature_hz_is_a_declared_assumption():
    src=synthetic_wesad_shaped_inputs(30)
    with pytest.raises(ValueError,match='cadence must be declared'):
        simulate_continuous(src)


def test_missing_eda_refuses_three_domain_fusion_claim():
    src=synthetic_wesad_shaped_inputs(30)
    del src['eda']
    with pytest.raises(ValueError,match='eda'):
        simulate_continuous(src,temperature_output_hz=1)


def test_misalignment_is_rejected_rather_than_silent_join():
    src=synthetic_wesad_shaped_inputs(30)
    eda,hz=src['eda'];src['eda']=(eda[:60],hz)
    with pytest.raises(ValueError,match='time-aligned'):
        simulate_continuous(src,temperature_output_hz=1)


def test_noise_dropout_is_reproducible_and_qc_withholds():
    src=synthetic_wesad_shaped_inputs(60)
    a=simulate_continuous(src,seed=77,dropout_probability=.20,temperature_output_hz=1)
    b=simulate_continuous(src,seed=77,dropout_probability=.20,temperature_output_hz=1)
    np.testing.assert_array_equal(a.streams['ppg'].samples,b.streams['ppg'].samples)
    r=qc_and_features(a)
    assert r['ppg_coverage'] < .95
    assert r['ppg_qc']=='withheld_insufficient_coverage'
    assert r['autonomic_dysfunction_probability'] is None
    assert r['diagnostic_accuracy'] is None


def test_missing_source_values_not_resampled_as_valid():
    x=np.ones(500);x[5]=np.nan
    with pytest.raises(ValueError,match='QC before resampling'):
        downsample_recording(x,25,25)


def test_demo_does_not_invent_clinical_results():
    a=run()
    assert a['recorded_subjects_used']==0
    assert a['watch_devices_used']==0
    assert a['results']['heart_rate_bpm'] is None
    assert a['results']['pulse_hrv'] is None
    assert not a['results']['beat_detection_validated']
    assert a['results']['diagnostic_accuracy'] is None
