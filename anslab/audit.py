"""Conservative quality gate: metadata is never evidence of efficacy."""
def audit(records):
    seen = set()
    errors = []
    for record in records:
        pmid = record.get("pmid")
        if not pmid or pmid in seen:
            errors.append("missing or duplicate PMID")
        seen.add(pmid)
        if not record.get("title") or not record.get("url", "").startswith("https://pubmed.ncbi.nlm.nih.gov/"):
            errors.append("missing title or invalid source URL")
        if record.get("verified_full_text"):
            errors.append("full-text verification must not be asserted by metadata scout")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors,
            "limitation": "Metadata-only discovery cannot establish clinical findings, novelty, or diagnostic performance."}
