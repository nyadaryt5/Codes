"""Twin a cooling loop: sensors, a lying model, decay, and a counterfactual."""

from __future__ import annotations

from veridian.counterfactual import without
from veridian.factory import claim
from veridian.lattice import Lattice
from veridian.observation import Triple
from veridian.query import Query, QueryEngine
from veridian.synthetic import GenerationGuard


def main() -> None:
    lat = Lattice(guard=GenerationGuard(max_depth=2), now_ns=1_000)
    t0 = 1_000_000_000
    a = claim(
        lat,
        subject="reactor.core",
        predicate="temperature_c",
        obj="loop-a",
        value=310.0,
        agent_id="thermocouple.1",
        sensor_id="k-type",
        confidence=0.95,
        half_life_s=60.0,
        wall_ns=t0,
    )
    b = claim(
        lat,
        subject="reactor.core",
        predicate="temperature_c",
        obj="loop-a",
        value=312.4,
        agent_id="thermocouple.2",
        sensor_id="k-type",
        confidence=0.9,
        half_life_s=60.0,
        wall_ns=t0 + 5_000_000_000,
        parents=(a.obs_id,),
    )
    lie = claim(
        lat,
        subject="reactor.core",
        predicate="temperature_c",
        obj="loop-a",
        value=180.0,
        agent_id="forecast.llm",
        sensor_id="synthetic",
        confidence=0.7,
        gen_depth=1,
        half_life_s=30.0,
        wall_ns=t0 + 8_000_000_000,
        parents=(b.obs_id,),
    )
    print("belief", lat.belief(Triple("reactor.core", "temperature_c", "loop-a")))
    print("entropy", lat.entropy().to_dict())
    print("query", QueryEngine(lat).run(Query(subject="reactor.core", min_confidence=0.1)))
    fork = without(lat, {lie.obs_id})
    print("what-if without the model", fork.entropy().to_dict())
    print("fork belief", fork.belief(Triple("reactor.core", "temperature_c", "loop-a")))


if __name__ == "__main__":
    main()
