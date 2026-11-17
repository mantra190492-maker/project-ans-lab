"""Clinical-reference registry integrity tests: metadata only, no patient records."""
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "clinical_reference" / "registry.json"


def test_eight_specialist_modalities_are_external_references_not_watch_sensors():
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    refs = payload["references"]
    assert len(refs) == 8
    assert len({r["id"] for r in refs}) == 8
    assert all(r["watch_sensor"] is False for r in refs)
    assert all(r["general_ANS_gold_standard"] is False for r in refs)
    assert all(r["confounding_and_limits"] for r in refs)
    assert "No same-person" in payload["clinical_status"]


def test_specific_pathology_not_mislabeled_as_general_ans_target():
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    pathology = next(r for r in payload["references"] if r["id"] == "PHOSPHO_ALPHA_SYNUCLEIN")
    assert pathology["group"] == "disease_specific_pathology"
    assert "synucleinopathies" in pathology["domain"]


def test_reference_only_inputs_and_independent_evaluation_required():
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rules = " ".join(payload["design_rules"]).lower()
    assert "excluded from wearable-only predictor" in rules
    assert "real participants" in rules
    assert "missing, not normal" in rules
