from __future__ import annotations

import json
from pathlib import Path

from veridian.lattice import Lattice


def save(lattice: Lattice, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lattice.snapshot(), indent=2, default=str), encoding="utf-8")


def load(path: Path) -> Lattice:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Lattice.from_snapshot(data)
