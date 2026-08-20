import pytest
from veridian.errors import QueryError
from veridian.factory import claim
from veridian.lattice import Lattice
from veridian.query import Query, QueryEngine


def test_query_filters_subject_and_predicate():
    lat = Lattice()
    claim(lat, subject="alpha", predicate="temp", obj="c", value=1, agent_id="s")
    claim(lat, subject="beta", predicate="temp", obj="c", value=2, agent_id="s")
    claim(lat, subject="alpha", predicate="press", obj="kpa", value=3, agent_id="s")
    rows = QueryEngine(lat).run(Query(subject="alpha", predicate="temp"))
    assert len(rows) == 1
    assert rows[0]["subject"] == "alpha"
    assert rows[0]["predicate"] == "temp"


def test_query_object_filter():
    lat = Lattice()
    claim(lat, subject="r", predicate="p", obj="a", value=1, agent_id="s")
    claim(lat, subject="r", predicate="p", obj="b", value=2, agent_id="s")
    rows = QueryEngine(lat).run(Query(object="b"))
    assert len(rows) == 1
    assert rows[0]["object"] == "b"


def test_query_min_confidence_rejects_out_of_range():
    lat = Lattice()
    with pytest.raises(QueryError):
        QueryEngine(lat).run(Query(min_confidence=1.5))


def test_query_max_depth_filters_synthetic():
    lat = Lattice()
    claim(lat, subject="x", predicate="y", obj="z", value=1, agent_id="h", gen_depth=0)
    claim(lat, subject="m", predicate="y", obj="z", value=2, agent_id="llm", gen_depth=2)
    shallow = QueryEngine(lat).run(Query(max_depth=0))
    assert all(r["gen_depth"] == 0 for r in shallow)
    deep = QueryEngine(lat).run(Query(max_depth=3))
    assert len(deep) >= len(shallow)
