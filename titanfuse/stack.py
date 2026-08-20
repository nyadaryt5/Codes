from __future__ import annotations

from titanfuse.backends import get_backend
from titanfuse.config import TrainConfig


class TitanFuse:
    """Facade that picks Unsloth, Liger-Kernel, or TorchTitan and emits a run plan."""

    def __init__(self, cfg: TrainConfig, gpu_count: int | None = None, vram_gb: float | None = None):
        self.cfg = cfg
        self.backend_name = cfg.resolved_backend(gpu_count=gpu_count, vram_gb=vram_gb)
        self.backend = get_backend(self.backend_name)

    def summary(self) -> str:
        return (
            f"workload={self.cfg.workload} model={self.cfg.model}\n"
            f"backend={self.backend_name}\n"
            f"{self.backend.describe(self.cfg)}\n"
            f"install: {self.backend.install_hint()}"
        )

    def plan(self) -> dict:
        plan = self.backend.plan(self.cfg)
        plan["backend"] = self.backend_name
        plan["workload"] = self.cfg.workload
        plan["model"] = self.cfg.model
        plan["dataset"] = self.cfg.dataset
        plan["output_dir"] = self.cfg.output_dir
        if self.cfg.use_liger and self.backend_name != "liger":
            plan["liger_overlay"] = (
                "Optional: apply Liger kernels on HF models even when routing to Unsloth "
                "or Titan if the model path is Hugging Face compatible."
            )
        return plan
