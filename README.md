# Project ANS Lab

Private research automation prototype for ANS-003: adult-onset neuromuscular disease differentiation.

## Run
`python -m scripts.daily`

Requires Python 3.11+ and `requests` (`pip install -r requirements.txt`). Scheduled workflow runs daily at 09:00 UTC. Results are metadata-only research leads, not clinical findings or medical advice.

Research sources: NCBI PubMed E-utilities. No paywall circumvention, patient data, or paid model required.
