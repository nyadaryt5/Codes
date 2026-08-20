from pathlib import Path

import pytest
from titanfuse.config import Parallelism, TrainConfig, load_config
from titanfuse.errors import ConfigError


def test_parallelism_rejects_zero():
    with pytest.raises(ConfigError, match="data_parallel"):
        Parallelism(data_parallel=0).validate()


def test_from_dict_rejects_non_mapping():
    with pytest.raises(ConfigError, match="mapping"):
        TrainConfig.from_dict([])  # type: ignore[arg-type]


def test_from_dict_bad_parallelism_type():
    with pytest.raises(ConfigError, match="parallelism"):
        TrainConfig.from_dict({"parallelism": [1, 2]})


def test_validate_learning_rate():
    with pytest.raises(ConfigError, match="learning_rate"):
        TrainConfig.from_dict({"learning_rate": 0})


def test_validate_empty_model():
    with pytest.raises(ConfigError, match="model"):
        TrainConfig.from_dict({"model": "  "})


def test_validate_epochs():
    with pytest.raises(ConfigError, match="epochs"):
        TrainConfig.from_dict({"epochs": 0})


def test_resolved_backend_rejects_bad_gpus():
    cfg = TrainConfig(backend="auto")
    with pytest.raises(ConfigError, match="gpu_count"):
        cfg.resolved_backend(gpu_count=0, vram_gb=16)


def test_resolved_backend_rejects_bad_vram():
    cfg = TrainConfig(backend="auto")
    with pytest.raises(ConfigError, match="vram"):
        cfg.resolved_backend(gpu_count=1, vram_gb=0)


def test_to_dict_roundtrip_keys():
    cfg = TrainConfig(backend="liger", workload="dpo")
    data = cfg.to_dict()
    again = TrainConfig.from_dict(data)
    assert again.backend == "liger"
    assert again.workload == "dpo"


def test_load_invalid_yaml(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(p)


def test_leftover_keys_go_to_extra():
    cfg = TrainConfig.from_dict({"seed": 7, "model": "x-1B"})
    assert cfg.extra["seed"] == 7
