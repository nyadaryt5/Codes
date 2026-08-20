from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from veridian.observation import Observation


def _logit(p: float) -> float:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return math.log(p / (1 - p))


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)


@dataclass(frozen=True)
class Belief:
    value: Any
    confidence: float
    sources: tuple[str, ...]
    conflict: bool
    gen_depth: int


def merge_belief(observations: list[Observation], now_ns: int) -> Belief | None:
    """Log-odds pool for compatible payloads; flag conflict otherwise.

    Compatible means all payloads share the same canonical `value` key, or
    the entire payload is identical. Conflicts fork rather than average.
    """
    live = [o for o in observations if o.decayed_confidence(now_ns) >= 1e-6]
    if not live:
        return None

    def value_of(o: Observation) -> Any:
        if "value" in o.payload:
            return o.payload["value"]
        return o.payload

    groups: dict[str, list[Observation]] = {}
    for o in live:
        key = repr(value_of(o))
        groups.setdefault(key, []).append(o)

    winner_key = max(groups, key=lambda k: sum(x.decayed_confidence(now_ns) for x in groups[k]))
    winners = groups[winner_key]
    logit = 0.0
    sources = []
    depth = 0
    for o in winners:
        w = o.decayed_confidence(now_ns)
        logit += _logit(w)
        sources.append(o.obs_id)
        depth = max(depth, o.gen_depth)
    conf = _sigmoid(logit / max(len(winners), 1))
    return Belief(
        value=value_of(winners[0]),
        confidence=conf,
        sources=tuple(sources),
        conflict=len(groups) > 1,
        gen_depth=depth,
    )
