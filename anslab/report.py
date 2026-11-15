import json
from pathlib import Path
from datetime import datetime, timezone
from .audit import audit

def write_report(records, queries, directory="reports"):
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    check = audit(records)
    payload = {"project": "ANS-003", "generated_utc": timestamp,
               "queries": queries, "records": records, "audit": check}
    json_path = folder / f"scout_{timestamp}.json"
    md_path = folder / f"scout_{timestamp}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# ANS-003 Literature Scout", "",
             f"Generated UTC: {timestamp}", f"Records: {len(records)}",
             f"Audit: {check['status']}", "",
             "**Limitation:** " + check["limitation"], "",
             "## Search queries"] + [f"- {q}" for q in queries]
    lines += ["", "## Retrieved publications"]
    for r in records:
        lines.append(f"- [{r['title']}]({r['url']}) — {r['journal']} ({r['published']}); PMID {r['pmid']}. **Metadata only.**")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
