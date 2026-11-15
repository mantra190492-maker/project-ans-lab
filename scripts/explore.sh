#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -uo pipefail
# POOL-VR-001 stage A. Retry on PhysioNet connection timeouts.
for attempt in 1 2 3; do
  python -m scripts.vr_validate && exit 0
  echo "attempt $attempt failed; retrying in 90 s"; sleep 90
done
exit 1
