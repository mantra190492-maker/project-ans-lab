from scripts.diab_prepare2 import PERSON_COLUMNS, header_comment_keys, label_counts, linkage, person_table, read_table

TEXT = ("Patient ID,Visit,Group,HEIGHT (M),Race,sex,age\n"
        "S0001,2,DM,1.70,W,F,61\nS0001,8,DM,1.70,W,F,63\nS0002,2,CONTROL,1.82,B,M,70\nS0003,2,DM,,W,,\n")


def test_label_counts_are_per_person_and_restricted_to_kept_ids():
    header, rows = read_table(TEXT)
    assert label_counts(header, rows, r"group") == {"control": 1, "dm": 2}
    assert label_counts(header, rows, r"group", keep_ids={"s0002"}) == {"control": 1}
    assert label_counts(header, rows, r"nonexistent") is None


def test_person_table_takes_first_non_missing_value():
    header, rows = read_table(TEXT)
    people, found = person_table(header, rows, PERSON_COLUMNS)
    assert people["s0001"] == {"height": "1.70", "race": "w", "group": "dm", "age": "61", "sex": "f"}
    assert people["s0003"]["sex"] == "" and found["sex"] == "sex"


def test_linkage_compares_height_race_group():
    a = {"s0001": {"height": "1.70", "race": "w", "group": "dm"}, "s0002": {"height": "1.82", "race": "b", "group": "control"}}
    b = {"s0001": {"height": "1.71", "race": "white", "group": "dm"}, "s0002": {"height": "1.60", "race": "w", "group": "dm"}}
    assert linkage(a, b) == {"shared_ids": 2, "height_comparable": 2, "height_within_3cm": 1,
                             "race_comparable": 2, "race_same": 1, "group_comparable": 2, "group_same": 1}


def test_header_comment_keys_never_return_values():
    keys = header_comment_keys("rec 2 500 1000\nrec.dat 16 1 16 0 0 0 0 ecg\n# Age: 61\n#sex=F\n")
    assert dict(keys) == {"age": 1, "sex": 1}
