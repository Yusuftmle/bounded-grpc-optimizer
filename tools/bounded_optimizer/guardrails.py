class SafetyGuardrail:
    """
    Enforces deterministic safety constraints on flow control window recommendations:
    1. Absolute Quota Limits: [min_window_bytes, max_window_bytes] (e.g. 64 KB to 8 MB)
    2. Relative Rate-of-Change Limiter: |Δw| <= max_step_ratio * current_window (e.g. max +/- 20%)

    Defense in Depth: Must be applied to ALL outputs (Kalman predictions, Fallback BDP, Probing signals).
    """
    def __init__(self, min_window_bytes: int = 65536, max_window_bytes: int = 8388608, max_step_ratio: float = 0.20):
        self.min_window_bytes = min_window_bytes
        self.max_window_bytes = max_window_bytes
        self.max_step_ratio = max_step_ratio

    def apply(self, current_window: float, proposed_window: float) -> tuple[float, bool]:
        """
        Applies quota bounds and step limiter.
        Returns: (clamped_window, was_clamped_flag)
        """
        # 1. Apply Relative Rate-of-Change Clamp (MaxStep)
        min_allowed_step = current_window * (1.0 - self.max_step_ratio)
        max_allowed_step = current_window * (1.0 + self.max_step_ratio)
        step_clamped = max(min_allowed_step, min(max_allowed_step, proposed_window))

        # 2. Apply Absolute Quota Bounds [MinQuota, MaxQuota]
        final_clamped = max(self.min_window_bytes, min(self.max_window_bytes, step_clamped))
        
        was_clamped = (final_clamped != proposed_window)
        return final_clamped, was_clamped
