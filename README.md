# TitanFuse

One CLI that **combines** three high-impact LLM training projects:

| Layer | Project | Role |
| --- | --- | --- |
| Cluster pretrain | [TorchTitan](https://github.com/pytorch/torchtitan) (Meta / PyTorch) | Native PyTorch 4D-parallel (DP × TP × PP × CP) blueprint |
| Kernel speedups | [Liger-Kernel](https://github.com/linkedin/Liger-Kernel) (LinkedIn) | Triton kernels — ~**+20%** throughput, ~**−60%** memory on HF trainers |
| Consumer fine-tune | [Unsloth](https://github.com/unslothai/unsloth) | LoRA / QLoRA on a single GPU |

This repo does **not** vendor those codebases. It is a **router, validator, memory heuristic, and recipe generator**.

```
workload / hardware
        │
        ▼
   TitanFuse.auto
   ├── 1× consumer GPU, SFT/QLoRA  → Unsloth
   ├── multi-GPU HF SFT / distill  → Liger-Kernel
   └── pretrain or 8+ GPUs         → TorchTitan
```

## Install

```bash
pip install -e ".[dev]"
pytest -q
```

Optional heavy backends:

```bash
pip install unsloth
pip install liger-kernel
# TorchTitan: https://github.com/pytorch/torchtitan
```

## CLI

```bash
titanfuse backends
titanfuse recommend --gpus 1 --vram 16
titanfuse recommend --pretrain --gpus 16
titanfuse plan configs/consumer_sft.yaml
titanfuse plan configs/hf_liger.yaml --json
titanfuse estimate configs/cluster_pretrain.yaml --gpus 32 --vram 80
titanfuse serve --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/` for the planner UI (`GET /health`, `GET /api/recommend`).

## Design

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Configs live in `configs/`. `backend: auto` uses GPU count, VRAM, and `workload`.

## License

MIT. Upstream projects keep their own licenses. Use them directly for training.

## Security

Do not commit tokens. Do not paste GitHub PATs into third-party scoring sites. See [SECURITY.md](SECURITY.md).
