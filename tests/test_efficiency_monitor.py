import unittest
from tools.bounded_optimizer.efficiency_monitor import EfficiencyMonitor, CircuitState

class TestEfficiencyMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = EfficiencyMonitor(
            k_threshold=5,
            cooldown_ticks=3,
            epsilon_ms=1.0,
            beta=1.5,
            rtt_noise_threshold_ms=3.0,
            warmup_ticks=3
        )

    def test_warmup_period_suppresses_failures(self):
        for _ in range(3):
            score = self.monitor.evaluate_step(1e6, -5e5, 20.0, 50.0)
            self.assertEqual(self.monitor.state, CircuitState.CLOSED)
            self.assertEqual(score, 1.0)

    def test_state_transition_closed_to_open_to_half_open_to_closed(self):
        for _ in range(3):
            self.monitor.evaluate_step(1e6, 0, 20.0, 0)
        self.assertEqual(self.monitor.state, CircuitState.CLOSED)

        for i in range(5):
            self.monitor.evaluate_step(1e6, -5e4, 20.0, 15.0)

        self.assertEqual(self.monitor.state, CircuitState.OPEN)
        self.assertTrue(self.monitor.is_tripped())

        self.monitor.evaluate_step(1e6, 0, 20.0, 0)
        self.monitor.evaluate_step(1e6, 0, 20.0, 0)
        self.monitor.evaluate_step(1e6, 0, 20.0, 0)
        self.assertEqual(self.monitor.state, CircuitState.HALF_OPEN)

        self.monitor.evaluate_step(1e6, 1e5, 20.0, -1.0)
        self.assertEqual(self.monitor.state, CircuitState.CLOSED)
        self.assertEqual(self.monitor.consecutive_failures, 0)

if __name__ == '__main__':
    unittest.main()
