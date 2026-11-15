# Project ANS — Multi-agent scientific evidence board

**Updated:** 2026-11-15  
**Purpose:** Consolidate each LLM agent's independently cited claims, keep disagreements visible, and translate only verified proposals into experimental gates. This board is a **decision log**, not a peer-reviewed systematic literature review.

## Agent coverage

| Contributor | Review scope | Evidence reviewed | Status / artifact |
|---|---|---|---|
| Agent 1 (external LLM) | General longitudinal literature, datasets, biomarkers | Written submission; corrected errors in age dataset size, Framingham author/year, 2007 post-MI BRS and cognitions citations | [Evidence audit](AGENT_01_EVIDENCE_REVIEW.md) |
| Agent 2 (external LLM) | Skeptical prediction, interventions and novel datasets | 19-page report supplied by founder; primary sources and datasets checked selectively | [Skeptical audit](AGENT_02_SKEPTICAL_ASSESSMENT_AUDIT.md) |
| **Independent Project ANS review** | **All five tracks: biomarker, BRS, prediction, recovery and skepticism** | Primary papers and provider documentation; no new survival model fitted | [Full independent review](INDEPENDENT_BIOMARKER_REVIEW_2026-11-15.md) |
| Agent 3 (external, pending) | Biomarker discovery | Standalone submission not included in this four-PDF batch | Awaiting report |
| Agent 4 (external PDF 2) | BRS method validity | BRS validation, 10-page report; BaroKit/PRCP identified; 90% yield gate proposed, not established | [Batch adjudication](EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md) |
| Agent 5 (external PDF 3) | Clinical outcome prediction | MUSIC protocol, 9-page report; stronger deceleration-capacity comparator; transplant and drug assertions corrected | [Batch adjudication](EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md) |
| Agent 6 (external PDF 4) | Dynamic physiological recovery | 9-page report; Panaite meta and PRCP accepted; 12-year TILDA 'preprint' claim obsolete | [Batch adjudication](EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md) |
| Agent 7 (external PDF 5) | Prior art / critical falsification | 7-page red-team report; existing Polyscore and HRF patent application verified; originality remains unproven | [Batch adjudication](EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md) |

## Consensus, disagreement and decision

| Claim | Agent 1 | Agent 2 | Independent Project ANS assessment | Decision |
|---|---|---|---|---|
| Autonomic age score establishes longevity | No | No; same-dataset prior art | No. Age is not a prospective health outcome; 2023 and 2025 source-cohort age clocks already exist | **Do not develop yet** |
| Conventional HRV alone is adequate | Potential baseline | Often small incremental value; confounding | **Use as reference** adjusted for mean HR, clinical factors and rhythm | Baseline comparator |
| Heart-rate fragmentation predicts future events | Not central | MESA positive and novel vs resting HRV | Verified MESA association; independent clinical replication is mandatory | **First software/clinical candidate** |
| Our current 12/20 BRS result confirms baroreflex dysfunction | Not claimed | Calls it pipeline fault | Neither valid nor automatically erroneous; no reference-ground-truth and quality gate changes yield | **Method-validation HOLD** |
| BRS can be clinically useful | Yes in post-MI | Some Rotterdam subset support | Population-dependent observational associations; spontaneous methods disagree with true gain | Cardiovascular-specific research, not a universal age marker |
| Stress/recovery dynamics may add novel value | Yes | TILDA evidence / MIDUS lead | Strong hypothesis, cohort access and precise time alignment outstanding | Parallel dataset/engineering track |
| One score for pregnancy, menopause, children, athletes and CVD | No | No | Missing clinical phenotypes forbid cross-population generalization | Separate cohorts |
| Increasing vagal tone extends lifespan | No proof | Negative major HF device trials | No trial proof of longevity benefit; advanced HF failures do not rule out all contexts | No intervention product claims |
| Full 1,121 PhysioNet scan should run now | Suggested | Suggested | **Not yet**; first establish BP/BRS reference validity and diagnostic failure reasons | Gated expansion |

## Ordered evidence priorities

1. [MUSIC cohort](../reports/MUSIC_METADATA_AUDIT.md): 992 heart-failure patients; 587 with baseline SDNN/RMSSD; clinical follow-up and death codes. Confirm source-specific event/censoring and eligible sinus-rhythm selection.
2. [HRF measurement module](../anslab/heart_rate_fragmentation.py): PIP/W1 with explicit 4-ms/5-ms quantization and beat-gap handling. **Synthetic testing is not a prognostic result.**
3. [Fantasia reference benchmark](../reports/FANTASIA_ECG_BENCHMARK.md): four selected ECGs; timing/QRS validation only. Next move into independent rhythm/ectopy annotations in a clinical cohort.
4. [BRS limitations](INDEPENDENT_BIOMARKER_REVIEW_2026-11-15.md#agent-4--baroreflex-measurement-validator): two spontaneous methods + correctly time-shifted negative control + manual BP/ECG alignment.
5. [Dynamic physiological challenge](INDEPENDENT_BIOMARKER_REVIEW_2026-11-15.md#agent-6--autonomic-recovery--physiologic-resilience-researcher): CDED/CVES for open ECG/BP challenge feasibility; TILDA for already-published mortality evidence; MIDUS resolution and linkage need verification.
6. Outcomes in independently accessible cohorts: MUSIC first; SHHS/NSRR and MIDUS if authorization and usable data permit.

## Rules for integrating another agent's submission

1. **Source identity:** record DOI/PMID/dataset URL, study design, publication date, number of participants/events, and exact measured outcome. Check the original source.
2. **Independent verification:** label each statement **verified / partially verified / disputed / unsupported**. A copied bibliography is not proof.
3. **Novelty screening:** check prior art, other age clocks and standard HRF/BRS literature before calling a marker new.
4. **Dataset feasibility:** distinguish publicly downloadable raw waveforms, metadata-only releases, approval-required datasets, and outcomes requiring roster/censoring linkage.
5. **Experimental usefulness:** accept only if it changes an implementable measurement, real-outcome test, QC criterion, or plausible falsification.
6. **Contradictions stay visible:** never silently replace negative/null observations or change preregistered thresholds after seeing outcomes.
7. **No patient-level data in research repo:** public aggregate counts only; observe provider access and usage agreements.

**Current scientific status:** 0 validated ageing/longevity biomarkers, 0 Project ANS survival models, 0 demonstrated life-extending interventions.

## 2026-11-15 follow-up: batch of four external reports

All four are reviewed in [the combined evidence adjudication](EXTERNAL_AGENTS_BRS_MUSIC_RECOVERY_REDTEAM_2026-11-15.md).

- BRS: PRCP and BaroKit are legitimate references; 12/20 provisional output is not automatically a malfunction; xBRS variance-ratio confounding is demonstrated.
- MUSIC: use deceleration capacity as an advanced comparison; **beta-blocker column already verified**, and **transplant must not be mislabeled a death**. Minimum event count and exact censoring remain open.
- Dynamic recovery: 2015 prospective meta-analysis confirms an association, but the **12-year TILDA full-response article was published in December 2025**, not merely preprinted.
- Red team: a plain HRV/BRS/HRF/recovery composite is not new. HRF patent application **US20200375480A1** exists; Google currently records that application as *abandoned*, not freedom-to-operate.

**Invention gate:** prior-art differentiation and repeatable longitudinal human outcomes are prerequisites before an original autonomic biomarker can be claimed.
