import numpy as np

from scripts.diab_prepare import demographics, earliest_quiet_window, same_person_evidence, subject_key, table_columns
from tests.test_ge71_analysis import _capno


def test_earliest_quiet_window_skips_a_breath_hold():
    hz = 10
    co2 = _capno(900, hz=hz).copy()
    co2[40 * hz:70 * hz] = 0.0                      # mask off for an early Valsalva
    start, n = earliest_quiet_window(co2, hz=hz)
    assert start == 70 and n > 10
    assert earliest_quiet_window(np.zeros(900 * hz), hz=hz) == (None, 0)


def test_table_helpers_find_columns_and_count_only():
    text = "Patient ID,Group,age,Gender,X\nS0001,DM,61,F,\nS0002,CONTROL,70,M,3\n"
    header, rows, cols = table_columns(text)
    people, found = demographics(header, rows)
    assert found == {"id": "Patient ID", "age": "age", "sex": "Gender", "group": "Group"}
    assert people["s0001"] == {"age": "61", "sex": "f", "group": "dm"} and cols[4] == (4, "X", 1)
    assert subject_key("s0044DB-v2") == "s0044"


def test_same_person_evidence_uses_age_and_sex():
    a = {"s0001": {"age": "61", "sex": "f", "group": ""}, "s0002": {"age": "70", "sex": "m", "group": ""}}
    b = {"s0001": {"age": "62", "sex": "f", "group": ""}, "s0002": {"age": "55", "sex": "m", "group": ""}, "s0003": {"age": "50", "sex": "f", "group": ""}}
    assert same_person_evidence(a, b) == {"shared_ids": 2, "comparable": 2, "same_sex_and_age_within_3y": 1}
