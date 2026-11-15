# ANS-001 — MUSIC cardiovascular cohort metadata feasibility audit

Generated UTC: 2026-11-15T13:27:01.173839+00:00
Source: https://physionet.org/files/music-sudden-cardiac-death/1.0.1/subject-info.csv
Dataset DOI: 10.13026/z3m7-rf58

**No individual patient records were stored or committed. This is not a survival analysis.**

- Participants: **992**
- Distinct identifiers: **992**

## Observable fields

| Field | Nonmissing | Missing |
|---|---:|---:|
| Age | 992 | 0 |
| Gender (male=1) | 992 | 0 |
| Body Mass Index (Kg/m2) | 992 | 0 |
| Prior Myocardial Infarction (yes=1) | 992 | 0 |
| Prior Revascularization | 992 | 0 |
| Follow-up period from enrollment (days) | 992 | 0 |
| Cause of death | 992 | 0 |
| Holter available | 992 | 0 |
| Holter rhythm | 933 | 59 |
| Betablockers (yes=1) | 992 | 0 |
| SDNN (ms) | 587 | 405 |
| RMSSD (ms) | 587 | 405 |

## Coded baseline categories (aggregate counts only)

- Prior revascularization (0 none, 1 percutaneous, 2 surgical, 3 both): 0: 736, 1: 149, 2: 80, 3: 27
- Cause-of-death codes (0 survivor, 1 noncardiac, 3 sudden cardiac, 6-7 pump failure): 0: 726, 1: 61, 3: 94, 6: 100, 7: 11
- Holter availability: 0: 56, 1: 936
- Holter rhythm: 0: 651, 1: 171, 2: <5, 3: 105, 4: <5

## Scientific decision

1. Percutaneous revascularization is **not a verified coronary stent**. Do not relabel the field.
2. Baseline HRV metrics and event codes may support a **cardiovascular-disease-specific** benchmark, but this cohort is not a healthy-ageing reference.
3. Missingness, rhythm exclusions, event codes, follow-up/censoring definitions and data leakage must be prespecified before modeling.
4. ECG/BP BRS cannot be calculated here without a matching beat-to-beat BP signal.
5. The full MUSIC waveform archive is around **90 GB uncompressed**; this audit downloads only a small CSV.
6. An outcome risk score that is already published is **prior art**, not Project ANS novelty.

Sources:
- [PhysioNet MUSIC v1.0.1](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/)
- [Official outcome/revascularization coding](https://physionet.org/content/music-sudden-cardiac-death/1.0.1/subject-info_codes.csv)
- [Agent 02 scientific audit](../docs/AGENT_02_SKEPTICAL_ASSESSMENT_AUDIT.md)
