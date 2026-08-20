"""Fork the lattice: replay without a set of observation ids (a lie, a sensor)."""

from __future__ import annotations

from veridian.lattice import Lattice
from veridian.observation import Observation


def without(lattice: Lattice, drop_ids: set[str]) -> Lattice:
    """Return a new lattice that never saw `drop_ids` or their descendants."""
    banned = set(drop_ids)
    changed = True
    while changed:
        changed = False
        for obs in lattice.all_observations():
            if obs.obs_id in banned:
                continue
            if any(p in banned for p in obs.parents):
                banned.add(obs.obs_id)
                changed = True
    kept: list[Observation] = []
    for obs in lattice.all_observations():
        if obs.obs_id not in banned:
            kept.append(obs)
    kept.sort(key=lambda o: (o.logical_time, o.obs_id))
    fork = Lattice(
        budget=type(lattice.budget)(joules=lattice.budget.joules),
        guard=lattice.guard,
        now_ns=lattice.now_ns,
    )
    for obs in kept:
        fork.observe(obs)
    return fork
