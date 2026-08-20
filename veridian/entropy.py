"""Lattice entropy: how much of the store is still *alive* vs decayed/synthetic."""

from __future__ import annotations

from dataclasses import dataclass

from veridian.observation import Observation


@dataclass(frozen=True)
class EntropyReport:
    n_obs: int
    live_mass: float
    synthetic_mass: float
    mean_depth: float
    collapse_risk: float

    def to_dict(self) -> dict:
        return {
            "n_obs": self.n_obs,
            "live_mass": round(self.live_mass, 4),
            "synthetic_mass": round(self.synthetic_mass, 4),
            "mean_depth": round(self.mean_depth, 4),
            "collapse_risk": round(self.collapse_risk, 4),
        }


def report(observations: list[Observation], now_ns: int) -> EntropyReport:
    if not observations:
        return EntropyReport(0, 0.0, 0.0, 0.0, 0.0)
    live = 0.0
    syn = 0.0
    depth_acc = 0.0
    for o in observations:
        c = o.decayed_confidence(now_ns)
        live += c
        if o.gen_depth > 0:
            syn += c
        depth_acc += o.gen_depth * c
    mean_depth = depth_acc / live if live else 0.0
    # Collapse risk rises as synthetic mass and depth dominate live sensor mass.
    sensor = max(live - syn, 1e-9)
    risk = min(1.0, (syn / live) * (mean_depth / (1.0 + mean_depth))) if live else 0.0
    _ = sensor
    return EntropyReport(len(observations), live, syn, mean_depth, risk)
