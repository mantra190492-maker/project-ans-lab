"""Population-data availability audit. Missing values must never be treated as negatives."""
from collections import Counter

def audit_population_coverage(records, framework):
    if not isinstance(records, list) or not records:
        raise ValueError("Nonempty participant records required")
    if framework.get("current_dataset", {}).get("name") != "PhysioNet Autonomic Aging v1.0.0":
        raise ValueError("This audit targets the documented PhysioNet healthy-adult dataset only")
    source = framework["current_dataset"]
    available = ("age_group", "sex_code", "bmi", "device_code")
    measured = {field: sum(r.get(field) is not None for r in records)
                for field in available}
    unmeasured = list(source["not_documented_individually"])
    # Explicitly refuse to infer a phenotype when not measured in the source.
    contradictions = [field for field in unmeasured
                      if any(r.get(field) is not None for r in records)]
    if contradictions:
        raise ValueError(
            "Source metadata conflicts with declared availability: "
            + ", ".join(contradictions)
            + ". Verify provenance and update the source inventory before inference."
        )
    age_values = [int(r["age_group"]) for r in records
                  if r.get("age_group") is not None]
    if any(age < 1 or age > 15 for age in age_values):
        raise ValueError("Unexpected age-group codes")
    counts = Counter(r.get("age_stratum", "not_recorded") for r in records)
    return {
        "study":"ANS-001 population coverage audit",
        "dataset":source["name"],
        "participant_count":len(records),
        "observed_counts":measured,
        "selected_age_strata":dict(sorted(counts.items())),
        "children_under_18_included":False,
        "children_status":"absent_by_study_eligibility_18_to_92_years",
        "unmeasured_fields":{field:"unknown_not_measured" for field in unmeasured},
        "cannot_infer":[
            "pregnancy/nonpregnancy",
            "pre-/peri-/postmenopause",
            "history of PCI or coronary stents",
            "athlete/nonathlete",
            "future health outcomes or longevity"
        ],
        "inference_status":"HOLD: adult resting engineering pilot only"
    }
