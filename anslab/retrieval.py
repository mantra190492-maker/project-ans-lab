"""Authorized PubMed E-utilities retrieval, metadata only."""
import time
import requests

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HEADERS = {"User-Agent": "ProjectANS-Lab/0.1 (research; public-metadata)"}

def pubmed_search(query, limit=12, timeout=20, session=None):
    client = session or requests
    response = client.get(BASE + "esearch.fcgi", params={
        "db": "pubmed", "term": query, "retmode": "json", "retmax": limit
    }, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json().get("esearchresult", {}).get("idlist", [])

def pubmed_summaries(pmids, timeout=20, session=None):
    if not pmids:
        return []
    client = session or requests
    response = client.get(BASE + "esummary.fcgi", params={
        "db": "pubmed", "id": ",".join(pmids), "retmode": "json"
    }, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    payload = response.json().get("result", {})
    records = []
    for pmid in pmids:
        item = payload.get(str(pmid), {})
        if not item:
            continue
        records.append({
            "pmid": str(pmid),
            "title": item.get("title", ""),
            "published": item.get("pubdate", ""),
            "journal": item.get("fulljournalname", ""),
            "url": "https://pubmed.ncbi.nlm.nih.gov/" + str(pmid) + "/",
            "source_type": "PubMed bibliographic metadata",
            "verified_full_text": False
        })
    return records

def discover(queries, limit=12, timeout=20, sleep_seconds=0.4):
    all_records = {}
    for query in queries:
        ids = pubmed_search(query, limit, timeout)
        time.sleep(sleep_seconds)
        for record in pubmed_summaries(ids, timeout):
            record.setdefault("matched_queries", []).append(query)
            if record["pmid"] in all_records:
                all_records[record["pmid"]]["matched_queries"].append(query)
            else:
                all_records[record["pmid"]] = record
        time.sleep(sleep_seconds)
    return list(all_records.values())
