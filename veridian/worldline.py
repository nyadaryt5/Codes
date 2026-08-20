from __future__ import annotations

from veridian.observation import Observation, Triple


class Worldline:
    """Totally ordered observations for one triple, linked by parent hashes."""

    def __init__(self, triple: Triple) -> None:
        self.triple = triple
        self._obs: list[Observation] = []
        self._ids: set[str] = set()

    def append(self, obs: Observation) -> None:
        if obs.triple.key() != self.triple.key():
            raise ValueError("observation triple does not match worldline")
        if obs.obs_id in self._ids:
            return
        if self._obs:
            last = self._obs[-1]
            if last.obs_id not in obs.parents and obs.logical_time <= last.logical_time:
                raise ValueError("new observation must cite a parent or advance logical time")
        self._obs.append(obs)
        self._ids.add(obs.obs_id)

    def latest(self) -> Observation | None:
        return self._obs[-1] if self._obs else None

    def at(self, logical_time: int) -> Observation | None:
        chosen: Observation | None = None
        for obs in self._obs:
            if obs.logical_time <= logical_time:
                chosen = obs
            else:
                break
        return chosen

    def __len__(self) -> int:
        return len(self._obs)

    def observations(self) -> tuple[Observation, ...]:
        return tuple(self._obs)
