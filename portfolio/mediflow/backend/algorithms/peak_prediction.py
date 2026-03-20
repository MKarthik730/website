# ================================================================
#  algorithms/peak_prediction.py
#  Holt-Winters Triple Exponential Smoothing — O(n) per forecast
#  Captures level + trend + seasonality for appointment demand
# ================================================================

import math
from typing import Optional


class HoltWinters:
    """
    Triple Exponential Smoothing (additive Holt-Winters).
    alpha: level smoothing
    beta:  trend smoothing
    gamma: seasonal smoothing
    period: seasonality length (e.g. 24 for hourly, 7 for weekly)
    """

    def __init__(
        self,
        alpha:  float = 0.3,
        beta:   float = 0.1,
        gamma:  float = 0.2,
        period: int   = 24,   # 24 hours
    ):
        self.alpha  = alpha
        self.beta   = beta
        self.gamma  = gamma
        self.period = period

        self._level:    float       = 0.0
        self._trend:    float       = 0.0
        self._seasonal: list[float] = [0.0] * period
        self._fitted:   list[float] = []
        self._is_trained: bool      = False

    def _init_components(self, series: list[float]) -> None:
        n = len(series)
        if n < self.period * 2:
            # Pad if not enough data
            series = series + [sum(series) / len(series)] * (self.period * 2 - n)

        # Initial level = mean of first period
        self._level = sum(series[:self.period]) / self.period

        # Initial trend = avg difference between first two periods
        self._trend = (
            sum(series[self.period: self.period * 2]) -
            sum(series[:self.period])
        ) / (self.period ** 2)

        # Initial seasonal indices
        period_avgs = [
            sum(series[i * self.period: (i + 1) * self.period]) / self.period
            for i in range(n // self.period)
        ]
        self._seasonal = [
            series[i] / period_avgs[0] if period_avgs[0] != 0 else 1.0
            for i in range(self.period)
        ]

    def fit(self, series: list[float]) -> "HoltWinters":
        """Train on historical series. O(n)."""
        if len(series) < 2:
            return self
        self._init_components(series)
        self._fitted = []

        for i, y in enumerate(series):
            s = i % self.period
            prev_level = self._level
            prev_trend = self._trend

            self._level    = self.alpha * (y / max(self._seasonal[s], 0.001)) + (1 - self.alpha) * (prev_level + prev_trend)
            self._trend    = self.beta  * (self._level - prev_level)           + (1 - self.beta)  * prev_trend
            self._seasonal[s] = self.gamma * (y / max(self._level, 0.001))    + (1 - self.gamma) * self._seasonal[s]
            self._fitted.append((self._level + self._trend) * self._seasonal[s])

        self._is_trained = True
        return self

    def forecast(self, steps: int = 24) -> list[float]:
        """Forecast next `steps` values. O(steps)."""
        if not self._is_trained:
            return [0.0] * steps
        forecasts = []
        level, trend = self._level, self._trend
        seasonal = self._seasonal.copy()

        for h in range(1, steps + 1):
            s = (h - 1) % self.period
            f = (level + h * trend) * seasonal[s]
            forecasts.append(max(0.0, round(f, 2)))

        return forecasts

    def peak_hours(self, steps: int = 24, top_n: int = 3) -> list[int]:
        """Return indices of top-N peak hours in the forecast window."""
        fc = self.forecast(steps)
        indexed = sorted(enumerate(fc), key=lambda x: -x[1])
        return [i for i, _ in indexed[:top_n]]


# ----------------------------------------------------------------
#  Per-branch, per-department forecaster registry
# ----------------------------------------------------------------

_forecasters: dict[tuple[int, int], HoltWinters] = {}


def get_forecaster(branch_id: int, department_id: int) -> HoltWinters:
    key = (branch_id, department_id)
    if key not in _forecasters:
        _forecasters[key] = HoltWinters()
    return _forecasters[key]


def train_forecaster(
    branch_id:     int,
    department_id: int,
    history:       list[float],
) -> list[float]:
    """Train and return 24-hour forecast."""
    hw = get_forecaster(branch_id, department_id)
    hw.fit(history)
    return hw.forecast(24)
