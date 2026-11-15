#!/usr/bin/env bash
# Current exploration step (edited per loop). Structure/QC only unless a frozen plan says otherwise.
set -euo pipefail
python -m scripts.vr_validate  # POOL-VR-001 stage A
