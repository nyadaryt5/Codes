"""Heuristic memory and token-cost estimates. Not a substitute for a profiler."""

from __future__ import annotations

from dataclasses import dataclass

from titanfuse.config import TrainConfig

# Rough parameter counts for common name fragments (billions).
_PARAM_B: tuple[tuple[str, float], ...] = (
    ("405b", 405.0),
    ("70b", 70.0),
    ("65b", 65.0),
    ("34b", 34.0),
    ("32b", 32.0),
    ("13b", 13.0),
    ("8b", 8.0),
    ("7b", 7.0),
    ("3b", 3.0),
    ("1b", 1.0),
    ("0.5b", 0.5),
)


def infer_params_billion(model: str) -> float:
    lower = model.lower()
    for token, billions in _PARAM_B:
        if token in lower:
            return billions
    return 1.0


@dataclass(frozen=True)
class ResourceEstimate:
    params_billion: float
    bytes_per_param: float
    weights_gb: float
    activations_gb: float
    optimizer_gb: float
    total_gb: float
    fits: bool
    notes: str

    def to_dict(self) -> dict:
        return {
            "params_billion": self.params_billion,
            "bytes_per_param": self.bytes_per_param,
            "weights_gb": round(self.weights_gb, 2),
            "activations_gb": round(self.activations_gb, 2),
            "optimizer_gb": round(self.optimizer_gb, 2),
            "total_gb": round(self.total_gb, 2),
            "fits": self.fits,
            "notes": self.notes,
        }


def estimate_memory(
    cfg: TrainConfig,
    *,
    backend: str,
    gpu_count: int = 1,
    vram_gb: float = 16.0,
) -> ResourceEstimate:
    params_b = infer_params_billion(cfg.model)
    params = params_b * 1e9
    if backend == "unsloth" and cfg.use_4bit:
        bytes_per = 0.5  # nf4
        opt_mult = 0.15  # LoRA adapters + 8-bit opt
        note = "QLoRA: 4-bit base weights, LoRA in bf16, 8-bit optimizer states"
    elif backend == "unsloth":
        bytes_per = 2.0
        opt_mult = 0.2
        note = "bf16 LoRA; base frozen"
    elif backend == "liger":
        bytes_per = 2.0
        opt_mult = 2.0  # Adam moments roughly 2x weights in mixed precision
        note = "Liger fused CE/RMSNorm cuts activation memory ~60% vs vanilla HF"
    else:
        bytes_per = 2.0
        opt_mult = 2.0
        note = "TorchTitan shards weights across 4D mesh; per-GPU share used below"

    weights_gb = params * bytes_per / 1e9
    seq = cfg.max_seq_len
    # Activation ballpark: tokens * hidden * layers; hidden ~ 128 * sqrt(params_b)
    hidden = max(512.0, 128.0 * (params_b**0.5) * 8)
    layers = max(8.0, 8.0 * (params_b**0.4))
    act = cfg.batch_size * seq * hidden * layers * 2.0 / 1e9
    if backend == "liger":
        act *= 0.4
    if backend == "unsloth":
        act *= 0.5
    if backend == "torchtitan":
        world = max(cfg.parallelism.world_size(), gpu_count)
        weights_gb /= max(world, 1)
        act /= max(cfg.parallelism.tensor_parallel * cfg.parallelism.pipeline_parallel, 1)
        note += f"; world={world}"

    optimizer_gb = weights_gb * opt_mult
    total = weights_gb + act + optimizer_gb
    per_gpu_budget = vram_gb * 0.85
    fits = total <= per_gpu_budget if backend != "torchtitan" else total <= per_gpu_budget
    return ResourceEstimate(
        params_billion=params_b,
        bytes_per_param=bytes_per,
        weights_gb=weights_gb,
        activations_gb=act,
        optimizer_gb=optimizer_gb,
        total_gb=total,
        fits=fits,
        notes=note,
    )
