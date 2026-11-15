import pytest
from scripts.music_metadata_audit import summarize, counts_display, render

def rows(n=992):
    template = {
        "Patient ID": "",
        "Follow-up period from enrollment (days)": "1000",
        "Cause of death": "0",
        "Exit of the study": "",
        "Age": "62",
        "Gender (male=1)": "1",
        "Body Mass Index (Kg/m2)": "26",
        "Prior Myocardial Infarction (yes=1)": "0",
        "Prior Revascularization": "0",
        "Holter available": "1",
        "Holter rhythm ": "0",
        "Betablockers (yes=1)": "1",
        "SDNN (ms)": "103",
        "RMSSD (ms)": "28",
    }
    return [{**template, "Patient ID":f"P{i:04d}"} for i in range(n)]

def test_aggregate_sample_schema_and_no_patient_data():
    data=rows()
    for r in data[:35]:
        r["Prior Revascularization"]="1"
    for r in data[35:40]:
        r["Prior Revascularization"]="3"
    data[0]["Cause of death"]="3"
    result=summarize(data)
    assert result["participant_rows"]==992
    assert result["field_completeness"]["RMSSD (ms)"]==992
    assert result["prior_revascularization_codes"]["1"]==35
    assert result["prior_revascularization_codes"]["3"]==5
    assert result["raw_data_saved"] is False
    assert "P0001" not in str(result)
    text=render({**result,"generated_utc":"2026-11-15"})
    assert "No individual patient records" in text

def test_blank_and_sentinel_hrv_are_missing():
    sample=rows()
    sample[0]["RMSSD (ms)"]=""
    sample[1]["RMSSD (ms)"]="999"
    sample[2]["RMSSD (ms)"]="NA"
    out=summarize(sample)
    assert out["field_completeness"]["RMSSD (ms)"]==989

def test_duplicate_subjects_rejected():
    sample=rows()
    sample[1]["Patient ID"]=sample[0]["Patient ID"]
    with pytest.raises(ValueError,match="not unique"):
        summarize(sample)

def test_missing_schema_fails_loudly():
    sample=rows()
    for r in sample: r.pop("Prior Revascularization")
    with pytest.raises(ValueError,match="Missing essential columns"):
        summarize(sample)

def test_small_groups_suppressed_in_markdown():
    assert "1: <5" in counts_display({"1":3,"0":989})

def test_optional_holter_rhythm_absent_from_source():
    source=rows()
    for item in source:
        item.pop("Holter rhythm ")
    report=summarize(source)
    assert report["holter_rhythm_status"]=="not_found_in_metadata_header"
    assert report["field_completeness"]["Holter rhythm"]==0

def test_double_space_holter_rhythm_header_from_real_metadata():
    sample=rows()
    for item in sample:
        item["Holter  rhythm"]=item.pop("Holter rhythm ")
    report=summarize(sample)
    assert report["holter_rhythm_source_column"]=="Holter  rhythm"
    assert report["field_completeness"]["Holter rhythm"]==992
    assert report["holter_rhythm_codes"]["0"]==992

def test_exit_and_cause_cross_tab_preserves_blanks():
    source=rows()
    source[0]["Exit of the study"]="2"
    source[1]["Exit of the study"]="1"
    source[2]["Exit of the study"]="3"
    source[2]["Cause of death"]="3"
    report=summarize(source)
    assert report["exit_of_study_codes"]["2"]==1
    assert report["exit_of_study_codes"]["<blank>"]==989
    assert report["exit_cause_joint_counts"]["exit=2;cause=0"]==1
    assert sum(report["exit_cause_joint_counts"].values())==992
