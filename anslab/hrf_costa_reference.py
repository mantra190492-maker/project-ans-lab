"""Independent Python implementation of Costa 2017/2024 HRF source semantics.

Reference: Costa, PhysioNet (2024), https://doi.org/10.13026/0mzj-gn98
    https://physionet.org/content/heart-rate-fragmentation-code/1.0.0/

This is an independently written numerical implementation, NOT copied AWK code.
The official source uses R-PEAK TIMES and per-BEAT rhythm annotations.
Input NN intervals without timestamps cannot reproduce author QC/gridding exactly.

Do not use for clinical diagnosis, and do not claim author equivalence until all
official AWK fixtures agree, including the 3rd fixture's corrected 30/46 PIP.
"""
from __future__ import annotations

import math
from typing import Sequence


def costa_fragmentation_from_peaks(
    peak_times_seconds: Sequence[float],
    beat_labels: Sequence[int],
    *,
    sampling_hz: float = 250.0,
    nn_min_seconds: float = 0.300,
    nn_max_seconds: float = 1.800,
):
    """Return PIP, PNNSS and PNNLS with author-style per-beat eligibility.

    The reference holds a segment open until the next inflection, and truncates
    unresolved first/last segments and interruptions by non-sinus or invalid NN.
    Therefore its PIP denominator is NOT all triplets in a fixed time window.

    Beat labels: 1=sinus, 2/3=ectopic, as in author's official test files.
    Sampling frequency is for native R-peak quantization. DO NOT interpolate
    a coarse ECG to a high sampling frequency and claim recovered resolution.

    Scope: exact SHHS agreement/clinical validity NOT yet demonstrated.
    """
    times = [float(t) for t in peak_times_seconds]
    labels = [int(v) for v in beat_labels]
    if len(times) != len(labels) or len(times) < 5:
        raise ValueError("Need at least five ordered R peaks with one label per peak")
    if not math.isfinite(sampling_hz) or not 10.0 <= sampling_hz <= 5000.0:
        raise ValueError("Invalid native ECG sampling frequency")
    if not (0 < nn_min_seconds < nn_max_seconds):
        raise ValueError("Invalid acceptable NN interval bounds")
    if not all(math.isfinite(t) for t in times) or any(
        times[i] <= times[i - 1] for i in range(1, len(times))
    ):
        raise ValueError("R-peak timestamps must be finite and strictly increasing")
    if any(x not in (1, 2, 3) for x in labels):
        raise ValueError("Beat labels must be source format 1/2/3 (sinus/PVC/PAC)")

    # Author software version 1.0 uses a THREE-decimal formatting operation
    # while aligning R-peak timestamps to the nominal sample grid. We make that
    # explicit for the same author-fixture behavior (not higher timing accuracy).
    # WARNING: source rounding details are a methodological sensitivity.
    aligned = []
    for t in times:
        q = int(float(f"{t * sampling_hz:.3f}"))
        lower = q / sampling_hz
        if 0 < t - lower <= 0.5:
            aligned.append(lower)
        elif t - lower > 0.5:
            aligned.append((q + 1) / sampling_hz)
        else:
            aligned.append(t)
    times = aligned

    ip = 0
    valid_nn_count = 0
    total_author = 0
    delta_total = 0
    short_steps = 0
    long_steps = 0
    elapsed_steps = 0
    break_pending = False
    valid_three_interval_windows = 0
    hard_ips = 0
    soft_ips = 0
    step=1.0/1000.0

    for i in range(len(times)):
        if i >= 3:
            # Three consecutive NN intervals require four sinus-labelled beats.
            sinus = all(label == 1 for label in labels[i-3:i+1])
            intervals = (
                times[i] - times[i-1],
                times[i-1] - times[i-2],
                times[i-2] - times[i-3],
            )
            plausible = all(nn_min_seconds < n < nn_max_seconds for n in intervals)
            if not (sinus and plausible):
                break_pending = True
            else:
                valid_three_interval_windows += 1
                # A zero is defined by rounded NN DIFFERENCE at 0.001 s,
                # not by a +/- sample-resolution symbol deadband.
                d_current = round((intervals[0] - intervals[1]) / step) * step
                d_previous = round((intervals[1] - intervals[2]) / step) * step
                hard = d_current * d_previous < 0
                soft = (d_current == 0 or d_previous == 0) and d_current != d_previous
                if hard or soft:
                    ip += 1
                    hard_ips += int(hard)
                    soft_ips += int(soft)
                    if break_pending:
                        # Discard unresolved segment across rhythm/artifact gap.
                        total_author += 1
                        break_pending = False
                    elif ip == 1:
                        total_author = 1
                    else:
                        total_author += elapsed_steps
                        delta_total += elapsed_steps
                        if elapsed_steps > 2:
                            long_steps += elapsed_steps
                        elif hard or d_previous != 0:
                            short_steps += elapsed_steps
                    elapsed_steps = 0

        if i >= 1:
            elapsed_steps += 1

    valid_nn_count=sum(
        1 for i in range(1,len(times))
        if labels[i-1] == 1 and labels[i] == 1
        and nn_min_seconds < times[i]-times[i-1] < nn_max_seconds
    )
    if total_author == 0:
        raise ValueError("No reference-countable inflection points; PIP undefined")
    n_acc_dec=short_steps+long_steps
    return {
        "pip_percent":100*ip/total_author,
        "pnnss_percent":100*short_steps/n_acc_dec if n_acc_dec else float("nan"),
        "pnnls_percent":100*long_steps/delta_total if delta_total else float("nan"),
        "n_inflection_points":ip,
        "n_hard_inflections":hard_ips,
        "n_soft_inflections":soft_ips,
        "n_author_eligible_nn":total_author,
        "n_counted_delta_nn":delta_total,
        "n_short_delta_nn":short_steps,
        "n_long_delta_nn":long_steps,
        "n_valid_three_interval_windows":valid_three_interval_windows,
        "n_valid_pairwise_sinus_nn":valid_nn_count,
        "native_sampling_hz":float(sampling_hz),
        "software_reference":"Costa 2024 PhysioNet HRF.awk v1.0.0; independent implementation undergoing differential tests",
        "clinical_validation":"none",
    }
