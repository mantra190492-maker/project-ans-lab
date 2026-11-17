#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -uo pipefail
# DIAB-PIP-001 preparation: tables, protocol docs, ID overlap, CO2-only rest windows. No ECG is read.
for attempt in 1 2; do
  python -m scripts.diab_prepare && exit 0
  echo "attempt $attempt failed; retrying in 60 s"; sleep 60
done
exit 1
