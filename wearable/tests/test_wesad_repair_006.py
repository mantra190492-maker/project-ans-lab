"""Artificial aggregate test fixtures, not WESAD recordings."""
from wearable.experiments.wesad_repair_006 import summarize


def row(baseline_direct,baseline_interp,stress_direct,stress_interp):
    return {
        "baseline":{"abs_64hz_error_bpm":1.,
                    "abs_direct25_error_bpm":baseline_direct,
                    "abs_interpolated25_error_bpm":baseline_interp,
                    "interpolation_minus_direct_abs_error":baseline_interp-baseline_direct},
        "stress":{"abs_64hz_error_bpm":3.,
                  "abs_direct25_error_bpm":stress_direct,
                  "abs_interpolated25_error_bpm":stress_interp,
                  "interpolation_minus_direct_abs_error":stress_interp-stress_direct}
    }


def test_aggregate_preserves_pairs_and_no_diagnosis_claim():
    out=summarize([row(10,6,25,12),row(4,4,17,20)])
    assert out["additional_untouched_subjects_attempted"]==2
    assert out["results"]["baseline"]["n_interpolated_less_error_than_direct25"]==1
    assert out["results"]["baseline"]["n_equal"]==1
    assert out["results"]["stress"]["n_interpolated_more_error_than_direct25"]==1
    assert out["clinical_accuracy"] is None
    assert out["beat_alignment_accuracy"] is None
    assert out["clinical_ANS_or_EDS_labels"]==0
    assert not out["subject_data_shared"]


def test_withheld_subjects_preserve_denominator_and_are_not_zero_imputed():
    out=summarize([row(10,6,25,12),{"baseline":{"withheld_reason":"ECG QC"},
                                 "stress":{"withheld_reason":"ECG QC"}}])
    assert out["results"]["stress"]["n_valid"]==1
    assert out["results"]["stress"]["n_withheld"]==1
    assert out["results"]["stress"]["withheld_reason_counts"]=={"ECG QC":1}
    assert out["results"]["stress"]["metrics"]["abs_direct25_error_bpm"]["median"]==25


def test_no_valid_pairs_makes_null_metrics():
    out=summarize([{"baseline":{"withheld_reason":"quality"},
                    "stress":{"withheld_reason":"quality"}}])
    assert out["results"]["stress"]["metrics"]["abs_direct25_error_bpm"] is None
