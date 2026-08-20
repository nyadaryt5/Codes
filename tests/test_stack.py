from pathlib import Path

import pytest
from titanfuse.backends import get_backend
from titanfuse.cli import main
from titanfuse.config import TrainConfig, load_config
from titanfuse.errors import BackendError, ConfigError
from titanfuse.estimate import infer_params_billion
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
        assert "estimate" in plan


def test_titan_world_size():
    cfg = load_config(ROOT / "configs" / "cluster_pretrain.yaml")
    assert cfg.parallelism.world_size() == 32
    assert cfg.global_batch_size() == cfg.batch_size * cfg.grad_accum * cfg.parallelism.data_parallel


def test_invalid_backend():
    with pytest.raises(ConfigError):
        TrainConfig.from_dict({"backend": "megatron"})


def test_invalid_seq():
    with pytest.raises(ConfigError):
        TrainConfig.from_dict({"max_seq_len": 8})


def test_missing_file():
    with pytest.raises(ConfigError):
        load_config(ROOT / "configs" / "nope.yaml")


def test_unknown_backend_lookup():
    with pytest.raises(BackendError):
        get_backend("nope")


def test_infer_params():
    assert infer_params_billion("Llama-3.1-8B") == 8.0
    assert infer_params_billion("mystery") == 1.0


def test_qlora_uses_less_memory_than_bf16():
    q = TitanFuse(TrainConfig(backend="unsloth", use_4bit=True, model="x-8B")).estimate()
    f = TitanFuse(TrainConfig(backend="unsloth", use_4bit=False, model="x-8B")).estimate()
    assert q["total_gb"] < f["total_gb"]


def test_cli_backends(capsys):
    assert main(["backends"]) == 0
    out = capsys.readouterr().out
    assert "unsloth" in out and "liger" in out and "torchtitan" in out


def test_cli_plan_json(capsys):
    assert main(["plan", str(ROOT / "configs" / "consumer_sft.yaml"), "--json"]) == 0
    assert '"backend"' in capsys.readouterr().out


def test_cli_bad_config():
    assert main(["plan", str(ROOT / "missing.yaml")]) == 2
