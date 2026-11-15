# Project ANS — Research guardrails (founder mission control)

**Effective:** 2026-11-15. **Source of truth:** [research_charter.json](../config/research_charter.json). The primary mission is locked to the founder's research intent, **not** to the current most convenient dataset or commercial idea.

> Discover and validate a genuinely differentiated physiological marker that detects autonomic nervous system dysfunction or longitudinal deterioration.

## Binding decision rules

1. **No scope drift.** Age clocks, mortality prediction, MUSIC cardiac death, diabetes screening, wellness apps, and commercial models are **secondary only**. They cannot silently become the purpose of Project ANS. Never present the easiest viable business as if it answers our discovery objective.
2. **No novelty claims without a novelty test.** Before calling a marker "new," document exact formulas, inputs, physiology, reference method, outcome, prior studies/patents and the precise original element. "We combined HRV, BRS, HRF" is not invention. A *proposed* new equation is only a hypothesis.
3. **Clinical target must be explicit.** "ANS deterioration" is not a single clinically established disease. Each proposal identifies the specific affected functional domain, study population, independent diagnostic/physiological reference, and whether the goal is current dysfunction or longitudinal worsening.
4. **Two different truths.** **Engineering success** (readable signals, high beat F1, stable formula) is never described as **clinical biomarker validity** (actual dysfunction discrimination). Clinical prediction is never called ANS diagnosis unless the endpoint is an independent autonomic reference.
5. **Existing standards are the baseline.** Include relevant autonomic reflex testing / CASS domains where available, established individual measures, medications, rhythm/respiration/posture and a clinically meaningful comparison. Do not compare against weak straw-man baselines.
6. **Falsification before execution.** Every experiment has an explicit negative result / stop rule, reproducibility criterion, dataset rights, cost and expected scientific decision. Failed results remain in the research record.
7. **No cheap-data substitution.** If outcome-labelled clinical data are unavailable, label the test **engineering-only / blocked for clinical validity**. No agent's convincing argument can transform healthy-only recordings into disease labels.
8. **No unapproved pivots.** Agents can propose new directions but cannot set our mission. Only the founder can authorize a scope change; record the rationale and evidence before updating the mission. A new commercial niche must be considered separately.
9. **Cost discipline.** Default to under USD 50/month. No device build, subscriptions, bulk download or clinical expenditure merely because an agent proposes it.
10. **No overstating success.** Report exact dataset counts, failures, missingness and verification status. Claims must be labelled **hypothesis / analytical feasibility / clinically validated / independently replicated**.

## Gate table

| Gate | Required question | If unmet |
|---|---|---|
| G1 Target | What exact autonomic impairment or deterioration is being detected? | Do not frame as a clinical marker |
| G2 Prior art | What precise method, physiological relationship or use is genuinely not established? | Classify as replication / unproven originality |
| G3 Reference | What independent physiological/clinical reference can validate this? Is it accessible? | HOLD clinical claims |
| G4 Analytical | Is the measure robust to noise, timing, repeat visits, drugs and posture? | Engineering only |
| G5 Incremental | Does it beat relevant clinical tests/established markers, with adequate sample sizes? | No clinical utility claim |
| G6 Replication | Does it reproduce in a separate cohort/device/context? | No generalizable or commercial biomarker claim |

**A missing gate is never silently interpreted as passed.** A proposal may still exist as an IDEA or measurement experiment, but it cannot be promoted to validated discovery.

## Agent intake and decisions

Every new agent report gets one short **Claim / Source / Prior art / Independent reference / Falsifier / Cost / Decision** entry in [the evidence board](AGENT_EVIDENCE_COMPARISON_BOARD.md). Distinguish the agent's assertions from independently verified evidence. Sort reports by *whether they resolve one of G1–G6*, not how persuasive the prose is.

**Default response to commercial pushback:** Evaluate the argument as a secondary market hypothesis, state its relevance to the unchanged ANS deterioration mission, and do **not** redirect the primary laboratory.

## Current program snapshot

- **AFDV**: Proposed domain-specific functional deterioration formulation; scientific originality, physiological reliability and clinical reference validation **unproven**.
- **PRCP and Fantasia**: Engineering/annotation feasibility only. Ten healthy PRCP subjects cannot verify a disease marker.
- **MUSIC**: Cardiac prognosis benchmark, not direct autonomic deterioration diagnosis.
- **ANS clinical label access**: Still needed for genuine validation (appropriate autonomic reflex testing / independent adjudication).
- **Valid original biomarker**: **zero** at this date.

## Repository-level enforcement

The checker `scripts/check_research_guardrails.py` validates the charter and structured research proposals in `research/proposals/`. A [GitHub Action](../.github/workflows/research-guardrails.yml) runs the check. This is a **schema/consistency guard**, **not** proof that a citation is valid or that a scientist has approved a biomarker. Because the repository currently permits direct writes to `main`, the check is an alert, not an unbypassable branch-protection rule. Branch protection / required checks and code-owner review would further strengthen enforcement.

**Review discipline:** Before each substantive change, restate (internally) the unchanged mission; classify proposed work as (a) discovery, (b) supporting measurement validation, or (c) secondary business/relevance; reject anything that cannot advance or explicitly challenge a gate.
