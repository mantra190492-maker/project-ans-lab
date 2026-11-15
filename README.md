# Project ANS Lab

> **FOUNDER RESEARCH CHARTER — LOCKED:** [Read the mission and six evidence gates](docs/RESEARCH_GUARDRAILS.md) · [Decision log](docs/RESEARCH_DECISION_LOG.md) · [Machine-readable charter](config/research_charter.json) · [Open hypothesis and blocked gates](research/proposals/AFDV-001.json). Do **not** change the primary objective to ageing, mortality, a generic HRV product, or diabetic screening because an external agent recommends it. Only explicit founder approval can authorize a pivot. **No new clinically validated ANS biomarker exists yet.**

**Mission ANS-001:** Find and validate objective physiological markers that **detect emerging autonomic nervous system dysfunction, localize affected functional domains, and track deterioration over repeated tests**. The primary endpoints are independently assessed autonomic impairment/progression, **not biological age or lifespan**. Mortality and CVD prediction are secondary external relevance benchmarks.

**Status: early research, NOT a clinically validated autonomic dysfunction detector.** A validated clinical autonomic reflex screen and CASS already exist. ECG/BP measures only cardiovagal and adrenergic responses; sudomotor assessment needs additional tests. No predictive clinical-deterioration model has been validated.

**[Primary research formulation — detect ANS functional deterioration](docs/FORMULATION_001_AUTONOMIC_FUNCTION_DETERIORATION.md)**. We propose domain-specific repeat-visit changes compared with clinical autonomic-reflex/CASS standards. This is a hypothesis, not a proven new marker.

## Research overview

| Track | Current grounded status | Detailed evidence |
|---|---|---|
| Daily evidence collection | PubMed queries run on a daily schedule; a permanent PMID-deduplicated archive contains **46 bibliographic records** (not full-paper reviews) | [Research Observatory](reports/README.md) |
| Adult ECG/BP engineering | 20 PhysioNet adult recordings processed; 19 automated ECG-quality checks passed; 12 provisional BRS results. **No validated clinical BRS measurements** | [Cohort report](reports/COHORT_001_SUMMARY.md), [quality audit](docs/COHORT_001_AUDIT.md) |
| Independently annotated ECG | Four Fantasia ECG windows checked against visually verified beat annotations: F1 1.000 at 150 ms tolerance; limited scope | [Fantasia benchmark](reports/FANTASIA_ECG_BENCHMARK.md) |
| Cardiovascular outcome data | MUSIC public metadata feasibility: 992 people, 587 with standard HRV; outcomes/censoring data recorded. **No prediction model fitted** | [MUSIC audit](reports/MUSIC_METADATA_AUDIT.md), [experiment plan](docs/MUSIC_OUTCOME_MODEL_PROTOCOL_001.md) |
| Heart-rate fragmentation | PIP/W1 calculation with explicit beat-gap, sampling-quantization and sinus-rhythm guards; synthetic tests and a small annotated beat pilot | [Measurement code](anslab/heart_rate_fragmentation.py), [pilot workflow](.github/workflows/fantasia-hrf-pilot.yml) |
| Pregnant, menopausal, pediatric, athlete, coronary-stent populations | Unobserved or absent from healthy adult dataset; require separately labelled cohorts | [Population protocol](docs/POPULATION_STRATIFICATION.md) |

## Independent research and multi-agent evidence review

- **[Living multi-agent evidence board](docs/AGENT_EVIDENCE_COMPARISON_BOARD.md)** — compare external agents' evidence, disagreements and decisions.
- **[Project ANS independent research review (Agents 3–7 topics)](docs/INDEPENDENT_BIOMARKER_REVIEW_2026-11-15.md)** — biomarker discovery, BRS method validation, outcome prediction, dynamic recovery, falsification/novelty.
- [External Agent 01 — source integrity audit](docs/AGENT_01_EVIDENCE_REVIEW.md).
- [External Agent 02 — skeptical research assessment audit](docs/AGENT_02_SKEPTICAL_ASSESSMENT_AUDIT.md).
- [External Agents 04–07 — BRS, MUSIC, dynamic recovery and independent red-team adjudication](docs/EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md).
- [Originality decision and prior-art reset](docs/NOVELTY_RESET_2026-11-15.md).

## Core research decision

1. **Primary discovery objective:** Detect genuine autonomic function deterioration across clinically assessed cardiovagal, adrenergic and (when measured) sudomotor domains. The target is **autonomic dysfunction/progression**, not biological age.
2. **Proposed formulation:** An Autonomic Functional Deterioration Vector (AFDV) based on repeated standardized challenges, domain-specific impairment-oriented change and explicit measurement gaps; validate against CASS and disease-status progression, not self-declared autonomic health.
3. **Supporting measurements:** Continue cardiovagal/adrenergic ECG+BP quality validation, HRF as a known comparator, and open PRCP stand/tilt tests. MUSIC cardiac mortality benchmarking remains **secondary** and does not establish ANS diagnosis.
4. **Do not market a single ANS score.** Clinical gold-standard autonomic reflex and QSART tests cover domains unavailable in our current ECG/BP data; partner access is needed to measure disease progression and prove a new marker.

## Running and cost

Python 3.11+; research-only open-source libraries. The literature scout uses `requirements-scout.txt`, daily schedule 09:00 UTC in [ANS Literature Scout](.github/workflows/daily-research.yml). Physiological experiments are independent GitHub Actions workflows. Budget target: **under USD 50/month**, using small bounded waveform samples rather than bulk data downloads.

Most research outputs live in `reports/`, and experiment definitions in `docs/`. All individual clinical participants are de-identified in original sources and **not** included as patient-level files in this repository. Aggregate research summaries must not be interpreted as individual diagnosis, treatment advice or proven longevity interventions.

**Secondary track:** ANS-003 neuromuscular-disease differentiation is exploratory and is not the primary scientific mission.
