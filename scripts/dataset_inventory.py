"""Generate a transparent, machine-readable dataset inventory without downloading patient signals."""
import json
from pathlib import Path
from datetime import datetime, timezone

def main():
    inventory = json.loads(Path("config/datasets.json").read_text(encoding="utf-8"))
    out = Path("reports")
    out.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["# ANS-001 Dataset Inventory", "", f"Generated UTC: {stamp}", ""]
    for dataset in inventory["datasets"]:
        lines.extend([
            f"## {dataset['name']}", "",
            f"- Source: {dataset['url']}",
            f"- DOI: {dataset['doi']}",
            f"- Access: {dataset['access']}",
            f"- Signals: {', '.join(dataset['signals'])}",
            f"- Status: {dataset['status']}",
            "- Limitations:",
        ])
        lines.extend(f"  - {x}" for x in dataset["limitations"])
        lines.append("")
    (out / f"dataset_inventory_{stamp}.md").write_text("\n".join(lines), encoding="utf-8")
    print("Dataset inventory generated")

if __name__ == "__main__":
    main()
