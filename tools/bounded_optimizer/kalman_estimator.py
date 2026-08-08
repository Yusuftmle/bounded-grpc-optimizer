class KalmanWindowEstimator:
    """
    1D Linear Kalman Filter for optimal Bandwidth-Delay Product (BDP) estimation.
    Estimates true underlying un-buffered BDP state from noisy, jitter-prone telemetries.
    """
    def __init__(self, initial_bdp_bytes: float = 1048576.0, process_noise: float = 100.0, measurement_noise: float = 1000.0):
        self.state = initial_bdp_bytes       # x_t (estimated BDP in bytes)
        self.covariance = 100000.0           # P_t (error covariance)
        self.process_noise = process_noise   # Q (process noise)
        self.measurement_noise = measurement_noise # R (measurement noise)

    def predict(self):
        # State extrapolation (assuming constant state model between rapid ticks)
        self.covariance = self.covariance + self.process_noise

    def update(self, measurement: float) -> float:
        # Predict step
        self.predict()

        # Kalman Gain computation: K_t = P_t / (P_t + R)
        kalman_gain = self.covariance / (self.covariance + self.measurement_noise)

        # State update: x_t = x_t + K_t * (z_t - x_t)
        self.state = self.state + kalman_gain * (measurement - self.state)

        # Covariance update: P_t = (1 - K_t) * P_t
        self.covariance = (1.0 - kalman_gain) * self.covariance

        return self.state
