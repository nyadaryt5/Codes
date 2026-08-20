"""Geohash-like spatial index for (lat, lon) payloads — robot / IoT maps."""

from __future__ import annotations

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash(lat: float, lon: float, precision: int = 8) -> str:
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError("lat/lon out of range")
    lat_int = (-90.0, 90.0)
    lon_int = (-180.0, 180.0)
    bits: list[int] = []
    lon_bit = True
    while len(bits) < precision * 5:
        if lon_bit:
            mid = (lon_int[0] + lon_int[1]) / 2
            if lon >= mid:
                bits.append(1)
                lon_int = (mid, lon_int[1])
            else:
                bits.append(0)
                lon_int = (lon_int[0], mid)
        else:
            mid = (lat_int[0] + lat_int[1]) / 2
            if lat >= mid:
                bits.append(1)
                lat_int = (mid, lat_int[1])
            else:
                bits.append(0)
                lat_int = (lat_int[0], mid)
        lon_bit = not lon_bit
    chars = []
    for i in range(0, len(bits), 5):
        n = 0
        for b in bits[i : i + 5]:
            n = (n << 1) | b
        chars.append(_BASE32[n])
    return "".join(chars)


def neighbors(hash_: str) -> list[str]:
    """Prefix neighbors: same cell plus shorter prefixes (containment)."""
    return [hash_[:k] for k in range(1, len(hash_) + 1)]
