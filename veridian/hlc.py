"""Hybrid logical clocks: wall time + Lamport so distributed agents never go backwards."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HLC:
    wall_ns: int = 0
    logical: int = 0

    def stamp(self, now_ns: int) -> tuple[int, int]:
        if now_ns > self.wall_ns:
            self.wall_ns = now_ns
            self.logical = 0
        else:
            self.logical += 1
        return self.wall_ns, self.logical

    def merge(self, other_wall: int, other_logical: int, now_ns: int) -> tuple[int, int]:
        max_wall = max(self.wall_ns, other_wall, now_ns)
        if max_wall == self.wall_ns == other_wall:
            self.logical = max(self.logical, other_logical) + 1
        elif max_wall == self.wall_ns:
            self.logical += 1
        elif max_wall == other_wall:
            self.logical = other_logical + 1
        else:
            self.logical = 0
        self.wall_ns = max_wall
        return self.wall_ns, self.logical

    def tuple(self) -> tuple[int, int]:
        return self.wall_ns, self.logical
