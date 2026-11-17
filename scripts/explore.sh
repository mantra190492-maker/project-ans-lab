#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -uo pipefail
# DIAB-PIP-001 preparation part 2: covariate availability and ID linkage. Tables and header text only; no signal is read.
for attempt in 1 2; do
  python -m scripts.diab_prepare2 && exit 0
  echo "attempt $attempt failed; retrying in 60 s"; sleep 60
done
exit 1
