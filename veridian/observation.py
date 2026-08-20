from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from veridian.hashutil import canonical_json, sha256_hex


@dataclass(frozen=True)
class Triple:
    """A grounded statement: subject —predicate→ object."""

    subject: str
    predicate: str
    object: str

    def key(self) -> str:
        return f"{self.subject}|{self.predicate}|{self.object}"


@dataclass(frozen=True)
class Observation:
    """An append-only, content-addressed fact with causal parents.

    `gen_depth` is 0 for human/sensor, n+1 if a model synthesized from depth-n
    material. Training pipelines can refuse depth above a policy cap to slow
    synthetic-data collapse.
    """

    triple: Triple
    payload: dict[str, Any]
    agent_id: str
    sensor_id: str
    logical_time: int
    wall_ns: int
    confidence: float
    half_life_s: float
    gen_depth: int
    parents: tuple[str, ...] = ()
    obs_id: str = field(default="")

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if self.half_life_s <= 0:
            raise ValueError("half_life_s must be positive")
        if self.gen_depth < 0:
            raise ValueError("gen_depth must be >= 0")
        if not self.obs_id:
            object.__setattr__(self, "obs_id", self.compute_id())

    def compute_id(self) -> str:
        body = {
            "triple": asdict(self.triple),
            "payload": self.payload,
            "agent_id": self.agent_id,
            "sensor_id": self.sensor_id,
            "logical_time": self.logical_time,
            "wall_ns": self.wall_ns,
            "confidence": self.confidence,
            "half_life_s": self.half_life_s,
            "gen_depth": self.gen_depth,
            "parents": list(self.parents),
        }
        return sha256_hex(canonical_json(body))[:32]

    def decayed_confidence(self, now_ns: int) -> float:
        elapsed_s = max(0.0, (now_ns - self.wall_ns) / 1e9)
        # N(t) = N0 * 2^(-t/half_life)
        return self.confidence * (0.5 ** (elapsed_s / self.half_life_s))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["triple"] = asdict(self.triple)
        data["parents"] = list(self.parents)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Observation:
        payload = dict(data)
        triple = payload.pop("triple")
        parents = tuple(payload.pop("parents", ()))
        allowed = {
            "payload",
            "agent_id",
            "sensor_id",
            "logical_time",
            "wall_ns",
            "confidence",
            "half_life_s",
            "gen_depth",
            "obs_id",
        }
        kwargs = {k: v for k, v in payload.items() if k in allowed}
        return cls(triple=Triple(**triple), parents=parents, **kwargs)
