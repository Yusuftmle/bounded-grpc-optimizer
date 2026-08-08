import unittest
from tools.bounded_optimizer.guardrails import SafetyGuardrail

class TestSafetyGuardrail(unittest.TestCase):
    def setUp(self):
        self.guardrail = SafetyGuardrail(
            min_window_bytes=65536,
            max_window_bytes=8388608,
            max_step_ratio=0.20
        )

    def test_min_quota_clamp(self):
        current_window = 100000
        proposed_window = 10000
        clamped, was_clamped = self.guardrail.apply(current_window=current_window, proposed_window=proposed_window)
        self.assertGreaterEqual(clamped, 65536)
        self.assertTrue(was_clamped)

    def test_max_quota_clamp(self):
        current_window = 7500000
        proposed_window = 20000000
        clamped, was_clamped = self.guardrail.apply(current_window=current_window, proposed_window=proposed_window)
        self.assertEqual(clamped, 8388608)
        self.assertTrue(was_clamped)

    def test_relative_step_increase_limit(self):
        current_window = 1000000
        proposed_window = 1500000
        clamped, was_clamped = self.guardrail.apply(current_window=current_window, proposed_window=proposed_window)
        self.assertEqual(clamped, 1200000)
        self.assertTrue(was_clamped)

    def test_relative_step_decrease_limit(self):
        current_window = 1000000
        proposed_window = 300000
        clamped, was_clamped = self.guardrail.apply(current_window=current_window, proposed_window=proposed_window)
        self.assertEqual(clamped, 800000)
        self.assertTrue(was_clamped)

    def test_valid_in_bounds_suggestion(self):
        current_window = 1000000
        proposed_window = 1100000
        clamped, was_clamped = self.guardrail.apply(current_window=current_window, proposed_window=proposed_window)
        self.assertEqual(clamped, 1100000)
        self.assertFalse(was_clamped)

if __name__ == '__main__':
    unittest.main()
