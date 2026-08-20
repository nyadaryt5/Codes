from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Literal

import yaml

from titanfuse.errors import ConfigError

BackendName = Literal["auto", "unsloth", "liger", "torchtitan"]
Workload = Literal["pretrain", "sft", "dpo", "distill"]

VALID_BACKENDS = frozenset({"auto", "unsloth", "liger", "torchtitan"})
VALID_WORKLOADS = frozenset({"pretrain", "sft", "dpo", "distill"})


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

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, int) or value < 1:
                raise ConfigError(f"parallelism.{name} must be an integer >= 1")


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

    def validate(self) -> None:
        if self.backend not in VALID_BACKENDS:
            raise ConfigError(f"backend must be one of {sorted(VALID_BACKENDS)}")
        if self.workload not in VALID_WORKLOADS:
            raise ConfigError(f"workload must be one of {sorted(VALID_WORKLOADS)}")
        if not self.model.strip():
            raise ConfigError("model must be a non-empty string")
        if self.max_seq_len < 32:
            raise ConfigError("max_seq_len must be >= 32")
        if self.batch_size < 1 or self.grad_accum < 1:
            raise ConfigError("batch_size and grad_accum must be >= 1")
        if self.learning_rate <= 0:
            raise ConfigError("learning_rate must be positive")
        if self.epochs < 1:
            raise ConfigError("epochs must be >= 1")
        if self.lora_r < 1 or self.lora_alpha < 1:
            raise ConfigError("lora_r and lora_alpha must be >= 1")
        self.parallelism.validate()

    def resolved_backend(self, gpu_count: int | None = None, vram_gb: float | None = None) -> str:
        self.validate()
        if self.backend != "auto":
            return self.backend
        gpus = gpu_count if gpu_count is not None else 1
        vram = vram_gb if vram_gb is not None else 16.0
        if gpus < 1:
            raise ConfigError("gpu_count must be >= 1")
        if vram <= 0:
            raise ConfigError("vram_gb must be positive")
        if self.workload == "pretrain" or gpus >= 8:
            return "torchtitan"
        if gpus >= 2 or (not self.use_4bit and vram >= 40):
            return "liger"
        return "unsloth"

    def global_batch_size(self) -> int:
        return self.batch_size * self.grad_accum * self.parallelism.data_parallel

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrainConfig:
        if not isinstance(data, dict):
            raise ConfigError("Config must be a mapping")
        payload = dict(data)
        para = payload.pop("parallelism", None) or {}
        extra = dict(payload.pop("extra", {}) or {})
        known = {f.name for f in fields(cls)}
        kwargs = {k: v for k, v in payload.items() if k in known and k != "parallelism"}
        leftover = {k: v for k, v in payload.items() if k not in known}
        extra.update(leftover)
        if not isinstance(para, dict):
            raise ConfigError("parallelism must be a mapping")
        try:
            cfg = cls(
                parallelism=Parallelism(**para) if para else Parallelism(),
                extra=extra,
                **kwargs,
            )
        except TypeError as exc:
            raise ConfigError(str(exc)) from exc
        cfg.validate()
        return cfg


def load_config(path: str | Path) -> TrainConfig:
    target = Path(path)
    if not target.is_file():
        raise ConfigError(f"Config file not found: {target}")
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML: {exc}") from exc
    return TrainConfig.from_dict(raw)
