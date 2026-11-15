import json
from pathlib import Path
import pytest
from scripts.dataset_inventory import main, render_inventory

def test_unknown_doi_in_record_does_not_crash():
    d=[{"name":"Candidate longitudinal cohort","url":"https://example.org",
        "access":"registered","signals":["ECG"],"status":"candidate",
        "limitations":["BP not documented"]}]
    text=render_inventory(d,"20261115T000000Z")
    assert "- DOI: Not provided" in text
    assert "- Signals: ECG" in text

def test_missing_optional_fields_are_labelled_unknown():
    result=render_inventory([{"name":"N","url":"https://example.org"}],"20261115")
    assert "- Access: Not provided" in result
    assert "- Signals: Not provided" in result
    assert "- Status: Not provided" in result
    assert "Not documented" in result

def test_registry_with_multiple_different_schemas(tmp_path):
    datasets=[{"name":"A","url":"https://example.org/A","doi":"10.1/a",
               "signals":["ECG"],"limitations":[]},
              {"name":"B","url":"https://example.org/B","access":"registered",
               "signals":["PSG","ECG"],"limitations":["No BRS"]}]
    registry=tmp_path/"datasets.json"
    registry.write_text(json.dumps({"datasets":datasets}))
    output=main(registry=registry,directory=tmp_path/"out")
    assert output.exists()
    txt=output.read_text()
    assert "## A" in txt and "## B" in txt
    assert "- DOI: Not provided" in txt

def test_invalid_dataset_identity_rejected():
    with pytest.raises(ValueError,match="name and source"):
        render_inventory([{"name":"No URL"}],"20261115")
