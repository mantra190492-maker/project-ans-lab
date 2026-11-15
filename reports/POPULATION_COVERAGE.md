# ANS-001 — Population coverage and missingness audit

Source: PhysioNet Autonomic Aging v1.0.0
Participants audited: 20

## Variables actually observed in the current cohort

| Variable | Known participants | Not known |
|---|---:|---:|
| age_group | 20 | 0 |
| sex_code | 20 | 0 |
| bmi | 20 | 0 |
| device_code | 20 | 0 |

## Clinical and developmental population coverage

| Target | Status |
|---|---|
| Pregnant / nonpregnant and postpartum | UNKNOWN — not recorded |
| Premenopause / perimenopause / postmenopause | UNKNOWN — not recorded |
| Coronary stents, PCI and cardiovascular disease history | UNKNOWN — not recorded; screened healthy-volunteer sample |
| Athletes / physical training status | UNKNOWN — not recorded |
| Children younger than 18 | ABSENT — adult dataset |

**UNKNOWN is not the same as NO.** Healthy-volunteer eligibility does not independently identify any participant's reproductive or training status.

## Selected age-group counts

- 18-34: 5
- 35-49: 5
- 50-64: 5
- 65+: 5

## Allowed and prohibited inference

- Allowed: exploratory adult HRV/BRS signal-processing feasibility and transparent quality metrics.
- Not allowed: pregnancy/menopause/PCI/athlete subgroup comparisons, pediatric results, health risk or longevity predictions.
- Any group-specific comparison requires an externally verified phenotype and a suitable study design.

Protocol: [Population Stratification](../docs/POPULATION_STRATIFICATION.md)
Source: https://physionet.org/content/autonomic-aging-cardiovascular/1.0.0/
