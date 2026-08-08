import math
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED"       # Normal healthy operation (AI/Kalman active)
    OPEN = "OPEN"           # Tripped / Fallback active (Fallback BDP forced for cooldown)
    HALF_OPEN = "HALF_OPEN" # Probing recovery state

class EfficiencyMonitor:
    """
    Evaluates real-time transport efficiency and manages a 3-State Circuit Breaker:
    - Adaptive RTT Noise Threshold: max(rtt_noise_threshold_ms, rtt_noise_ratio * current_rtt_ms)
      Prevents over-sensitivity in low-RTT / high-speed regimes (e.g. 10ms links).
    - CLOSED: Normal operation. Increments failure counter on negative efficiency score.
    - OPEN: Tripped. Forces fallback BDP for cooldown_ticks (e.g. 5 ticks).
    - HALF_OPEN: Probes 1 step after cooldown to test if network efficiency recovered.
    """
    def __init__(
        self,
        k_threshold: int = 5,
        cooldown_ticks: int = 5,
        epsilon_ms: float = 1.0,
        beta: float = 1.5,
        rtt_noise_threshold_ms: float = 3.0,
        rtt_noise_ratio: float = 0.15,
        warmup_ticks: int = 10
    ):
        self.k_threshold = k_threshold
        self.cooldown_ticks = cooldown_ticks
        self.epsilon_ms = epsilon_ms
        self.beta = beta
        self.rtt_noise_threshold_ms = rtt_noise_threshold_ms
        self.rtt_noise_ratio = rtt_noise_ratio
        self.warmup_ticks = warmup_ticks
        
        self.consecutive_failures = 0
        self.current_tick = 0
        self.state = CircuitState.CLOSED
        self.cooldown_counter = 0

    def evaluate_step(self, base_throughput: float, delta_throughput: float, current_rtt_ms: float, delta_rtt_ms: float) -> float:
        self.current_tick += 1

        # 1. Warm-up Period
        if self.current_tick <= self.warmup_ticks:
            self.state = CircuitState.CLOSED
            self.consecutive_failures = 0
            return 1.0

        # 2. State Machine: Cooldown tracking when OPEN
        if self.state == CircuitState.OPEN:
            self.cooldown_counter += 1
            if self.cooldown_counter >= self.cooldown_ticks:
                self.state = CircuitState.HALF_OPEN
                self.cooldown_counter = 0
            return -1.0

        # 3. Efficiency Score Calculation with Adaptive RTT Noise Threshold
        throughput_norm = delta_throughput / max(base_throughput, 1.0)
        
        # Adaptive Noise Threshold scales with RTT regime (e.g. 15% of RTT or min 3.0ms)
        effective_noise_threshold = max(self.rtt_noise_threshold_ms, self.rtt_noise_ratio * current_rtt_ms)
        penalized_rtt_delta = max(0.0, delta_rtt_ms - effective_noise_threshold)
        
        rtt_penalty = self.beta * (penalized_rtt_delta / max(current_rtt_ms, self.epsilon_ms))
        score = throughput_norm - rtt_penalty

        # 4. State Transitions
        if self.state == CircuitState.HALF_OPEN:
            if score >= 0.0:
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
            else:
                self.state = CircuitState.OPEN
                self.cooldown_counter = 0
        else: # CLOSED state
            if score < 0.0:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.k_threshold:
                    self.state = CircuitState.OPEN
                    self.cooldown_counter = 0
            else:
                self.consecutive_failures = 0

        return score

    def is_tripped(self) -> bool:
        return self.state == CircuitState.OPEN

    @staticmethod
    def is_nan_or_inf(val: float) -> bool:
        return math.isnan(val) or math.isinf(val)
