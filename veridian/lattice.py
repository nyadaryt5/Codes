from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from veridian.budget import EnergyBudget
from veridian.entropy import EntropyReport
from veridian.entropy import report as entropy_report
from veridian.errors import IntegrityError
from veridian.hlc import HLC
from veridian.kalman import KalmanState, filter_values
from veridian.merge import Belief, merge_belief
from veridian.merkle import MerkleLog
from veridian.observation import Observation, Triple
from veridian.quorum import Quorum
from veridian.synthetic import GenerationGuard
from veridian.worldline import Worldline


class Lattice:
    """Append-only DAG of observations, indexed by triple worldlines."""

    APPEND_COST = 0.01
    BELIEF_COST = 0.02

    def __init__(
        self,
        *,
        budget: EnergyBudget | None = None,
        guard: GenerationGuard | None = None,
        now_ns: int = 0,
    ) -> None:
        self.budget = budget or EnergyBudget(joules=1_000.0)
        self.guard = guard or GenerationGuard(max_depth=3)
        self.now_ns = now_ns
        self._by_id: dict[str, Observation] = {}
        self._lines: dict[str, Worldline] = {}
        self._children: dict[str, list[str]] = defaultdict(list)
        self.clock = 0
        self.merkle = MerkleLog()
        self.hlc = HLC(wall_ns=now_ns)
        self.quorum = Quorum()

    def observe(self, obs: Observation) -> Observation:
        self.guard.check(obs)
        for parent in obs.parents:
            if parent not in self._by_id:
                raise IntegrityError(f"unknown parent {parent}")
        if obs.obs_id in self._by_id:
            return self._by_id[obs.obs_id]
        self.quorum.admit(obs)
        self.budget.charge(self.APPEND_COST, "append")
        self._by_id[obs.obs_id] = obs
        self.merkle.append(obs.obs_id)
        self.hlc.merge(obs.wall_ns, obs.logical_time, obs.wall_ns)
        key = obs.triple.key()
        if key not in self._lines:
            self._lines[key] = Worldline(obs.triple)
        self._lines[key].append(obs)
        for parent in obs.parents:
            self._children[parent].append(obs.obs_id)
        self.clock = max(self.clock, obs.logical_time)
        self.now_ns = max(self.now_ns, obs.wall_ns)
        return obs

    def get(self, obs_id: str) -> Observation | None:
        return self._by_id.get(obs_id)

    def worldline(self, triple: Triple) -> Worldline | None:
        return self._lines.get(triple.key())

    def belief(self, triple: Triple, *, now_ns: int | None = None) -> Belief | None:
        self.budget.charge(self.BELIEF_COST, "belief")
        line = self.worldline(triple)
        if line is None:
            return None
        t = now_ns if now_ns is not None else self.now_ns
        return merge_belief(list(line.observations()), t)

    def entropy(self, *, now_ns: int | None = None) -> EntropyReport:
        t = now_ns if now_ns is not None else self.now_ns
        return entropy_report(list(self._by_id.values()), t)

    def heads(self) -> list[Observation]:
        return [o for oid, o in self._by_id.items() if not self._children[oid]]

    def ancestors(self, obs_id: str) -> list[Observation]:
        out: list[Observation] = []
        seen: set[str] = set()
        stack = [obs_id]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            node = self._by_id.get(current)
            if node is None:
                continue
            out.append(node)
            stack.extend(node.parents)
        return out

    def all_observations(self) -> Iterable[Observation]:
        return self._by_id.values()

    def numeric_series(self, triple: Triple) -> list[float]:
        line = self.worldline(triple)
        if line is None:
            return []
        out: list[float] = []
        for o in line.observations():
            val = o.payload.get("value")
            if isinstance(val, (int, float)):
                out.append(float(val))
        return out

    def kalman(self, triple: Triple) -> KalmanState | None:
        series = self.numeric_series(triple)
        if not series:
            return None
        return filter_values(series)

    def snapshot(self) -> dict:
        return {
            "clock": self.clock,
            "now_ns": self.now_ns,
            "n": len(self._by_id),
            "merkle_root": self.merkle.root,
            "hlc": list(self.hlc.tuple()),
            "budget": self.budget.to_dict(),
            "entropy": self.entropy().to_dict(),
            "observations": [o.to_dict() for o in self._by_id.values()],
        }

    @classmethod
    def from_snapshot(cls, data: dict, **kwargs) -> Lattice:
        kwargs.setdefault("budget", EnergyBudget(joules=1_000_000.0))
        lat = cls(now_ns=int(data.get("now_ns", 0)), **kwargs)
        # Insert in an order that satisfies parents: Kahn-style by logical_time.
        obs = sorted(
            (Observation.from_dict(raw) for raw in data.get("observations", [])),
            key=lambda o: (o.logical_time, o.obs_id),
        )
        for o in obs:
            lat.observe(o)
        return lat
