"""Render the dataset registry with explicit missing values and stable output."""
import json
from datetime import datetime, timezone
from pathlib import Path


def _value(value):
    if value is None or value == "":
        return "Not provided"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "Not provided"
    return str(value)


def render_inventory(datasets, generated_utc):
    if not isinstance(datasets, list):
        raise ValueError("The dataset registry must contain a list of datasets")
    lines = ["# ANS-001 Dataset Inventory", "",
             f"Generated UTC: {generated_utc}", "",
             "**Unknown metadata is not evidence of absence.**", ""]
    for item in datasets:
        if not isinstance(item, dict):
            raise ValueError("Dataset entries must be objects")
        if not item.get("name") or not item.get("url"):
            raise ValueError("Each dataset requires an identifiable name and source URL")
        lines.extend([
            f"## {item['name']}", "",
            f"- Source: {item['url']}",
            f"- DOI: {_value(item.get('doi'))}",
            f"- Access: {_value(item.get('access'))}",
            f"- Signals: {_value(item.get('signals'))}",
            f"- Status: {_value(item.get('status'))}",
            "- Limitations:",
        ])
        limits = item.get("limitations") or ["Not documented"]
        if not isinstance(limits, list):
            raise ValueError("Limitations must be an array")
        lines.extend(f"  - {limit}" for limit in limits)
        lines.append("")
    return "\n".join(lines) + "\n"


def main(registry="config/datasets.json", directory="reports"):
    data = json.loads(Path(registry).read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    text = render_inventory(data["datasets"], stamp)
    dest = Path(directory)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"dataset_inventory_{stamp}.md"
    path.write_text(text, encoding="utf-8")
    print(f"Dataset inventory generated: {len(data['datasets'])} datasets, {path}")
    return path


if __name__ == "__main__":
    main()
