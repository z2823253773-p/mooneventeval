import unittest
from validation.rational_oracle import eligible


def event(onset, offset, label='a'):
    return dict(id='e', label=label, onset_s=onset, offset_s=offset)


class RationalOracleTests(unittest.TestCase):
    def test_onset_equality_and_microsecond_outside(self):
        r = event('10', '12')
        self.assertTrue(eligible(r, event('10.2', '12.2'), {})['eligible'])
        self.assertFalse(eligible(r, event('10.200001', '12.2'), {})['eligible'])
        self.assertEqual(eligible(r, event('9.8', '12'), {})['onset_delta_s'], '-0.2')

    def test_offset_reference_duration_and_equality(self):
        r = event('10', '12')
        self.assertTrue(eligible(r, event('10', '13'), {})['eligible'])
        self.assertFalse(eligible(r, event('10', '13.000001'), {})['eligible'])
        self.assertFalse(eligible(r, event('10', '10.999999'), {})['eligible'])

    def test_fractional_microsecond_and_collar_dominance(self):
        result = eligible(event('10', '10.000003'), event('10', '10.000004'),
                          dict(collar_s='0', offset_ratio='0.5'))
        self.assertTrue(result['eligible'])
        self.assertEqual(result['offset_limit_s'], '0.0000015')
        self.assertTrue(eligible(event('0', '0.1'), event('0.2', '0.3'), {})['eligible'])

    def test_labels_and_zero_ratio_do_not_disable_conditions(self):
        self.assertFalse(eligible(event('1','2'), event('1','2','b'), {})['eligible'])
        self.assertFalse(eligible(event('1','2'), event('1','2.200001'),
                                 dict(offset_ratio='0'))['eligible'])
