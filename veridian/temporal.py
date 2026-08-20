"""Linear temporal logic lite over a boolean series sampled from a worldline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Trace:
    bits: tuple[bool, ...]

    def always(self) -> bool:
        return all(self.bits)

    def eventually(self) -> bool:
        return any(self.bits)

    def until(self, release: "Trace") -> bool:
        """φ U ψ: φ holds until ψ, and ψ happens at least once."""
        if len(release.bits) != len(self.bits):
            raise ValueError("traces must be the same length")
        for i, psi in enumerate(release.bits):
            if psi:
                return all(self.bits[:i])
        return False

    def next(self) -> bool:
        return bool(self.bits[1]) if len(self.bits) > 1 else False


def from_threshold(values: list[float], op: str, bound: float) -> Trace:
    ops = {
        ">": lambda v: v > bound,
        ">=": lambda v: v >= bound,
        "<": lambda v: v < bound,
        "<=": lambda v: v <= bound,
        "==": lambda v: abs(v - bound) < 1e-9,
    }
    if op not in ops:
        raise ValueError(f"unknown op {op}")
    fn = ops[op]
    return Trace(tuple(fn(v) for v in values))
