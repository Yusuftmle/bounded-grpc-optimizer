import unittest
from tools.bounded_optimizer.kalman_estimator import KalmanWindowEstimator

class TestKalmanWindowEstimator(unittest.TestCase):
    def setUp(self):
        self.estimator = KalmanWindowEstimator(
            initial_bdp_bytes=1048576.0,
            process_noise=100.0,
            measurement_noise=1000.0
        )

    def test_kalman_initialization(self):
        self.assertAlmostEqual(self.estimator.state, 1048576.0)

    def test_covariance_reduction_on_update(self):
        initial_p = self.estimator.covariance
        for _ in range(10):
            self.estimator.update(measurement=1050000.0)
        self.assertLess(self.estimator.covariance, initial_p)

    def test_noise_filtering_and_convergence(self):
        true_bdp = 2097152.0
        noisy_measurements = [
            2097152.0 + 50000.0,
            2097152.0 - 45000.0,
            2097152.0 + 30000.0,
            2097152.0 - 60000.0,
            2097152.0 + 10000.0,
            2097152.0 - 20000.0
        ]

        for m in noisy_measurements:
            self.estimator.update(m)

        error = abs(self.estimator.state - true_bdp) / true_bdp
        self.assertLess(error, 0.05)

if __name__ == '__main__':
    unittest.main()
