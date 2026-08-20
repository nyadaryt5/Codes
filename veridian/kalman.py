"""Scalar Kalman filter over a numeric worldline (process + observation noise)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KalmanState:
    x: float
    p: float
    q: float
    r: float

    def to_dict(self) -> dict:
        return {"x": self.x, "p": self.p, "q": self.q, "r": self.r, "std": self.p**0.5}


def filter_values(values: list[float], *, q: float = 0.05, r: float = 1.0) -> KalmanState:
    if not values:
        raise ValueError("need at least one observation")
    x = values[0]
    p = 1.0
    for z in values[1:]:
        p = p + q
        k = p / (p + r)
        x = x + k * (z - x)
        p = (1 - k) * p
    return KalmanState(x=x, p=p, q=q, r=r)
