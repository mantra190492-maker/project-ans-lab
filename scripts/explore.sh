#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -uo pipefail
# TILT-001 (docs/TILT_001_PLAN.md). Uses the PhysioNet open S3 mirror first.
for attempt in 1 2; do
  python -m scripts.tilt_001 && exit 0
  echo "attempt $attempt failed; retrying in 60 s"; sleep 60
done
exit 1
