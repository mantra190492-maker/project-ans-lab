import pytest
from anslab.population import audit_population_coverage

def framework():
    return {"current_dataset":{
        "name":"PhysioNet Autonomic Aging v1.0.0",
        "not_documented_individually":[
            "pregnancy_status","menopause_stage","coronary_stent_history","athlete_status"
        ]
    }}

def test_unrecorded_status_is_unknown_not_negative():
    rows=[{"age_group":2,"sex_code":1,"bmi":22,"device_code":0,"age_stratum":"18-34"},
          {"age_group":10,"sex_code":0,"bmi":24,"device_code":0,"age_stratum":"50-64"}]
    result=audit_population_coverage(rows,framework())
    assert result["participant_count"]==2
    assert result["children_under_18_included"] is False
    assert result["unmeasured_fields"]["pregnancy_status"]=="unknown_not_measured"
    assert result["unmeasured_fields"]["coronary_stent_history"]=="unknown_not_measured"

def test_rejects_undocumented_metadata_without_provenance_update():
    rows=[{"age_group":2,"pregnancy_status":False}]
    with pytest.raises(ValueError,match="conflicts"):
        audit_population_coverage(rows,framework())

def test_rejects_unexpected_child_age_encoding():
    with pytest.raises(ValueError,match="age-group"):
        audit_population_coverage([{"age_group":0}],framework())

def test_missing_bmi_not_assumed_normal():
    result=audit_population_coverage([{"age_group":8,"sex_code":1,"bmi":None,"device_code":0}],framework())
    assert result["observed_counts"]["bmi"]==0
