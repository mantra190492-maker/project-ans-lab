# POOL-VR-001 — automated Valsalva ratio, then one pooled test of resting fragmentation

Written 2026-11-15 after GE71-ANS-001 (null, n = 27). Two stages; stage B is frozen separately only if stage A passes.

## Stage A — validate an automated Valsalva ratio (no predictor involved)

**Why:** only GE-71 has lab-scored Valsalva ratios. To test more people (CDED visit 2 and GE-75), the ratio has to be computed from the signals, and that has to be shown to agree with the lab first.

**Method, fixed before the first run:**
- Beats: repo detector in 2-minute chunks at native rate, peaks refined to the dominant-polarity maximum (±40 ms). RR series smoothed with a 3-beat median to remove single ectopic beats.
- **Gap-based locator (the one usable in all datasets):** mask-off gaps = CO2 below 25% of typical end-tidal for 8–150 s, starting after the first minute and ending ≥35 s before the record ends. For each gap: shortest RR between 10 s before the gap and 10 s after it; longest RR in the 30 s after that shortest beat. Ratio = longest ÷ shortest. Participant value = largest ratio over gaps.
- **Marker-based locator (GE-71 Day 1 only, reference):** maneuvers from the marker ordinals in the dataset's Day-1 marker table; shortest RR from start to 5 s after end, longest RR up to 30 s after end.
- Compared with the lab's `VM RATIO` for the same person. The lab values may come from either day.

**Pass rule:** the gap-based ratio is accepted if Spearman ρ ≥ 0.60 against the lab value in ≥ 20 people (on either day's recording). If it fails, POOL-VR-001 stops and the ledger moves to the next item.

Stage A reads outcomes only (automated vs lab Valsalva ratio). No fragmentation or HRV value is computed in this stage.

## Stage B — pooled test (to be frozen after stage A, before any pooled outcome is computed)

Planned shape: resting PIP vs automated Valsalva ratio in CDED visit 2 and GE-75 (people not in GE71-ANS-001), adjusted for age, sex, diabetes, dataset, mean heart rate and log RMSSD; one test; same robustness rules as GE71-ANS-001.
