from __future__ import annotations

import time
from typing import Any

from veridian.lattice import Lattice
from veridian.observation import Observation, Triple


def tick_ns() -> int:
    return time.time_ns()


def claim(
    lattice: Lattice,
    *,
    subject: str,
    predicate: str,
    obj: str,
    value: Any,
    agent_id: str,
    sensor_id: str = "human",
    confidence: float = 0.8,
    half_life_s: float = 86_400.0,
    gen_depth: int = 0,
    parents: tuple[str, ...] = (),
    wall_ns: int | None = None,
) -> Observation:
    lattice.clock += 1
    obs = Observation(
        triple=Triple(subject, predicate, obj),
        payload={"value": value},
        agent_id=agent_id,
        sensor_id=sensor_id,
        logical_time=lattice.clock,
        wall_ns=wall_ns if wall_ns is not None else tick_ns(),
        confidence=confidence,
        half_life_s=half_life_s,
        gen_depth=gen_depth,
        parents=parents,
    )
    return lattice.observe(obs)
