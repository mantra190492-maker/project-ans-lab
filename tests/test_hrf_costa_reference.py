"""Small local correctness guards; official author fixture agreement runs on CI."""
import unittest
from anslab.hrf_costa_reference import costa_fragmentation_from_peaks


def beat_peaks(intervals):
    times=[0.0]
    for rr in intervals:
        times.append(round(times[-1]+rr,6))
    return times


class CostaSourceGuards(unittest.TestCase):
    def test_missing_peak_annotations_are_not_acceptable(self):
        with self.assertRaisesRegex(ValueError, "one label"):
            costa_fragmentation_from_peaks([0,.8,1.6,2.4,3.2],[1]*4)

    def test_non_monotone_peak_times_rejected(self):
        with self.assertRaisesRegex(ValueError, "increasing"):
            costa_fragmentation_from_peaks([0,.8,1.6,1.6,3.2],[1]*5)

    def test_unknown_rhythm_status_is_never_treated_as_sinus(self):
        with self.assertRaisesRegex(ValueError, "source format"):
            costa_fragmentation_from_peaks([0,.8,1.6,2.4,3.2],[1,1,0,1,1])

    def test_constant_nn_is_not_falsely_reported_as_normal_health(self):
        with self.assertRaisesRegex(ValueError, "No reference-countable"):
            costa_fragmentation_from_peaks(beat_peaks([.8]*40),[1]*41)

    def test_repeated_real_reversals_are_detected(self):
        rr=[.8,.812]*25
        y=costa_fragmentation_from_peaks(beat_peaks(rr),[1]*51)
        self.assertGreater(y["n_hard_inflections"],20)
        self.assertGreater(y["pip_percent"],50)

    def test_zero_transitions_count_as_soft_inflections(self):
        rr=[.8,.8,.804,.804,.8]*18
        y=costa_fragmentation_from_peaks(beat_peaks(rr),[1]*91)
        self.assertGreater(y["n_soft_inflections"],0)

    def test_preserve_native_sampling_frequency_in_metadata(self):
        peaks=beat_peaks([.8,.812]*25)
        y=costa_fragmentation_from_peaks(peaks,[1]*51,sampling_hz=125)
        self.assertEqual(y["native_sampling_hz"],125.)

    def test_single_non_sinus_beat_breaks_adjoining_nn(self):
        rr=[.8,.812]*30
        peaks=beat_peaks(rr)
        labels=[1]*len(peaks)
        labels[25]=2
        y=costa_fragmentation_from_peaks(peaks,labels)
        self.assertLess(y["n_valid_pairwise_sinus_nn"],len(rr))
        self.assertLess(y["n_valid_three_interval_windows"],len(rr)-2)

    def test_implausible_rr_is_not_artificially_joined(self):
        rr=[.8,.812]*15+[2.0]+[.8,.812]*15
        peaks=beat_peaks(rr)
        y=costa_fragmentation_from_peaks(peaks,[1]*len(peaks))
        self.assertLess(y["n_valid_three_interval_windows"],len(rr)-2)


if __name__=="__main__":
    unittest.main()
