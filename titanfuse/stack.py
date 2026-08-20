from __future__ import annotations

from titanfuse.backends import get_backend
from titanfuse.config import TrainConfig
from titanfuse.estimate import estimate_memory


class TitanFuse:
    """Facade that picks Unsloth, Liger-Kernel, or TorchTitan and emits a run plan."""

    def __init__(self, cfg: TrainConfig, gpu_count: int | None = None, vram_gb: float | None = None):
        self.cfg = cfg
        self.gpu_count = gpu_count if gpu_count is not None else 1
        self.vram_gb = vram_gb if vram_gb is not None else 16.0
        self.backend_name = cfg.resolved_backend(gpu_count=self.gpu_count, vram_gb=self.vram_gb)
        self.backend = get_backend(self.backend_name)

    def summary(self) -> str:
        est = self.estimate()
        fit = "fits" if est["fits"] else "may OOM"
        return (
            f"workload={self.cfg.workload} model={self.cfg.model}\n"
            f"backend={self.backend_name}\n"
            f"{self.backend.describe(self.cfg)}\n"
            f"memory≈{est['total_gb']} GB/GPU ({fit})\n"
            f"install: {self.backend.install_hint()}"
        )

    def estimate(self) -> dict:
        return estimate_memory(
            self.cfg,
            backend=self.backend_name,
            gpu_count=self.gpu_count,
            vram_gb=self.vram_gb,
        ).to_dict()

    def plan(self) -> dict:
        plan = self.backend.plan(self.cfg)
        plan["backend"] = self.backend_name
        plan["workload"] = self.cfg.workload
        plan["model"] = self.cfg.model
        plan["dataset"] = self.cfg.dataset
        plan["output_dir"] = self.cfg.output_dir
        plan["global_batch_size"] = self.cfg.global_batch_size()
        plan["estimate"] = self.estimate()
        if self.cfg.use_liger and self.backend_name != "liger":
            plan["liger_overlay"] = (
                "Optional: apply Liger kernels on HF models even when routing to Unsloth "
                "or Titan if the model path is Hugging Face compatible."
            )
        return plan
