from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from titanfuse.config import TrainConfig, load_config
from titanfuse.stack import TitanFuse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="titanfuse",
        description="Combine TorchTitan + Liger-Kernel + Unsloth behind one CLI",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    plan = sub.add_parser("plan", help="Print the training plan for a YAML config")
    plan.add_argument("config", type=Path)
    plan.add_argument("--gpus", type=int, default=None)
    plan.add_argument("--vram", type=float, default=None)
    plan.add_argument("--json", action="store_true")

    rec = sub.add_parser("recommend", help="Recommend a backend from hardware hints")
    rec.add_argument("--workload", default="sft")
    rec.add_argument("--gpus", type=int, default=1)
    rec.add_argument("--vram", type=float, default=16.0)
    rec.add_argument("--pretrain", action="store_true")

    sub.add_parser("backends", help="List backends")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "backends":
        print("unsloth     — consumer GPU LoRA/QLoRA (https://github.com/unslothai/unsloth)")
        print("liger       — Triton kernels for HF training (https://github.com/linkedin/Liger-Kernel)")
        print("torchtitan  — 4D parallel pretrain (https://github.com/pytorch/torchtitan)")
        return 0
    if args.cmd == "recommend":
        cfg = TrainConfig(workload="pretrain" if args.pretrain else args.workload)
        fuse = TitanFuse(cfg, gpu_count=args.gpus, vram_gb=args.vram)
        print(fuse.summary())
        return 0
    if args.cmd == "plan":
        cfg = load_config(args.config)
        fuse = TitanFuse(cfg, gpu_count=args.gpus, vram_gb=args.vram)
        if args.json:
            json.dump(fuse.plan(), sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(fuse.summary())
            print()
            print(fuse.plan()["snippet"])
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
