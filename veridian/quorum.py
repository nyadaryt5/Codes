"""Stake-weighted quorum: an agent cannot equivocate on the same triple+time."""

from __future__ import annotations

from collections import defaultdict

from veridian.errors import IntegrityError
from veridian.observation import Observation


class Quorum:
    def __init__(self, stake: dict[str, float] | None = None, threshold: float = 0.67) -> None:
        self.stake = stake or {}
        self.threshold = threshold
        self._seen: dict[tuple[str, str, int], str] = {}

    def admit(self, obs: Observation) -> None:
        key = (obs.agent_id, obs.triple.key(), obs.logical_time)
        prior = self._seen.get(key)
        if prior is not None and prior != obs.obs_id:
            raise IntegrityError(f"equivocation by {obs.agent_id} at t={obs.logical_time}")
        self._seen[key] = obs.obs_id

    def reached(self, observations: list[Observation]) -> bool:
        by_val: dict[str, float] = defaultdict(float)
        total = sum(self.stake.get(o.agent_id, 1.0) for o in observations) or 1.0
        for o in observations:
            by_val[repr(o.payload.get("value", o.payload))] += self.stake.get(o.agent_id, 1.0)
        return (max(by_val.values()) / total) >= self.threshold if by_val else False
