from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from titanfuse.config import TrainConfig
from titanfuse.errors import BackendError


class Backend(Protocol):
    name: str

    def describe(self, cfg: TrainConfig) -> str: ...

    def plan(self, cfg: TrainConfig) -> dict: ...

    def install_hint(self) -> str: ...


@dataclass
class UnslothBackend:
    """Consumer-GPU LoRA / QLoRA fine-tuning (Unsloth)."""

    name: str = "unsloth"

    def describe(self, cfg: TrainConfig) -> str:
        quant = "4-bit QLoRA" if cfg.use_4bit else "LoRA"
        return (
            f"Unsloth {quant} SFT on {cfg.model} "
            f"(seq={cfg.max_seq_len}, r={cfg.lora_r}) — consumer GPU path"
        )

    def plan(self, cfg: TrainConfig) -> dict:
        return {
            "library": "unsloth",
            "entry": "FastLanguageModel.from_pretrained",
            "repo": "https://github.com/unslothai/unsloth",
            "quantization": "4bit" if cfg.use_4bit else "bf16",
            "peft": {"r": cfg.lora_r, "alpha": cfg.lora_alpha},
            "trainer": "SFTTrainer",
            "snippet": _unsloth_snippet(cfg),
        }

    def install_hint(self) -> str:
        return "pip install unsloth"


@dataclass
class LigerBackend:
    """Hugging Face training with LinkedIn Liger Triton kernels."""

    name: str = "liger"

    def describe(self, cfg: TrainConfig) -> str:
        return (
            f"Liger-Kernel HF path for {cfg.model}: fused RMSNorm/RoPE/loss "
            "(~+20% throughput, ~-60% memory vs vanilla HF)"
        )

    def plan(self, cfg: TrainConfig) -> dict:
        return {
            "library": "liger_kernel",
            "entry": "AutoLigerKernelForCausalLM.from_pretrained",
            "repo": "https://github.com/linkedin/Liger-Kernel",
            "kernels": ["RMSNorm", "RoPE", "SwiGLU", "FusedLinearCrossEntropy"],
            "apply": "apply_liger_kernel_to_llama / AutoLigerKernelForCausalLM",
            "snippet": _liger_snippet(cfg),
        }

    def install_hint(self) -> str:
        return "pip install liger-kernel"


@dataclass
class TorchTitanBackend:
    """PyTorch-native 4D-parallel pretrain (Meta TorchTitan)."""

    name: str = "torchtitan"

    def describe(self, cfg: TrainConfig) -> str:
        p = cfg.parallelism
        return (
            f"TorchTitan 4D parallel pretrain world={p.world_size()} "
            f"(DP={p.data_parallel} TP={p.tensor_parallel} "
            f"PP={p.pipeline_parallel} CP={p.context_parallel})"
        )

    def plan(self, cfg: TrainConfig) -> dict:
        p = cfg.parallelism
        return {
            "library": "torchtitan",
            "entry": "torchtitan.train",
            "repo": "https://github.com/pytorch/torchtitan",
            "parallelism": {
                "dp": p.data_parallel,
                "tp": p.tensor_parallel,
                "pp": p.pipeline_parallel,
                "cp": p.context_parallel,
                "world": p.world_size(),
            },
            "launch": f"torchrun --nproc_per_node={p.world_size()} -m torchtitan.train",
            "snippet": _titan_snippet(cfg),
        }

    def install_hint(self) -> str:
        return "pip install torchtitan  # or clone https://github.com/pytorch/torchtitan"


BACKENDS: dict[str, Backend] = {
    "unsloth": UnslothBackend(),
    "liger": LigerBackend(),
    "torchtitan": TorchTitanBackend(),
}


def get_backend(name: str) -> Backend:
    if name not in BACKENDS:
        raise BackendError(f"Unknown backend {name!r}. Choose from {sorted(BACKENDS)}")
    return BACKENDS[name]


def _unsloth_snippet(cfg: TrainConfig) -> str:
    return f'''from unsloth import FastLanguageModel
from trl import SFTTrainer

model, tokenizer = FastLanguageModel.from_pretrained(
    "{cfg.model}",
    max_seq_length={cfg.max_seq_len},
    load_in_4bit={cfg.use_4bit},
)
model = FastLanguageModel.get_peft_model(model, r={cfg.lora_r}, lora_alpha={cfg.lora_alpha})
# trainer = SFTTrainer(model=model, tokenizer=tokenizer, ...)
'''


def _liger_snippet(cfg: TrainConfig) -> str:
    return f'''from liger_kernel.transformers import AutoLigerKernelForCausalLM
from transformers import AutoTokenizer, TrainingArguments, Trainer

model = AutoLigerKernelForCausalLM.from_pretrained("{cfg.model}")
tokenizer = AutoTokenizer.from_pretrained("{cfg.model}")
# Trainer(model=model, args=TrainingArguments(output_dir="{cfg.output_dir}"), ...)
'''


def _titan_snippet(cfg: TrainConfig) -> str:
    p = cfg.parallelism
    return f'''# TorchTitan is launched with torchrun, not imported as a Trainer.
# See https://github.com/pytorch/torchtitan
torchrun --nproc_per_node={max(p.world_size(), 1)} -m torchtitan.train \\
  --job.config_file ./torchtitan/models/llama3/train_configs/debug_model.toml
'''
