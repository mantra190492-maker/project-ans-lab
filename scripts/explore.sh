#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -uo pipefail
# DIAB-PIP-001 (docs/DIAB_PIP_001_PLAN.md, frozen in commit d033849 before any ECG was read).
for attempt in 1 2; do
  python -m scripts.diab_pip_001 && exit 0
  echo "attempt $attempt failed; retrying in 60 s"; sleep 60
done
exit 1
