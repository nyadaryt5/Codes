from pathlib import Path

from titanfuse.config import TrainConfig, load_config
from titanfuse.stack import TitanFuse


ROOT = Path(__file__).resolve().parents[1]


def test_auto_consumer():
    cfg = TrainConfig(backend="auto", workload="sft")
    fuse = TitanFuse(cfg, gpu_count=1, vram_gb=16)
    assert fuse.backend_name == "unsloth"


def test_auto_multi_gpu():
    cfg = TrainConfig(backend="auto", workload="sft", use_4bit=False)
    fuse = TitanFuse(cfg, gpu_count=4, vram_gb=80)
    assert fuse.backend_name == "liger"


def test_auto_pretrain():
    cfg = TrainConfig(backend="auto", workload="pretrain")
    fuse = TitanFuse(cfg, gpu_count=1, vram_gb=16)
    assert fuse.backend_name == "torchtitan"


def test_yaml_configs_load():
    for name in ("consumer_sft.yaml", "hf_liger.yaml", "cluster_pretrain.yaml", "auto.yaml"):
        cfg = load_config(ROOT / "configs" / name)
        plan = TitanFuse(cfg).plan()
        assert "snippet" in plan
        assert plan["repo"].startswith("https://github.com/")


def test_titan_world_size():
    cfg = load_config(ROOT / "configs" / "cluster_pretrain.yaml")
    assert cfg.parallelism.world_size() == 32
