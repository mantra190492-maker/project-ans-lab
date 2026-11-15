"""Tests of the founder charter and scientific maturity veto gates."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from scripts.check_research_guardrails import (
    MISSION_ID, NORTH_STAR, GATE_IDS, check_repository,
    validate_charter, validate_proposal,
)

ROOT=Path(__file__).resolve().parents[1]


class ResearchGuardrailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.charter=json.loads((ROOT/"config/research_charter.json").read_text())
        cls.proposal=json.loads((ROOT/"research/proposals/AFDV-001.json").read_text())

    def test_current_repository_passes_schema(self):
        self.assertEqual(check_repository(ROOT),[])

    def test_original_discovery_mission_cannot_silently_become_age(self):
        changed=copy.deepcopy(self.charter)
        changed["north_star"]="Build a consumer biological age tracker"
        self.assertTrue(any("mission changed" in problem for problem in validate_charter(changed)))

    def test_mortality_cannot_silently_replace_deterioration(self):
        changed=copy.deepcopy(self.charter)
        changed["primary_endpoint"]="All-cause mortality risk"
        self.assertTrue(any("Primary endpoint changed" in problem for problem in validate_charter(changed)))

    def test_new_hypothesis_must_have_a_falsification_rule(self):
        proposal=copy.deepcopy(self.proposal)
        proposal["rejection_rule"]=""
        self.assertTrue(any("Missing rejection_rule" in problem for problem in validate_proposal(proposal,self.charter)))

    def test_unvalidated_marker_cannot_be_promoted_to_clinically_valid(self):
        proposal=copy.deepcopy(self.proposal)
        proposal["claim_level"]="CLINICAL_VALIDITY"
        problems=validate_proposal(proposal,self.charter)
        self.assertTrue(any("G3_REFERENCE not passed" in problem for problem in problems))
        self.assertTrue(any("G5_INCREMENTAL not passed" in problem for problem in problems))

    def test_unreviewed_novelty_is_not_a_pass(self):
        proposal=copy.deepcopy(self.proposal)
        proposal["gates"]["G2_PRIOR_ART"]={"status":"PASS","evidence_ref":"","note":"Novel"}
        self.assertTrue(any("G2_PRIOR_ART cannot pass" in problem for problem in validate_proposal(proposal,self.charter)))

    def test_agent_cannot_approve_mission_pivot(self):
        proposal=copy.deepcopy(self.proposal)
        proposal["founder_authorized_mission_change"]=True
        self.assertTrue(any("cannot authorize" in problem for problem in validate_proposal(proposal,self.charter)))

    def test_all_six_gates_are_mandatory(self):
        proposal=copy.deepcopy(self.proposal)
        del proposal["gates"]["G3_REFERENCE"]
        self.assertTrue(any("all six evidence gates" in problem for problem in validate_proposal(proposal,self.charter)))

    def test_budget_guard(self):
        proposal=copy.deepcopy(self.proposal)
        proposal["monthly_budget_usd"]=200
        self.assertTrue(any("budget exceeds" in problem for problem in validate_proposal(proposal,self.charter)))


if __name__=="__main__":
    unittest.main()
