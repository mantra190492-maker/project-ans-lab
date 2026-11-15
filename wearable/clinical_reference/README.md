# Clinical-reference sidecar for wearable accuracy research

**Scope:** This folder maps the founder's eight specialist modalities to **external reference outcomes** for future same-person studies. None is a direct smartwatch sensor. No specialist data or clinically labelled paired wrist recordings are currently in this folder.

## Architecture: two non-interchangeable branches

```text
Wearable observation path                   Independent specialist evidence
L0 source + consent/provenance              Clinical expert assessment
L1 wrist acquisition                        MSNA / cardiac imaging
L2 device artifacts                         Sweat gland/small-fibre biopsy
L3 quality control                          Corneal nerve imaging
L4 wearable features                        p-alpha-syn pathology (disease-specific)
L5 wearable-only fusion                     GI / urinary / secretory tests
              \                             /
               L6: evaluation against a pre-defined
                   independent diagnostic/physiological
                   endpoint on the SAME participant
```

**No leakage:** The clinical-reference branch is *not* silently included in a wrist-only model. If specialist data are fed into a separate multimodal clinical model, report that as a different system, requiring its own access, costs and validation.

## Specialist categories and roles

| ID | Measurement | Role, NOT watch capability |
|---|---|---|
| MSNA | Microneurography of muscle sympathetic nerve activity | Direct sympathetic neurophysiology comparator; invasive, not routine general ANS truth |
| CARDIAC_INNERVATION | MIBG scintigraphy or sympathetic PET | Cardiac sympathetic organ-specific assessment; disease/medication confounded |
| SKIN_SMALL_FIBRES | IENFD and sweat-gland innervation in skin biopsy | Structural nerve evidence; distinguish somatic IENFD from autonomic sweat-gland fibres |
| CORNEAL_NERVES | Corneal confocal nerve fibre morphology | Supportive small-fibre structure; **not autonomic-specific** |
| PHOSPHO_ALPHA_SYNUCLEIN | Phosphorylated alpha-synuclein histology | Selected **synucleinopathy** pathology; **not general ANS deterioration** |
| GASTROINTESTINAL | Gastric emptying, transit and manometry | Organ-specific functional outcomes with many non-ANS confounders |
| URINARY | Urodynamics and bladder function | Organ-specific functional outcomes, not proof of neural damage |
| SECRETORY | Schirmer tears and salivary flow | Supporting exocrine outcomes with medication/gland confounders |

The machine-readable details, limitations and sources live in [registry.json](registry.json).

## Accuracy plan (future real paired data)

1. **Target first:** Specify a condition and clinically meaningful endpoint before collecting labels, e.g. independently physician-adjudicated neurogenic orthostatic hypotension or a defined neuropathy progression criterion. There is no universally valid “ANS damaged” binary label.
2. **Pair properly:** Match same person's *wearable data* to clinician measurements performed at a prespecified interval; document timing, disease, medications, posture and device.
3. **Do not merge distinct disease labels:** Skin alpha-synuclein positivity is not interchangeable with MSNA burst rate, corneal fibre length or gastric emptying delay. Use phenotype-specific models and report each endpoint separately.
4. **Predeclare comparator:** Relevant autonomic reflex tests, diagnosis and context; compare simple wearable model vs multimodal wearable, not against a deliberately weak comparator.
5. **Measure:** Sensitivity, specificity, uncertainty, calibration, incremental discrimination, missing-data sensitivity and confidence intervals using participant-separated tests. Report external-device/site validation before claims.
6. **Falsify:** If wrist features don't add predictive information above an established simple baseline, retain the null result and do not advertise a detector.

**Important:** A model tested against CASS is partly circular if its input includes the same reflex measurements contributing to CASS. Use blind clinician adjudication or a truly separate future endpoint where feasible. Do not train with the labels or post-baseline measurements among wearable-only inputs.

## Prior art and clinical standards

- 2026 [American Autonomic Society consensus](https://pubmed.ncbi.nlm.nih.gov/42766240/) on clinical autonomic testing
- 2020 [Autonomic electrodiagnostic consensus](https://pubmed.ncbi.nlm.nih.gov/33419664/) on cardiovagal, adrenergic and sudomotor standards
- 2021 [Auxiliary autonomic tests](https://pubmed.ncbi.nlm.nih.gov/34009848/) on microneurography, eye, GI, urogenital and secretory testing
- 2024 [Skin phosphorylated alpha-synuclein multicentre study](https://pubmed.ncbi.nlm.nih.gov/38506839/)
- 2023 [Corneal confocal microscopy compared with IENFD](https://pubmed.ncbi.nlm.nih.gov/37651181/)

**Current state:** Design and source inventory only. No specialist reference records, paired participants, model sensitivity/specificity or medically valid diagnostic accuracy have been collected or computed.
