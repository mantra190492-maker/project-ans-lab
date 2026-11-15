#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -uo pipefail
# FUSION-001 (wearable/experiments/FUSION_001_PLAN.md). Uses the PhysioNet open S3 mirror first (physionet.org timed out from runners).
for attempt in 1 2 3; do
  python -m wearable.experiments.fusion_001 && exit 0
  echo "attempt $attempt failed; retrying in 60 s"; sleep 60
done
exit 1
