# WATCH-SIM-001 — First self-contained acquisition smoke test

**Date:** 2026-11-15. **Status:** SYNTHETIC ENGINEERING CHECK, **not** real watch validation.

- Device profile: Galaxy Watch8-class published SDK rates, not Samsung firmware.
- Inputs: 180 seconds of artificial wrist signals sampled at WESAD-like input frequencies: BVP 64 Hz, accelerometer 32 Hz, EDA 4 Hz, temperature 4 Hz.
- Output from simulator: **4,500 PPG samples at 25 Hz**, **4,500 3-axis accelerometer samples at 25 Hz**, **180 EDA samples at 1 Hz**, **180 temperature values** at an *assumed* 1 Hz.
- Seeded scenario: artificial motion-correlated optical interference and 1.5% random PPG drop probability.
- Observed PPG sample coverage: **98.56%** (4,435 of 4,500 valid samples); this passes only a 95% **availability** gate. This does **not** mean 98.56% pulse-detection accuracy.
- Local unit tests: **10 passed** including anti-aliasing, source alignment, sensor-rate restrictions, required EDA, deterministic missingness, and suppression of unsupported clinical claims.

**Explicitly not established:** Real Samsung noise profile, real ECG/PPG beat agreement, processed HR/IBI, blood pressure response, sweat nerve function, ANS dysfunction detection, disease accuracy or 3-domain fusion.

**Real subjects analyzed in WATCH-SIM-001: 0. Watch devices: 0. Clinical labels: 0.**

**Next gate:** Obtain same-person WESAD raw wrist streams and independently recorded chest ECG as a timing comparator (with appropriate use permissions); compare optical beat extraction against ECG using subject-separated evaluation. WESAD stress labels are not ANS disease labels.

Code: [simulator](../simulator.py) · [demo](../experiments/watch_sim_001.py) · [tests](../tests/test_simulator.py).

Source specifications: https://developer.samsung.com/health/sensor/guide/data-specifications.html
