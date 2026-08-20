from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

BackendName = Literal["auto", "unsloth", "liger", "torchtitan"]
Workload = Literal["pretrain", "sft", "dpo", "distill"]


@dataclass
class Parallelism:
    """TorchTitan-style 4D parallelism (used when backend=torchtitan)."""

    data_parallel: int = 1
    tensor_parallel: int = 1
    pipeline_parallel: int = 1
    context_parallel: int = 1

    def world_size(self) -> int:
        return (
            self.data_parallel
            * self.tensor_parallel
            * self.pipeline_parallel
            * self.context_parallel
        )


@dataclass
class TrainConfig:
    backend: BackendName = "auto"
    workload: Workload = "sft"
    model: str = "meta-llama/Llama-3.2-1B"
    dataset: str = "yahma/alpaca-cleaned"
    max_seq_len: int = 2048
    batch_size: int = 2
    grad_accum: int = 4
    learning_rate: float = 2e-4
    epochs: int = 1
    lora_r: int = 16
    lora_alpha: int = 16
    use_4bit: bool = True
    use_liger: bool = True
    output_dir: str = "outputs"
    parallelism: Parallelism = field(default_factory=Parallelism)
    extra: dict[str, Any] = field(default_factory=dict)

    def resolved_backend(self, gpu_count: int | None = None, vram_gb: float | None = None) -> str:
        if self.backend != "auto":
            return self.backend
        gpus = gpu_count if gpu_count is not None else 1
        vram = vram_gb if vram_gb is not None else 16.0
        if self.workload == "pretrain" or gpus >= 8:
            return "torchtitan"
        if gpus >= 2 or (not self.use_4bit and vram >= 40):
            return "liger"
        return "unsloth"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrainConfig:
        para = data.pop("parallelism", None) or {}
        extra = data.pop("extra", {}) or {}
        known = {f.name for f in cls.__dataclass_fields__.values()}
        kwargs = {k: v for k, v in data.items() if k in known and k != "parallelism"}
        leftover = {k: v for k, v in data.items() if k not in known}
        extra = {**extra, **leftover}
        return cls(parallelism=Parallelism(**para) if para else Parallelism(), extra=extra, **kwargs)


def load_config(path: str | Path) -> TrainConfig:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    if not isinstance(raw, dict):
        raise ValueError("Config must be a YAML mapping")
    return TrainConfig.from_dict(raw)
