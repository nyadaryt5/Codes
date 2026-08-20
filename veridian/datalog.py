"""Horn-clause materialization over lattice beliefs (naive datalog)."""

from __future__ import annotations

from dataclasses import dataclass

from veridian.lattice import Lattice
from veridian.observation import Triple


@dataclass(frozen=True)
class Rule:
    """head(X) :- body1, body2...  Variables start with '?'."""

    head: tuple[str, str, str]
    body: tuple[tuple[str, str, str], ...]


def _is_var(tok: str) -> bool:
    return tok.startswith("?")


def _unify(pat: tuple[str, str, str], fact: Triple, env: dict[str, str]) -> dict[str, str] | None:
    nxt = dict(env)
    for p, f in zip(pat, (fact.subject, fact.predicate, fact.object)):
        if _is_var(p):
            if p in nxt and nxt[p] != f:
                return None
            nxt[p] = f
        elif p != f:
            return None
    return nxt


def _subst(pat: tuple[str, str, str], env: dict[str, str]) -> tuple[str, str, str]:
    return tuple(env.get(t, t) for t in pat)  # type: ignore[return-value]


def infer(lattice: Lattice, rules: list[Rule], *, max_rounds: int = 8) -> list[Triple]:
    facts = {o.triple.key(): o.triple for o in lattice.all_observations()}
    derived: list[Triple] = []
    for _ in range(max_rounds):
        grew = False
        snapshot = list(facts.values())
        for rule in rules:
            envs: list[dict[str, str]] = [{}]
            for atom in rule.body:
                nxt: list[dict[str, str]] = []
                for env in envs:
                    for fact in snapshot:
                        u = _unify(atom, fact, env)
                        if u is not None:
                            nxt.append(u)
                envs = nxt
            for env in envs:
                s, p, o = _subst(rule.head, env)
                trip = Triple(s, p, o)
                if trip.key() not in facts:
                    facts[trip.key()] = trip
                    derived.append(trip)
                    grew = True
        if not grew:
            break
    return derived


def materialize(lattice: Lattice, rules: list[Rule], *, agent_id: str = "reasoner") -> list[Triple]:
    """Write derived triples onto the lattice as gen_depth=1 claims."""
    from veridian.factory import claim

    derived = infer(lattice, rules)
    for trip in derived:
        claim(
            lattice,
            subject=trip.subject,
            predicate=trip.predicate,
            obj=trip.object,
            value=True,
            agent_id=agent_id,
            sensor_id="datalog",
            gen_depth=1,
            confidence=0.6,
        )
    return derived
