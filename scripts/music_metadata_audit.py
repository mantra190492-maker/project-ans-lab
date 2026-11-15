"""Aggregate-only feasibility audit of public MUSIC chronic heart-failure metadata.

Downloads only the source's published subject-info.csv (~301 KB). Never writes, logs,
or commits per-patient rows, patient IDs, or individual outcomes. Does not fit models.
"""
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import requests

BASE = "https://physionet.org/files/music-sudden-cardiac-death/1.0.1/"
OUT = Path("reports")
MISSING = {"", "NA", "N/A", "NAN", "NONE", "NULL", "999", "-999"}
REQUIRED = {
    "Patient ID", "Follow-up period from enrollment (days)",
    "Cause of death", "Age", "Gender (male=1)", "Body Mass Index (Kg/m2)",
    "Prior Myocardial Infarction (yes=1)", "Prior Revascularization",
    "Holter available", "Betablockers (yes=1)",
    "SDNN (ms)", "RMSSD (ms)",
}
# Header spelling, including trailing whitespace, comes from the published CSV.
# We normalize field names to protect against inconsequential white space.

def normalize_row(row):
    return {k.strip(): (v or "").strip() for k, v in row.items() if k is not None}

REQUIRED = {key.strip() for key in REQUIRED}

def present(value):
    return str(value).strip().upper() not in MISSING

def summarize(rows):
    """Returns aggregates only; never returns individual participant data."""
    if not rows:
        raise ValueError("MUSIC source has no participants")
    rows = [normalize_row(row) for row in rows]
    keys = set(rows[0])
    missing_fields = sorted(REQUIRED - keys)
    if missing_fields:
        raise ValueError("Missing essential columns: " + ", ".join(missing_fields))
    if not (800 <= len(rows) <= 1100):
        raise ValueError("Unexpected MUSIC cohort size; inspect source version")
    identifiers = [r["Patient ID"] for r in rows]
    if len(set(identifiers)) != len(rows):
        raise ValueError("Patient IDs not unique; stop rather than double-count")
    optional_rhythm = next((key for key in keys if key.lower().replace(" ", "") in {"holterrhythm", "holterrhythm;"}), None)
    checked_fields = [
        "Age", "Gender (male=1)", "Body Mass Index (Kg/m2)",
        "Prior Myocardial Infarction (yes=1)", "Prior Revascularization",
        "Follow-up period from enrollment (days)", "Cause of death",
        "Holter available", "Holter rhythm", "Betablockers (yes=1)",
        "SDNN (ms)", "RMSSD (ms)",
    ]
    observed_counts = {f: sum(present(r.get(f, "")) for r in rows) for f in checked_fields}
    revasc = Counter(r["Prior Revascularization"] for r in rows
                     if present(r.get("Prior Revascularization", "")))
    death = Counter(r["Cause of death"] for r in rows
                    if present(r.get("Cause of death", "")))
    rhythm = Counter(r.get(optional_rhythm, "") for r in rows
                     if optional_rhythm and present(r.get(optional_rhythm, "")))
    holter = Counter(r["Holter available"] for r in rows
                     if present(r.get("Holter available", "")))
    allowed_revasc = {"0", "1", "2", "3"}
    unknown_revasc = {c:n for c,n in revasc.items() if c not in allowed_revasc}
    return {
        "source": BASE + "subject-info.csv",
        "version": "1.0.1",
        "participant_rows": len(rows),
        "distinct_participant_identifiers_count": len(set(identifiers)),
        "field_completeness": observed_counts,
        "prior_revascularization_codes": dict(sorted(revasc.items())),
        "prior_revascularization_meanings": {
            "0": "none", "1": "percutaneous", "2": "surgical", "3": "both"
        },
        "unrecognized_revascularization_codes": unknown_revasc,
        "cause_of_death_codes": dict(sorted(death.items())),
        "cause_of_death_meanings": {
            "0": "survivor", "1": "noncardiac death", "3": "sudden cardiac death",
            "6": "pump-failure death", "7": "pump-failure death"
        },
        "holter_available_codes": dict(sorted(holter.items())),
        "holter_rhythm_codes": dict(sorted(rhythm.items())),
        "holter_rhythm_source_column": optional_rhythm,
        "holter_rhythm_status": "present" if optional_rhythm else "not_found_in_metadata_header",
        "interpretation": (
            "DESCRIPTIVE DATA READINESS ONLY. No predictive model fitted; do not "
            "infer stent implantation from percutaneous revascularization; "
            "death code 0 not automatically sufficient to prove censoring completeness."
        ),
        "raw_data_saved": False,
        "patient_level_data_committed": False,
    }

