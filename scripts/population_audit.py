"""Publish population generalizability limitations from existing cloud cohort metadata."""
import json
from pathlib import Path
from anslab.population import audit_population_coverage

def main():
    root = Path("reports")
    source = json.loads((root / "physionet_cohort.json").read_text(encoding="utf-8"))
    config = json.loads(Path("config/population_framework.json").read_text(encoding="utf-8"))
    results = audit_population_coverage(source["records"], config)
    root.mkdir(exist_ok=True)
    (root / "population_coverage.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    n = results["participant_count"]
    lines = [
        "# ANS-001 — Population coverage and missingness audit",
        "",
        f"Source: {results['dataset']}",
        f"Participants audited: {n}",
        "",
        "## Variables actually observed in the current cohort",
        "",
        "| Variable | Known participants | Not known |",
        "|---|---:|---:|",
    ]
    for key, count in results["observed_counts"].items():
        lines.append(f"| {key} | {count} | {n-count} |")
    lines += [
        "", "## Clinical and developmental population coverage", "",
        "| Target | Status |",
        "|---|---|",
        "| Pregnant / nonpregnant and postpartum | UNKNOWN — not recorded |",
        "| Premenopause / perimenopause / postmenopause | UNKNOWN — not recorded |",
        "| Coronary stents, PCI and cardiovascular disease history | UNKNOWN — not recorded; screened healthy-volunteer sample |",
        "| Athletes / physical training status | UNKNOWN — not recorded |",
        "| Children younger than 18 | ABSENT — adult dataset |",
        "",
        "**UNKNOWN is not the same as NO.** Healthy-volunteer eligibility does not independently identify any participant's reproductive or training status.",
        "",
        "## Selected age-group counts",
        ""
    ]
    for band, count in results["selected_age_strata"].items():
        lines.append(f"- {band}: {count}")
    lines += [
        "", "## Allowed and prohibited inference", "",
        "- Allowed: exploratory adult HRV/BRS signal-processing feasibility and transparent quality metrics.",
        "- Not allowed: pregnancy/menopause/PCI/athlete subgroup comparisons, pediatric results, health risk or longevity predictions.",
        "- Any group-specific comparison requires an externally verified phenotype and a suitable study design.",
        "",
        "Protocol: [Population Stratification](../docs/POPULATION_STRATIFICATION.md)",
        "Source: https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/",
    ]
    (root / "POPULATION_COVERAGE.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"Population coverage audited: {n} participants; {len(results['unmeasured_fields'])} fields not observed")

if __name__ == "__main__":
    main()
