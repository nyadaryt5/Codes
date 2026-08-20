from __future__ import annotations

from dataclasses import dataclass

from veridian.errors import QueryError
from veridian.lattice import Lattice
from veridian.merge import Belief
from veridian.observation import Triple


@dataclass(frozen=True)
class Query:
    subject: str | None = None
    predicate: str | None = None
    object: str | None = None
    min_confidence: float = 0.0
    max_depth: int | None = None
    as_of_ns: int | None = None


class QueryEngine:
    MATCH_COST = 0.005

    def __init__(self, lattice: Lattice) -> None:
        self.lattice = lattice

    def run(self, q: Query) -> list[dict]:
        if q.min_confidence < 0 or q.min_confidence > 1:
            raise QueryError("min_confidence must be in [0, 1]")
        hits: list[dict] = []
        seen_keys: set[str] = set()
        for obs in self.lattice.all_observations():
            t = obs.triple
            if q.subject is not None and t.subject != q.subject:
                continue
            if q.predicate is not None and t.predicate != q.predicate:
                continue
            if q.object is not None and t.object != q.object:
                continue
            key = t.key()
            if key in seen_keys:
                continue
            seen_keys.add(key)
            self.lattice.budget.charge(self.MATCH_COST, "query")
            belief = self.lattice.belief(t, now_ns=q.as_of_ns)
            if belief is None:
                continue
            if belief.confidence < q.min_confidence:
                continue
            if q.max_depth is not None and belief.gen_depth > q.max_depth:
                continue
            hits.append(_row(t, belief))
        hits.sort(key=lambda r: r["confidence"], reverse=True)
        return hits


def _row(triple: Triple, belief: Belief) -> dict:
    return {
        "subject": triple.subject,
        "predicate": triple.predicate,
        "object": triple.object,
        "value": belief.value,
        "confidence": round(belief.confidence, 6),
        "conflict": belief.conflict,
        "gen_depth": belief.gen_depth,
        "sources": list(belief.sources),
    }
