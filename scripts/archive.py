"""Persist daily research metadata with PMID-based deduplication and an audit trail."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("reports")
LIBRARY = ROOT / "library.json"
INDEX = ROOT / "README.md"

def main():
    reports = sorted(ROOT.glob("scout_*.json"))
    if not reports:
        raise SystemExit("No scout report to archive")
    newest = json.loads(reports[-1].read_text(encoding="utf-8"))
    previous = json.loads(LIBRARY.read_text(encoding="utf-8")) if LIBRARY.exists() else {"records":{}, "runs":[]}
    records = previous.get("records",{})
    new_count = 0
    for paper in newest.get("records",[]):
        pmid = str(paper.get("pmid","")).strip()
        if not pmid:
            continue
        if pmid not in records:
            records[pmid] = {**paper, "first_seen_utc":newest["generated_utc"],"review_status":"unreviewed"}
            new_count += 1
        else:
            old = records[pmid]
            old["last_seen_utc"] = newest["generated_utc"]
            old["queries"] = sorted(set(old.get("queries",[]) + paper.get("queries",[])))
    previous["records"] = records
    previous.setdefault("runs",[]).append({"timestamp":newest["generated_utc"],"retrieved":len(newest.get("records",[])),"new":new_count,"total_unique":len(records)})
    LIBRARY.write_text(json.dumps(previous,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines = ["# Project ANS — Research Observatory", "",
             "## Latest run", "",
             f"- Date (UTC): {newest['generated_utc']}",
             f"- Publications retrieved: {len(newest.get('records',[]))}",
             f"- Newly discovered: {new_count}",
             f"- Total unique publications archived: {len(records)}", "",
             "## Recent activity", "",
             "| Run (UTC) | Retrieved | New | Total unique |",
             "|---|---:|---:|---:|"]
    for run in reversed(previous["runs"][-30:]):
        lines.append(f"| {run['timestamp']} | {run['retrieved']} | {run['new']} | {run['total_unique']} |")
    lines += ["", "## Evidence policy", "",
              "This library stores bibliographic metadata, **not validated scientific findings**.",
              "Each paper remains unreviewed until methods and findings are independently assessed.",
              "The initial 46-paper run is not included retroactively unless imported from its original report.",
              "", "## Full library", "",
              "See [library.json](library.json) for PMIDs, source URLs, and review status."]
    INDEX.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Archived: {new_count} new, {len(records)} total unique")

if __name__ == "__main__":
    main()
