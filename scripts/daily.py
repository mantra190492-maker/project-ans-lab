import json
import time
from pathlib import Path
from datetime import datetime, timezone
import requests

QUERIES = [
    '"autonomic nervous system" AND (aging OR ageing) AND (biomarkers OR resilience)',
    '"heart rate variability" AND (aging OR ageing) AND (longitudinal OR mortality)',
    '"orthostatic" AND (aging OR ageing) AND (heart rate OR blood pressure)',
    '"baroreflex sensitivity" AND (aging OR ageing) AND (functional decline OR frailty)',
]

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HEADERS = {"User-Agent": "ProjectANS-Lab/0.1 (public research metadata)"}

def retrieve():
    records = {}
    for query in QUERIES:
        r = requests.get(BASE + "esearch.fcgi", params={"db":"pubmed","term":query,"retmax":12,"retmode":"json"}, headers=HEADERS, timeout=25)
        r.raise_for_status()
        ids = r.json()["esearchresult"].get("idlist", [])
        time.sleep(0.4)
        if not ids:
            continue
        r = requests.get(BASE + "esummary.fcgi", params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, headers=HEADERS, timeout=25)
        r.raise_for_status()
        result = r.json().get("result", {})
        for pmid in ids:
            item = result.get(pmid, {})
            if not item:
                continue
            if pmid not in records:
                records[pmid] = {"pmid":pmid,"title":item.get("title",""),"journal":item.get("fulljournalname",""),"published":item.get("pubdate",""),"url":f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/","queries":[],"evidence_level":"bibliographic metadata only"}
            records[pmid]["queries"].append(query)
        time.sleep(0.4)
    return list(records.values())

def main():
    records = retrieve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = Path("reports")
    folder.mkdir(exist_ok=True)
    (folder / f"scout_{stamp}.json").write_text(json.dumps({"project":"ANS-001","generated_utc":stamp,"queries":QUERIES,"records":records,"limitation":"Metadata alone cannot establish diagnostic accuracy, clinical efficacy, or novelty."},indent=2), encoding="utf-8")
    lines = ["# ANS-001 Literature Scout", "",f"Generated: {stamp} UTC",f"Records: {len(records)}","","**Metadata only; findings require full-text review and independent validation.**",""]
    lines.extend(f"- [{r['title']}]({r['url']}) — {r['journal']} ({r['published']}); PMID {r['pmid']}" for r in records)
    (folder / f"scout_{stamp}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Saved {len(records)} records.")

if __name__ == "__main__":
    main()
