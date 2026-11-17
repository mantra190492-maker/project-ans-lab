"""Validation invariants for repaired WESAD experiment; test values are synthetic."""
import math
import numpy as np
from wearable.experiments.wesad_repair_005 import aggregate, bpm, heldout


def pseudo_subject(error_legacy, error_64, error_25, *,calibrated=False):
    x={}
    for st in ("baseline","stress"):
        x[st]={
            "ecg_algorithm_agreement_f1":.995,
            "legacy_wrist_abs_rate_error_bpm":error_legacy,
            "repaired_wrist_64_abs_rate_error_bpm":error_64,
            "repaired_wrist_25_abs_rate_error_bpm":error_25,
            "pulse_timing_calibration":"passed" if calibrated else "withheld",
            "beat_f1_64":.88 if calibrated else None,
            "beat_f1_25":.86 if calibrated else None,
        }
    return x


def test_heldout_window_is_exact_and_excludes_training():
    samples=np.arange(0,180,.5)
    observed=heldout(samples)
    assert observed[0]==60
    assert observed[-1]==176.5
    assert 0 not in observed and 177 not in observed


def test_count_to_bpm_units():
    rr=np.arange(60,177,1)
    assert math.isclose(bpm(rr),60.0)


def test_aggregated_results_and_no_diagnostic_accuracy():
    r=aggregate([pseudo_subject(25,6,6.3),pseudo_subject(12,4,4.5)],verified_source=True)
    assert r["participants_attempted"]==2
    assert r["number_of_true_clinical_ANS_labels"]==0
    assert r["ANS_or_EDS_diagnostic_accuracy"] is None
    assert r["per_subject_data_shared"] is False
    assert r["results"]["stress"]["n_timing_calibration_withheld"]==2
    assert r["results"]["stress"]["stats"]["beat_f1_64"] is None
    assert math.isclose(r["results"]["stress"]["stats"]["repaired_wrist_64_abs_rate_error_bpm"]["median"],5.0)


def test_withheld_reference_not_silently_imputed():
    a=pseudo_subject(12,5,5.3,calibrated=True)
    b={"baseline":{"withheld_reason":"Independent ECG detectors disagree"},
       "stress":{"withheld_reason":"Independent ECG detectors disagree"}}
    out=aggregate([a,b],verified_source=False)
    assert out["results"]["baseline"]["n_valid_rate_pairs"]==1
    assert out["results"]["baseline"]["n_withheld_rate_pairs"]==1
    assert out["results"]["baseline"]["n_timing_calibration_pass"]==1
    assert out["results"]["baseline"]["stats"]["beat_f1_64"]["median"]==.88
    assert out["original_archive_verified"] is False
