from __future__ import annotations

from veridian.errors import DepthPolicyError
from veridian.observation import Observation


class GenerationGuard:
    """Refuse observations that would push the lattice into model-on-model soup."""

    def __init__(self, max_depth: int = 2) -> None:
        if max_depth < 0:
            raise ValueError("max_depth must be >= 0")
        self.max_depth = max_depth

    def check(self, obs: Observation) -> None:
        if obs.gen_depth > self.max_depth:
            raise DepthPolicyError(
                f"gen_depth {obs.gen_depth} exceeds policy cap {self.max_depth}"
            )

    def child_depth(self, parents: list[Observation]) -> int:
        if not parents:
            return 0
        return 1 + max(p.gen_depth for p in parents)
