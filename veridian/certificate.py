"""Compact audit certificate: Merkle inclusion + decayed belief at time T."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from veridian.hashutil import canonical_json, sha256_hex
from veridian.lattice import Lattice
from veridian.merkle import InclusionProof
from veridian.observation import Triple


@dataclass
class Certificate:
    triple: Triple
    as_of_ns: int
    value: Any
    confidence: float
    conflict: bool
    merkle_root: str
    proof: InclusionProof | None
    digest: str

    def verify(self, expected_root: str) -> bool:
        if self.merkle_root != expected_root:
            return False
        if self.proof is None:
            return False
        return self.proof.verify() and self.proof.root == expected_root

    def to_dict(self) -> dict:
        return {
            "triple": self.triple.key(),
            "as_of_ns": self.as_of_ns,
            "value": self.value,
            "confidence": self.confidence,
            "conflict": self.conflict,
            "merkle_root": self.merkle_root,
            "proof": None if self.proof is None else self.proof.to_dict(),
            "digest": self.digest,
        }


def issue(lattice: Lattice, triple: Triple, *, as_of_ns: int | None = None) -> Certificate | None:
    t = as_of_ns if as_of_ns is not None else lattice.now_ns
    belief = lattice.belief(triple, now_ns=t)
    if belief is None or not belief.sources:
        return None
    leaf = belief.sources[-1]
    proof = lattice.merkle.prove(leaf)
    body = {
        "triple": triple.key(),
        "as_of_ns": t,
        "value": belief.value,
        "confidence": belief.confidence,
        "root": lattice.merkle.root,
        "leaf": leaf,
    }
    digest = sha256_hex(canonical_json(body))
    return Certificate(
        triple=triple,
        as_of_ns=t,
        value=belief.value,
        confidence=belief.confidence,
        conflict=belief.conflict,
        merkle_root=lattice.merkle.root,
        proof=proof,
        digest=digest,
    )
