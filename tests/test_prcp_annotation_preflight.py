from types import SimpleNamespace
from scripts.prcp_annotation_preflight import annotation_summary, render


def test_marker_vocabulary_is_counted_not_given_unsupported_clinical_meaning():
    a=SimpleNamespace(sample=[10,20,30],symbol=["+","N","+"],
                      aux_note=["stand?","", "tilt?"])
    z=annotation_summary(a)
    assert z["n_annotations"]==3
    assert z["symbol_counts"]=={"+":2,"N":1}
    assert z["aux_labels_counts"]=={"stand?":1,"tilt?":1}
    assert z["first_event_sample"]==10


def test_empty_annotation_handled():
    a=SimpleNamespace(sample=[],symbol=[],aux_note=[])
    z=annotation_summary(a)
    assert z["n_annotations"]==0
    assert z["first_event_sample"] is None


def test_report_identifies_anonymous_failed_records_without_guessing():
    x={"generated_utc":"2026-11-15T00:00:00+00:00",
       "records":[{"record":"r1","status":"failed","error_type":"ValueError","error":"bad data"}]}
    text=render(x)
    assert "bad data" in text
    assert "cannot by itself validate ANS dysfunction diagnosis" in text
