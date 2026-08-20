"""Fragile watermark in numeric payloads so synthetic values can be detected later."""

from __future__ import annotations

from veridian.hashutil import sha256_hex


def embed(value: float, secret: str, bits: int = 8) -> float:
    digest = sha256_hex(secret, f"{value:.12g}")
    n = int(digest[:4], 16) % (2**bits)
    # Encode in the 1e-6 decimal band — enough for detection, tiny vs sensors.
    return value + n * 1e-8


def extract(value: float, secret: str, bits: int = 8) -> int:
    digest = sha256_hex(secret, f"{round(value, 6):.12g}")
    return int(digest[:4], 16) % (2**bits)


def matches(observed: float, claimed_plain: float, secret: str, bits: int = 8) -> bool:
    expected = embed(claimed_plain, secret, bits)
    return abs(observed - expected) < 5e-9
