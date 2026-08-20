"""In-process gossip: ingest foreign observations if parents exist or arrive together."""

from __future__ import annotations

from veridian.errors import IntegrityError
from veridian.hlc import HLC
from veridian.lattice import Lattice
from veridian.observation import Observation
from veridian.quorum import Quorum


class Peer:
    def __init__(self, name: str, lattice: Lattice, quorum: Quorum | None = None) -> None:
        self.name = name
        self.lattice = lattice
        self.hlc = HLC()
        self.quorum = quorum or Quorum()

    def gossip_from(self, other: "Peer") -> int:
        """Pull missing observations in causal order. Returns count ingested."""
        known = {o.obs_id for o in self.lattice.all_observations()}
        incoming = sorted(other.lattice.all_observations(), key=lambda o: (o.logical_time, o.obs_id))
        n = 0
        progressed = True
        pending = [o for o in incoming if o.obs_id not in known]
        while progressed and pending:
            progressed = False
            leftover: list[Observation] = []
            for obs in pending:
                if all(p in known or p in self.lattice._by_id for p in obs.parents):
                    try:
                        self.quorum.admit(obs)
                        self.lattice.observe(obs)
                        known.add(obs.obs_id)
                        self.hlc.merge(obs.wall_ns, obs.logical_time, obs.wall_ns)
                        n += 1
                        progressed = True
                    except IntegrityError:
                        leftover.append(obs)
                else:
                    leftover.append(obs)
            pending = leftover
        return n
