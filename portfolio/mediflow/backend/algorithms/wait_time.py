# ================================================================
#  algorithms/wait_time.py
#  Little's Law + Rolling Average — O(1) per update
#  W = L / λ
#  W = average wait time
#  L = average queue length
#  λ = average service rate (completions/min)
# ================================================================

from collections import deque
from datetime import datetime
from typing import Optional


class RollingAverage:
    """Fixed-window rolling average — O(1) update."""

    def __init__(self, window: int = 20):
        self._window = window
        self._values: deque[float] = deque(maxlen=window)

    def update(self, value: float) -> None:
        self._values.append(value)

    def get(self) -> float:
        if not self._values:
            return 15.0   # default 15 min if no data yet
        return sum(self._values) / len(self._values)

    def count(self) -> int:
        return len(self._values)


class WaitTimeEstimator:
    """
    Real-time wait time estimation per (doctor_id, branch_id).
    Uses Little's Law: W = L / λ
    λ is maintained as a rolling average of consultation durations.
    """

    def __init__(self):
        # Rolling avg consultation duration in minutes
        self._service_rate = RollingAverage(window=20)
        self._last_updated: Optional[datetime] = None

    def record_completion(self, duration_mins: float) -> None:
        """Call when a consultation ends. Updates λ."""
        if duration_mins > 0:
            self._service_rate.update(duration_mins)
        self._last_updated = datetime.utcnow()

    def estimate(self, queue_position: int, queue_length: int) -> dict:
        """
        Estimate wait time for a patient at given queue_position.
        Returns full breakdown dict.
        O(1).
        """
        avg_consult_mins = self._service_rate.get()          # avg duration per patient
        service_rate_per_min = 1.0 / avg_consult_mins        # λ = completions per minute

        # Little's Law: W = L / λ  →  W = L × avg_duration
        # For a specific position: W_position = position × avg_duration
        estimated_wait = queue_position * avg_consult_mins

        return {
            "estimated_wait_mins":  round(estimated_wait, 1),
            "queue_length":         queue_length,
            "queue_position":       queue_position,
            "service_rate":         round(service_rate_per_min, 4),
            "avg_consult_mins":     round(avg_consult_mins, 1),
            "samples_used":         self._service_rate.count(),
        }


# Registry
_estimators: dict[tuple[int, int], WaitTimeEstimator] = {}


def get_estimator(doctor_id: int, branch_id: int) -> WaitTimeEstimator:
    key = (doctor_id, branch_id)
    if key not in _estimators:
        _estimators[key] = WaitTimeEstimator()
    return _estimators[key]
