"""Laplace mechanism for exporting numeric beliefs."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


def _laplace(scale: float, rng: random.Random) -> float:
    u = rng.random() - 0.5
    return -scale * math.copysign(1.0, u) * math.log(1 - 2 * abs(u))


@dataclass
class PrivateNumber:
    value: float
    epsilon: float
    sensitivity: float

    def to_dict(self) -> dict:
        return {"value": self.value, "epsilon": self.epsilon, "sensitivity": self.sensitivity}


def release(true: float, *, epsilon: float, sensitivity: float, seed: int | None = None) -> PrivateNumber:
    if epsilon <= 0 or sensitivity < 0:
        raise ValueError("epsilon > 0 and sensitivity >= 0 required")
    rng = random.Random(seed)
    scale = sensitivity / epsilon
    return PrivateNumber(true + _laplace(scale, rng), epsilon, sensitivity)
