import math

from scripts.hrf_resolution_gate import (
    RULE, artifact_labels, compare, evaluate, parse_wfdb_annotation, regrid,
)
from scripts.hrf_shared_signal_null import classify, cohort


def _beats(n=300, base=0.9, swing=0.03):
    times, t = [0.0], 0.0
    for i in range(n):
        t += base + swing * math.sin(2 * math.pi * i / 4.5) + (0.004 if i % 7 == 0 else 0.0)
        times.append(round(t * 250) / 250)
    return times


def test_regrid_snaps_to_coarser_sample_grid_with_explicit_tie_rules():
    ties = [0.004, 0.012, 0.020]  # odd 250 Hz samples: exactly between 125 Hz samples
    assert regrid(ties, 125, tie="floor") == [0.0, 0.008, 0.016]
    assert regrid(ties, 125, tie="half_even") == [0.0, 0.016, 0.016]
    assert all(t in (0.0, 0.008, 0.016, 0.024) for t in regrid(ties, 125, tie="random"))
    assert regrid([0.008, 0.016], 125, tie="random") == [0.008, 0.016]  # on-grid beats untouched
    for t in regrid(_beats(), 125):
        assert abs(t * 125 - round(t * 125)) < 1e-9


def test_artifact_labels_flag_missed_beat_only():
    times = _beats(60)
    del times[30]  # simulate a missed R peak -> one long interval
    labels = artifact_labels(times)
    assert labels.count(3) >= 1
    assert labels[0] == 1


def test_compare_is_paired_on_identical_beats():
    times = _beats()
    row = compare("synthetic", times, [1] * len(times))
    assert row["n_beats"] == len(times)
    assert math.isclose(row["pip_shift_pp"], row["pip_125"] - row["pip_250"])


def test_wfdb_symbols_map_to_reference_labels():
    times, labels = parse_wfdb_annotation([0, 250, 500, 750, 1000], ["N", "V", "+", "A", "N"], 250.0)
    assert times == [0.0, 1.0, 3.0, 4.0]
    assert labels == [1, 2, 3, 1]


def test_rule_requires_all_three_checks():
    rows = [{"record": f"r{v}", "pip_250": v, "pip_125": v + 10, "pip_shift_pp": 10.0 + 0.01 * (v % 3),
             "rmssd_ms": 20 + v} for v in range(12)]
    result = evaluate(rows, "pip_250", "pip_125", "pip_shift_pp")
    assert result["checks"]["rank_agreement"] is True
    assert result["checks"]["small_mean_shift"] is False
    assert result["decision"] == "FAIL"
    assert RULE["min_spearman"] == 0.90


def test_null_simulation_runs_and_classifies():
    out = cohort((1, "null_stable_fragmentation", 40))
    assert set(out) >= {"rmssd", "rsa_resp"}
    assert classify(0.05) == "safe" and classify(0.09) == "borderline" and classify(0.2) == "trap material"


def test_spearman_handles_ties_with_average_ranks():
    from scripts.hrf_resolution_gate import spearman
    assert abs(spearman([1, 1, 2, 3], [1, 2, 3, 4]) - 0.9486832980505138) < 1e-9


def test_participant_clustering_groups_gudb_tasks():
    from scripts.hrf_resolution_gate import participant_of
    assert participant_of({"record": "gudb_s03_sitting"}) == participant_of({"record": "gudb_s03_maths"}) == "gudb_s03"
    assert participant_of({"record": "f1y01"}) == "f1y01"
