import time
import random
from dataclasses import dataclass

@dataclass
class TelemetryFrame:
    timestamp: float
    rtt_ms: float
    bytes_received: int
    throughput_bytes_per_sec: float
    active_streams: int

class SyntheticTelemetryStream:
    """
    Simulates live gRPC Channelz telemetries over a dynamic link.
    Supports injecting network jitter, latency spikes, and bursty payload patterns.
    """
    def __init__(self, base_rtt_ms: float = 20.0, base_bandwidth_mbps: float = 100.0):
        self.base_rtt_ms = base_rtt_ms
        self.base_bandwidth_mbps = base_bandwidth_mbps
        self.current_time = time.time()
        self.total_bytes = 0

    def generate_tick(self, duration_sec: float = 0.1, jitter_ms: float = 2.0, burst_factor: float = 1.0) -> TelemetryFrame:
        self.current_time += duration_sec
        
        # Calculate simulated RTT with Gaussian noise & burst factor
        actual_rtt = max(2.0, random.gauss(self.base_rtt_ms * burst_factor, jitter_ms))
        
        # Calculate byte arrival rate
        bandwidth_bytes_sec = (self.base_bandwidth_mbps * 1e6 / 8.0) * (1.0 / burst_factor)
        bytes_in_tick = int(bandwidth_bytes_sec * duration_sec * random.uniform(0.9, 1.1))
        self.total_bytes += bytes_in_tick

        return TelemetryFrame(
            timestamp=self.current_time,
            rtt_ms=actual_rtt,
            bytes_received=self.total_bytes,
            throughput_bytes_per_sec=bytes_in_tick / duration_sec,
            active_streams=random.randint(5, 20)
        )