def counts_display(counts):
    # Conservative suppression of small non-zero cells in rendered Markdown.
    return ", ".join(f"{k}: {n if n >= 5 else '<5'}" for k,n in counts.items()) or "No recorded values"

def render(summary):
    lines = [
        "# ANS-001 — MUSIC cardiovascular cohort metadata feasibility audit", "",
        f"Generated UTC: {summary['generated_utc']}",
        f"Source: {summary['source']}",
        "Dataset DOI: 10.13026/z3m7-rf58", "",
        "**No individual patient records were stored or committed. This is not a survival analysis.**", "",
        f"- Participants: **{summary['participant_rows']}**",
        f"- Distinct identifiers: **{summary['distinct_participant_identifiers_count']}**", "",
        "## Observable fields", "",
        "| Field | Nonmissing | Missing |",
        "|---|---:|---:|",
    ]
    n = summary["participant_rows"]
    for field, observed in summary["field_completeness"].items():
        lines.append(f"| {field} | {observed} | {n-observed} |")
    lines += [
        "", "## Coded baseline categories (aggregate counts only)", "",
        f"- Prior revascularization (0 none, 1 percutaneous, 2 surgical, 3 both): {counts_display(summary['prior_revascularization_codes'])}",
        f"- Cause-of-death codes (0 survivor, 1 noncardiac, 3 sudden cardiac, 6-7 pump failure): {counts_display(summary['cause_of_death_codes'])}",
        f"- Holter availability: {counts_display(summary['holter_available_codes'])}",
        f"- Holter rhythm: {counts_display(summary['holter_rhythm_codes'])}", "",
        "## Scientific decision", "",
        "1. Percutaneous revascularization is **not a verified coronary stent**. Do not relabel the field.",
        "2. Baseline HRV metrics and event codes may support a **cardiovascular-disease-specific** benchmark, but this cohort is not a healthy-ageing reference.",
        "3. Missingness, rhythm exclusions, event codes, follow-up/censoring definitions and data leakage must be prespecified before modeling.",
        "4. ECG/BP BRS cannot be calculated here without a matching beat-to-beat BP signal.",
        "5. The full MUSIC waveform archive is around **90 GB uncompressed**; this audit downloads only a small CSV.",
        "6. An outcome risk score that is already published is **prior art**, not Project ANS novelty.", "",
        "Sources:",
        "- [PhysioNet MUSIC v1.0.1](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/)",
        "- [Official outcome/revascularization coding](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/subject-info_codes.csv)",
        "- [Agent 02 scientific audit](../docs/AGENT_02_SKEPTICAL_ASSESSMENT_AUDIT.md)",
    ]
    if summary["unrecognized_revascularization_codes"]:
        lines += ["", "**WARNING:** Unexpected revascularization codes found. Investigate before subgroup modeling."]
    return "\n".join(lines)+"\n"

def main():
    response = requests.get(BASE + "subject-info.csv", timeout=90,
                            headers={"User-Agent": "ProjectANS-Lab/0.4"})
    response.raise_for_status()
    if len(response.content) > 2_000_000:
        raise ValueError("Metadata-only download cap exceeded")
    csvtext = response.content.decode("utf-8-sig", errors="strict")
    rows = list(csv.DictReader(StringIO(csvtext), delimiter=";"))
    report = summarize(rows)
    report["generated_utc"] = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"music_metadata_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8"
    )
    (OUT/"MUSIC_METADATA_AUDIT.md").write_text(render(report), encoding="utf-8")
    print("MUSIC metadata audit completed on", report["participant_rows"], "subjects")
    print("Only aggregate metadata output; no individual patient data retained.")

if __name__ == "__main__":
    main()
