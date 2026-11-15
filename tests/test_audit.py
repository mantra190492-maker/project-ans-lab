from anslab.audit import audit
from anslab.report import write_report

def test_valid_record():
    r = {"pmid":"123", "title":"Study", "url":"https://pubmed.ncbi.nlm.nih.gov/123/", "verified_full_text":False}
    assert audit([r])["status"] == "PASS"

def test_duplicates_rejected():
    r = {"pmid":"123", "title":"Study", "url":"https://pubmed.ncbi.nlm.nih.gov/123/", "verified_full_text":False}
    assert audit([r,r])["status"] == "FAIL"

def test_report(tmp_path):
    a,b = write_report([], ["muscle weakness"], tmp_path)
    assert a.exists() and b.exists()
    assert "Metadata-only" in b.read_text()
