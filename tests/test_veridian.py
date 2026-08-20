from pathlib import Path

import pytest

from veridian.budget import EnergyBudget
from veridian.cli import main
from veridian.counterfactual import without
from veridian.errors import BudgetExhausted, DepthPolicyError, IntegrityError
from veridian.factory import claim
from veridian.lattice import Lattice
from veridian.merge import merge_belief
from veridian.observation import Observation, Triple
from veridian.query import Query, QueryEngine
from veridian.store import load, save
from veridian.synthetic import GenerationGuard


def _obs(**kwargs) -> Observation:
    base = dict(
        triple=Triple("s", "p", "o"),
        payload={"value": 1},
        agent_id="a",
        sensor_id="x",
        logical_time=1,
        wall_ns=0,
        confidence=0.8,
        half_life_s=100.0,
        gen_depth=0,
        parents=(),
    )
    base.update(kwargs)
    return Observation(**base)


def test_content_address_stable():
    a = _obs()
    b = _obs()
    assert a.obs_id == b.obs_id


def test_decay():
    o = _obs(confidence=1.0, half_life_s=10.0, wall_ns=0)
    assert o.decayed_confidence(0) == 1.0
    assert abs(o.decayed_confidence(10_000_000_000) - 0.5) < 1e-9


def test_unknown_parent():
    lat = Lattice()
    with pytest.raises(IntegrityError):
        lat.observe(_obs(parents=("deadbeef",)))


def test_depth_guard():
    lat = Lattice(guard=GenerationGuard(max_depth=0))
    with pytest.raises(DepthPolicyError):
        lat.observe(_obs(gen_depth=1))


def test_merge_conflict():
    a = _obs(payload={"value": 1}, confidence=0.9, logical_time=1)
    b = _obs(payload={"value": 9}, confidence=0.4, logical_time=2, agent_id="b")
    belief = merge_belief([a, b], now_ns=0)
    assert belief is not None
    assert belief.conflict
    assert belief.value == 1


def test_query_and_budget():
    lat = Lattice(budget=EnergyBudget(joules=10))
    claim(lat, subject="room", predicate="co2", obj="ppm", value=420, agent_id="nds")
    rows = QueryEngine(lat).run(Query(subject="room", min_confidence=0.1))
    assert rows[0]["value"] == 420
    tiny = Lattice(budget=EnergyBudget(joules=0.001))
    with pytest.raises(BudgetExhausted):
        claim(tiny, subject="x", predicate="y", obj="z", value=1, agent_id="a")


def test_counterfactual_drops_descendants():
    lat = Lattice()
    a = claim(lat, subject="m", predicate="ok", obj="t", value=True, agent_id="h")
    b = claim(
        lat,
        subject="m",
        predicate="ok",
        obj="t",
        value=False,
        agent_id="llm",
        gen_depth=1,
        parents=(a.obs_id,),
    )
    fork = without(lat, {a.obs_id})
    assert fork.get(a.obs_id) is None
    assert fork.get(b.obs_id) is None


def test_roundtrip(tmp_path: Path):
    lat = Lattice()
    claim(lat, subject="k", predicate="v", obj="u", value="red", agent_id="h")
    path = tmp_path / "l.json"
    save(lat, path)
    other = load(path)
    assert other.snapshot()["n"] == 1


def test_cli_init_claim_query(tmp_path: Path):
    path = tmp_path / "l.json"
    assert main(["init", str(path)]) == 0
    assert (
        main(
            [
                "claim",
                str(path),
                "--subject",
                "bot",
                "--predicate",
                "pose",
                "--object",
                "map",
                "--value",
                "3",
            ]
        )
        == 0
    )
    assert main(["entropy", str(path)]) == 0
    assert main(["query", str(path), "--subject", "bot"]) == 0
