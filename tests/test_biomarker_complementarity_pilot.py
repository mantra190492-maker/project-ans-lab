import numpy as np
import pytest
from scripts.biomarker_complementarity_pilot import run_analysis, _rho, _rank_partial_rho


def fixture():
    # Artificial test-only values, not actual patient records.
    brs=[4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
    rs=[3, 10, 6, 12, 8, 18, 13, 15, 26, 20]
    measured=[dict(record=str(i),rmssd_ms=x,brs_ms_per_mmHg_exploratory=y,
                   brs_status="unvalidated_exploratory", automatic_ecg_qc="pass",
                   heart_rate_bpm=float(80-i)) for i,(x,y) in enumerate(zip(rs,brs))]
    missing=[dict(record=str(10+i),rmssd_ms=33+i,brs_ms_per_mmHg_exploratory=None,
                  brs_status="withheld_quality_or_sequences",automatic_ecg_qc="pass",
                  heart_rate_bpm=70) for i in range(6)]
    return {"dataset":"PhysioNet Autonomic Aging 1.0.0","records":measured+missing}


def test_results_reproducible_and_not_a_diagnostic_model():
    a=run_analysis(fixture(),bootstrap_samples=200,permutation_samples=300)
    b=run_analysis(fixture(),bootstrap_samples=200,permutation_samples=300)
    assert a == b
    assert a["persons_total"]==16
    assert a["provisional_brs_available"]==10
    assert a["brs_withheld_after_ecg_qc"]==6
    assert a["clinical_labels_present"] is False
    assert a["brs_independently_validated"] is False
    assert a["rmssd_brs_bootstrap_95pct_ci"][0] <= a["rmssd_brs_spearman_rho"] <= a["rmssd_brs_bootstrap_95pct_ci"][1]


def test_duplicate_record_rejected():
    a=fixture();a["records"][1]["record"]=a["records"][0]["record"]
    with pytest.raises(ValueError,match="Unique"):
        run_analysis(a,bootstrap_samples=200,permutation_samples=300)


def test_clinical_source_mismatch_rejected():
    a=fixture();a["dataset"]="invented clinical cohort"
    with pytest.raises(ValueError,match="Unexpected dataset"):
        run_analysis(a,bootstrap_samples=200,permutation_samples=300)


def test_tie_correct_spearman_ranks_and_not_argsort():
    assert np.isclose(_rho([1,1,2,3],[3,3,2,1]),-1)


def test_withheld_values_not_zero_imputed():
    a=fixture()
    r=run_analysis(a,bootstrap_samples=200,permutation_samples=300)
    assert r["brs_coverage_after_ecg_qc"]==10/16
    assert r["rmssd_median_without_brs_ms"]>r["rmssd_median_with_brs_ms"]
    assert r["rmssd_brs_spearman_rho"]==pytest.approx(_rho([v["rmssd_ms"] for v in a["records"][:10]],
                                                              [v["brs_ms_per_mmHg_exploratory"] for v in a["records"][:10]]))


def test_exclude_failed_ecg_qc():
    a=fixture()
    a["records"].append(dict(record="flagged", rmssd_ms=10000, automatic_ecg_qc="review_required",
                             brs_status="withheld_quality_or_sequences",brs_ms_per_mmHg_exploratory=None))
    r=run_analysis(a,bootstrap_samples=200,permutation_samples=300)
    assert r["ecg_qc_excluded"]==1
    assert r["rmssd_median_without_brs_ms"] < 10000


def test_partial_rank_correlation_is_finite_for_noncollinear_vectors():
    x=[1,2,3,4,5,6,7,8,9,10]
    y=[2,3,1,5,6,4,7,10,9,8]
    z=[10,9,6,7,5,4,1,3,2,8]
    assert -1<=_rank_partial_rho(x,y,z)<=1
