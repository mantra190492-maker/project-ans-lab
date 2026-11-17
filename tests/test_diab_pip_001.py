import numpy as np

from scripts.diab_pip_001 import (analyse, choose_records, co2_plausible, group_difference, is_pass, people_from_tables,
                                  predictor_hash, to_group)
from scripts.diab_prepare2 import read_table
from tests.test_ge71_analysis import _capno


def _row(ds, pid, status="ok", pip=60.0):
    r = {"dataset": ds, "id": pid, "status": status}
    if status == "ok":
        r.update({"pip": pip, "hr": 65.0, "log_rmssd": 3.0})
    return r


def test_co2_swing_must_be_physiologic():
    assert co2_plausible(_capno(240))
    assert not co2_plausible(_capno(240) * 3000)        # corrupted scale
    assert not co2_plausible(_capno(240, top=5.0))      # flat


def test_group_labels_and_visit_two_rows_only():
    assert (to_group(" DM "), to_group("control"), to_group("stroke"), to_group("")) == (1, 0, None, None)
    t = read_table("Patient ID,Visit,Group,BETA BLOCKERS\nS0001,8,CONTROL,Y\nS0001,2,DM,N\nS0002,2,CONTROL,\n")
    people = people_from_tables([t])
    assert people["s0001"] == {"group": "dm", "beta": "n", "age": "", "sex": ""}
    assert people["s0002"]["group"] == "control"


def test_choose_records_follows_the_frozen_rules():
    rows = [_row("GE75", "s0001"), _row("CDED", "s0001", pip=99.0),          # both pass -> GE-75 record
            _row("GE75", "s0002", status="ecg_qc_fail"), _row("CDED", "s0002"),  # GE-75 fails -> CDED record
            _row("CDED", "s0003"),                                           # also in GE-71 -> excluded
            _row("CDED", "s0004"),                                           # no label -> excluded
            _row("CDED", "s0005", status="no_breathing_gap")]                # nothing passes
    people = {"GE75": {"s0001": {"group": "dm", "beta": "y", "age": "61", "sex": "female"}, "s0002": {"group": "dm"}},
              "CDED": {"s0001": {"group": "dm"}, "s0002": {"group": "dm", "beta": "n"}, "s0003": {"group": "control"},
                       "s0005": {"group": "control"}}}
    chosen, flow, selection = choose_records(rows, people, {"s0003"})
    assert [(c["id"], c["dataset"], c["pip"]) for c in chosen] == [("s0001", "GE75", 60.0), ("s0002", "CDED", 60.0)]
    assert chosen[0]["age"] == "61" and chosen[1]["beta"] == "n"
    assert flow == {"unique_people": 5, "people_with_records_in_both_datasets": 2, "analysed": 2, "excluded_also_in_ge71": 1,
                    "excluded_no_group_label": 1, "no_record_passed_quality_rules": 1}
    assert selection == {"control": {"failed": 1}, "diabetes": {"passed": 2}}


def test_predictor_hash_ignores_row_order_and_changes_with_values():
    a, b = [_row("CDED", "s0001"), _row("GE75", "s0002", status="ecg_qc_fail")], [_row("GE75", "s0002", status="ecg_qc_fail"), _row("CDED", "s0001")]
    assert predictor_hash(a) == predictor_hash(b) != predictor_hash([_row("CDED", "s0001", pip=61.0), b[0]])


def test_group_difference_recovers_a_real_difference_and_not_a_confounded_one():
    rng = np.random.default_rng(1)
    n = 80
    g = (np.arange(n) % 2).astype(float)
    hr = rng.normal(65, 8, n)
    real = 60 + 6 * g + 0.3 * (hr - 65) + rng.normal(0, 3, n)
    res = group_difference(real, g, [hr, np.zeros(n)], n_boot=300)     # the constant covariate is dropped, not a crash
    assert 4 < res["difference"] < 8 and is_pass(res) and res["n_diabetes"] == 40
    hr2 = 65 + 8 * g + rng.normal(0, 2, n)                              # group differs only through heart rate
    confounded = 60 + 1.0 * (hr2 - 65) + rng.normal(0, 3, n)
    assert not is_pass(group_difference(confounded, g, [hr2], n_boot=300))
    assert is_pass(group_difference(confounded, g, [], n_boot=300))     # unadjusted, the confounded gap looks real
    assert not is_pass(group_difference(-real, g, [hr], n_boot=300))    # wrong sign never passes


def test_analyse_reports_s4_as_not_estimable_without_ten_per_group():
    rng = np.random.default_rng(2)
    chosen = []
    for i in range(40):
        dm = float(i % 2)
        ge75 = i < 12
        chosen.append({"dataset": "GE75" if ge75 else "CDED", "id": f"s{i:04d}", "status": "ok", "dm": dm,
                       "pip": 60 + 5 * dm + rng.normal(0, 3), "hr": rng.normal(65, 8), "log_rmssd": rng.normal(3, 0.4),
                       "beta": "y" if i % 7 == 0 else "n", "age": "60" if ge75 else "", "sex": ("female" if i % 3 else "male") if ge75 else ""})
    primary, sens, desc, rho, extra = analyse(chosen)
    assert primary["n"] == 40 and sens["S2_cded_only"]["n"] == 28 and extra["s4_subset_n"] == 12
    assert sens["S4_adding_age_and_sex_where_available"] is None
    assert desc["diabetes"]["n"] == 20 and desc["control"]["from_ge75"] == 6 and len(rho) == 2


def test_measure_is_the_tilt_001_pipeline_plus_the_co2_plausibility_rule():
    from scripts.diab_pip_001 import measure
    from scripts.tilt_001 import predictors_for
    from tests.test_ge71_analysis import _synthetic_ecg
    ecg, _ = _synthetic_ecg()
    co2 = np.repeat(_capno(240), 100)
    status, m = measure(ecg, co2, 1000.0)
    ref_status, ref = predictors_for(ecg, co2, 1000.0)
    assert status == ref_status == "ok" and m["pip"] == ref["pip"] and m["hr"] == ref["hr"]
    assert measure(ecg, co2 * 3000, 1000.0) == ("co2_implausible", None)
    gap = co2.copy(); gap[60000:80000] = 0.0
    assert measure(ecg, gap, 1000.0) == ("no_breathing_gap", None)
