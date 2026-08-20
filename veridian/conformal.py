"""Split conformal prediction intervals for numeric worldlines."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    low: float
    mid: float
    high: float
    alpha: float

    def contains(self, x: float) -> bool:
        return self.low <= x <= self.high

    def to_dict(self) -> dict:
        return {"low": self.low, "mid": self.mid, "high": self.high, "alpha": self.alpha}


def predict(calibrate: list[float], point: float, *, alpha: float = 0.1) -> Interval:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if not calibrate:
        return Interval(point, point, point, alpha)
    residuals = sorted(abs(v - point) for v in calibrate)
    n = len(residuals)
    # split-conformal quantile index
    k = min(n - 1, max(0, int(((1 - alpha) * (n + 1)))))
    width = residuals[k] if k < n else residuals[-1]
    return Interval(point - width, point, point + width, alpha)
