# Project ANS Lab

**Mission ANS-001:** Determine whether reproducible autonomic physiology measurements can provide *incremental prediction* of future cardiovascular or functional deterioration beyond age, resting heart rate, standard HRV and established clinical risk factors.

**Status: early research, NOT a clinical product or validated longevity biomarker.** No model has demonstrated extended lifespan, and no Project ANS outcome-prediction model has yet been fitted.

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

## Core research decision

1. **Candidate to test first:** HRF **PIP** compared with clinical baseline + mean HR + standard HRV in verified sinus-rhythm MUSIC Holters. This marker was already published; the opportunity is independent replication and potential incremental clinical value.
2. **Second experimental direction:** HR/BP **recovery following challenge** (stand, stress) when properly labelled longitudinal data are available.
3. **Parallel engineering validation:** Spontaneous cardiac **BRS** using methods, synchronization, respiration sensitivity, surrogate controls and actual BP/ECG reference measurements.
4. **Do not combine them into an "Autonomic Resilience Index" yet**. Only measurements that survive analytical validity, prospective outcomes and external validation can contribute.

## Running and cost

Python 3.11+; research-only open-source libraries. The literature scout uses `requirements-scout.txt`, daily schedule 09:00 UTC in [ANS Literature Scout](.github/workflows/daily-research.yml). Physiological experiments are independent GitHub Actions workflows. Budget target: **under USD 50/month**, using small bounded waveform samples rather than bulk data downloads.

Most research outputs live in `reports/`, and experiment definitions in `docs/`. All individual clinical participants are de-identified in original sources and **not** included as patient-level files in this repository. Aggregate research summaries must not be interpreted as individual diagnosis, treatment advice or proven longevity interventions.

**Secondary track:** ANS-003 neuromuscular-disease differentiation is exploratory and is not the primary scientific mission.
