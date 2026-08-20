"""Incremental binary Merkle tree over observation ids (lexicographic leaves)."""

from __future__ import annotations

from dataclasses import dataclass

from veridian.hashutil import sha256_hex


def _node(left: str, right: str) -> str:
    return sha256_hex("n", left, right)


@dataclass(frozen=True)
class InclusionProof:
    leaf: str
    siblings: tuple[tuple[str, str], ...]  # (side, hash) side in {L,R}
    root: str

    def verify(self) -> bool:
        acc = self.leaf
        for side, sib in self.siblings:
            acc = _node(sib, acc) if side == "L" else _node(acc, sib)
        return acc == self.root

    def to_dict(self) -> dict:
        return {"leaf": self.leaf, "siblings": [list(s) for s in self.siblings], "root": self.root}


class MerkleLog:
    def __init__(self) -> None:
        self._leaves: list[str] = []
        self._root = sha256_hex("empty")

    def append(self, leaf: str) -> str:
        self._leaves.append(leaf)
        self._root = self._compute_root(self._leaves)
        return self._root

    @property
    def root(self) -> str:
        return self._root

    def prove(self, leaf: str) -> InclusionProof:
        if leaf not in self._leaves:
            raise KeyError(leaf)
        idx = self._leaves.index(leaf)
        layer = list(self._leaves)
        siblings: list[tuple[str, str]] = []
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            next_layer: list[str] = []
            for i in range(0, len(layer), 2):
                left, right = layer[i], layer[i + 1]
                if idx == i:
                    siblings.append(("R", right))
                    idx = len(next_layer)
                elif idx == i + 1:
                    siblings.append(("L", left))
                    idx = len(next_layer)
                next_layer.append(_node(left, right))
            layer = next_layer
        return InclusionProof(leaf=leaf, siblings=tuple(siblings), root=layer[0] if layer else self._root)

    @staticmethod
    def _compute_root(leaves: list[str]) -> str:
        if not leaves:
            return sha256_hex("empty")
        layer = list(leaves)
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            layer = [_node(layer[i], layer[i + 1]) for i in range(0, len(layer), 2)]
        return layer[0]
