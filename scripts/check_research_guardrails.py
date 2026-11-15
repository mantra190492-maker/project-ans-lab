"""ANS-001 mission and research-stage guardrails.

Scope: deterministic review checks ONLY. Cannot independently verify scientific
truth, evidence quality, clinical diagnoses or a founder's approval.
"""
import json
import sys
from pathlib import Path

MISSION_ID = "ANS-001"
NORTH_STAR = (
    "Discover and validate a genuinely differentiated physiological marker "
    "that detects autonomic nervous system dysfunction or longitudinal deterioration."
)
PRIMARY_ENDPOINT = (
    "Independently confirmed autonomic dysfunction or worsening of autonomic function, "
    "with domain-specific clinically appropriate reference testing."
)
GATE_IDS = (
    "G1_TARGET", "G2_PRIOR_ART", "G3_REFERENCE",
    "G4_ANALYTICAL", "G5_INCREMENTAL", "G6_REPLICATION",
)
LEVELS = (
    "IDEA", "PRIOR_ART_SCREENED", "MEASUREMENT_FEASIBILITY",
    "ANALYTICAL_VALIDITY", "CLINICAL_VALIDITY", "INDEPENDENT_REPLICATION",
)
GATE_STATES = ("OPEN", "PARTIAL", "BLOCKED", "PASS")


def validate_charter(charter):
    issues = []
    if charter.get("schema_version") != 1:
        issues.append("Unsupported charter schema version")
    if charter.get("mission_id") != MISSION_ID:
        issues.append("Founder mission ID changed")
    if charter.get("mission_status") != "LOCKED_BY_FOUNDER_INTENT":
        issues.append("Founder mission lock removed")
    if charter.get("north_star") != NORTH_STAR:
        issues.append("Primary discovery mission changed: require explicit founder approval and documented governance revision")
    if charter.get("primary_endpoint") != PRIMARY_ENDPOINT:
        issues.append("Primary endpoint changed: clinical ANS dysfunction/progression must remain primary")
    if tuple(charter.get("evidence_levels", [])) != LEVELS:
        issues.append("Scientific claim maturity levels changed")
    if tuple(g.get("id") for g in charter.get("gates", []) if isinstance(g, dict)) != GATE_IDS:
        issues.append("G1-G6 evidence gate requirements were changed")
    if not isinstance(charter.get("cost_ceiling_usd_per_month"), (int, float)) or charter["cost_ceiling_usd_per_month"] > 50:
        issues.append("Budget ceiling above USD 50/month")
    return issues


def validate_proposal(proposal, charter):
    issues = []
    ident = proposal.get("proposal_id", "UNNAMED")
    def missing(field):
        return not isinstance(proposal.get(field), str) or not proposal[field].strip()

    if proposal.get("mission_id") != charter.get("mission_id"):
        issues.append(f"{ident}: Proposal is detached from ANS-001 mission")
    if proposal.get("track") not in ("discovery", "supporting_measurement", "secondary_relevance"):
        issues.append(f"{ident}: Must classify track as discovery / supporting_measurement / secondary_relevance")
    for field in ("candidate_name", "scientific_claim", "clinical_target", "population",
                  "novelty_gap", "reference_standard", "next_falsifiable_test", "rejection_rule"):
        if missing(field):
            issues.append(f"{ident}: Missing {field}")
    if proposal.get("claim_level") not in LEVELS:
        issues.append(f"{ident}: Invalid evidence maturity claim")
    try:
        budget=float(proposal["monthly_budget_usd"])
        if budget < 0 or budget > charter["cost_ceiling_usd_per_month"]:
            issues.append(f"{ident}: Proposed monthly budget exceeds authorized research ceiling")
    except (ValueError, TypeError, KeyError):
        issues.append(f"{ident}: Invalid or missing proposed budget")
    if not isinstance(proposal.get("available_data"), list) or not proposal["available_data"]:
        issues.append(f"{ident}: Must disclose what datasets are actually available or unavailable")
    gates=proposal.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(GATE_IDS):
        issues.append(f"{ident}: Must report all six evidence gates")
        return issues
    for gate in GATE_IDS:
        value=gates[gate]
        if not isinstance(value, dict):
            issues.append(f"{ident}: Invalid {gate} decision object")
            continue
        state=value.get("status")
        if state not in GATE_STATES:
            issues.append(f"{ident}: Invalid {gate} status")
        if not isinstance(value.get("note"), str) or not value["note"].strip():
            issues.append(f"{ident}: {gate} must explain its current state")
        if state == "PASS" and (not isinstance(value.get("evidence_ref"), str) or not value["evidence_ref"].strip()):
            issues.append(f"{ident}: {gate} cannot pass without a reviewable evidence reference")

    stage=proposal.get("claim_level")
    needed = {
        "PRIOR_ART_SCREENED":("G1_TARGET","G2_PRIOR_ART"),
        "MEASUREMENT_FEASIBILITY":("G1_TARGET","G2_PRIOR_ART"),
        "ANALYTICAL_VALIDITY":("G1_TARGET","G2_PRIOR_ART","G4_ANALYTICAL"),
        "CLINICAL_VALIDITY":("G1_TARGET","G2_PRIOR_ART","G3_REFERENCE","G4_ANALYTICAL","G5_INCREMENTAL"),
        "INDEPENDENT_REPLICATION":GATE_IDS,
    }.get(stage, ())
    for gate in needed:
        if gates.get(gate, {}).get("status") != "PASS":
            issues.append(f"{ident}: Cannot claim {stage} with {gate} not passed")

    if proposal.get("track") != "discovery" and stage in ("CLINICAL_VALIDITY","INDEPENDENT_REPLICATION"):
        issues.append(f"{ident}: Secondary/supporting project cannot automatically become the primary ANS discovery")
    if proposal.get("founder_authorized_mission_change") is True:
        issues.append(f"{ident}: A proposal field cannot authorize changes to the primary mission")
    return issues


def check_repository(root):
    root=Path(root)
    problems=[]
    try:
        charter=json.loads((root/"config/research_charter.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ["Cannot load founder charter: "+str(exc)]
    problems.extend(validate_charter(charter))
    proposal_dir=root/"research/proposals"
    paths=sorted(proposal_dir.glob("*.json"))
    if not paths:
        problems.append("At least one auditable research hypothesis proposal is required")
    for path in paths:
        try:
            proposal=json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{path}: Invalid proposal JSON: {exc}")
            continue
        if proposal.get("proposal_id") != path.stem:
            problems.append(f"{path}: filename does not match proposal_id")
        problems.extend(validate_proposal(proposal, charter))
    return problems


def main():
    root=Path(__file__).resolve().parents[1]
    problems=check_repository(root)
    if problems:
        print("Project ANS research governance CHECK FAILED:")
        for message in problems:
            print(" - "+message)
        return 1
    print("Project ANS governance CHECK PASSED.")
    print("Founder mission unchanged; proposals are staged and do not overclaim clinical validation.")
    print("This is a documentation/software gate, NOT independent scientific verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
