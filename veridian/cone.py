"""Causal past and future cones — the light-cone of an observation."""

from __future__ import annotations

from veridian.lattice import Lattice
from veridian.observation import Observation


def past(lattice: Lattice, obs_id: str) -> list[Observation]:
    return lattice.ancestors(obs_id)


def future(lattice: Lattice, obs_id: str) -> list[Observation]:
    out: list[Observation] = []
    seen: set[str] = set()
    stack = [obs_id]
    children = lattice._children  # intentional: DAG adjacency
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        node = lattice.get(current)
        if node is None:
            continue
        if current != obs_id:
            out.append(node)
        stack.extend(children.get(current, []))
    return out


def incomparable(lattice: Lattice, a: str, b: str) -> bool:
    past_a = {o.obs_id for o in past(lattice, a)}
    past_b = {o.obs_id for o in past(lattice, b)}
    return a not in past_b and b not in past_a and a != b
