from veridian.certificate import issue
from veridian.conformal import predict
from veridian.datalog import Rule, infer
from veridian.factory import claim
from veridian.federation import Peer
from veridian.geo import geohash, neighbors
from veridian.kalman import filter_values
from veridian.lattice import Lattice
from veridian.merkle import MerkleLog
from veridian.observation import Triple
from veridian.privacy import release
from veridian.temporal import from_threshold
from veridian.watermark import embed, matches
from veridian.cone import future, incomparable, past
from veridian.errors import IntegrityError
from veridian.quorum import Quorum
from veridian.observation import Observation
import pytest


def test_merkle_inclusion():
    log = MerkleLog()
    ids = []
    for i in range(7):
        ids.append(log.append(f"leaf{i}"))
    proof = log.prove("leaf3")
    assert proof.verify()
    bad = MerkleLog()
    bad.append("nope")
    assert not proof.verify() or proof.root != bad.root


def test_kalman_tracks_step():
    s = filter_values([0.0, 1.0, 2.0, 3.0, 4.0], q=0.2, r=0.5)
    assert s.x > 2.0


def test_ltl_until():
    hot = from_threshold([1, 1, 1, 5, 5], ">=", 1)
    trip = from_threshold([1, 1, 1, 5, 5], ">=", 5)
    assert hot.always()
    assert trip.eventually()
    assert hot.until(trip)


def test_conformal_covers():
    iv = predict([10.0, 10.2, 9.8, 10.1], 10.0, alpha=0.2)
    assert iv.contains(10.0)


def test_privacy_changes_value():
    p = release(42.0, epsilon=0.5, sensitivity=1.0, seed=7)
    assert p.value != 42.0


def test_geohash_stable():
    h = geohash(26.14, 91.77, precision=6)
    assert h == geohash(26.14, 91.77, precision=6)
    assert h[:3] in neighbors(h)


def test_watermark():
    w = embed(312.4, "reactor-secret")
    assert matches(w, 312.4, "reactor-secret")
    assert not matches(w, 312.4, "other")


def test_datalog_transitivity():
    lat = Lattice()
    claim(lat, subject="a", predicate="path", obj="b", value=True, agent_id="m")
    claim(lat, subject="b", predicate="path", obj="c", value=True, agent_id="m")
    rule = Rule(head=("?x", "path", "?z"), body=(("?x", "path", "?y"), ("?y", "path", "?z")))
    derived = infer(lat, [rule])
    assert any(t.subject == "a" and t.object == "c" for t in derived)


def test_certificate_verifies():
    lat = Lattice()
    claim(lat, subject="dock", predicate="free", obj="3", value=False, agent_id="lidar")
    cert = issue(lat, Triple("dock", "free", "3"))
    assert cert is not None
    assert cert.verify(lat.merkle.root)


def test_federation_and_cone():
    a = Peer("alpha", Lattice())
    b = Peer("beta", Lattice())
    o = claim(a.lattice, subject="bot", predicate="x", obj="m", value=1, agent_id="alpha")
    claim(a.lattice, subject="bot", predicate="x", obj="m", value=2, agent_id="alpha", parents=(o.obs_id,))
    n = b.gossip_from(a)
    assert n == 2
    ids = [x.obs_id for x in a.lattice.all_observations()]
    first, second = ids[0], ids[1]
    assert past(a.lattice, second)
    assert future(a.lattice, first)
    assert not incomparable(a.lattice, first, second)


def test_equivocation_rejected():
    q = Quorum()
    t = Triple("s", "p", "o")
    a = Observation(
        triple=t,
        payload={"value": 1},
        agent_id="evil",
        sensor_id="x",
        logical_time=1,
        wall_ns=0,
        confidence=0.9,
        half_life_s=10,
        gen_depth=0,
    )
    b = Observation(
        triple=t,
        payload={"value": 2},
        agent_id="evil",
        sensor_id="x",
        logical_time=1,
        wall_ns=0,
        confidence=0.9,
        half_life_s=10,
        gen_depth=0,
    )
    q.admit(a)
    with pytest.raises(IntegrityError):
        q.admit(b)


def test_lattice_kalman():
    lat = Lattice()
    for v in (10.0, 10.5, 11.0):
        claim(lat, subject="loop", predicate="temp", obj="a", value=v, agent_id="k")
    k = lat.kalman(Triple("loop", "temp", "a"))
    assert k is not None
    assert 10 <= k.x <= 11.2
