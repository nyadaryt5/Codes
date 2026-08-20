from titanfuse.config import TrainConfig
from titanfuse.estimate import estimate_memory, infer_params_billion


def test_infer_common_sizes():
    assert infer_params_billion("Llama-3.1-70B") == 70.0
    assert infer_params_billion("qwen2-7b-instruct") == 7.0
    assert infer_params_billion("unknown-model") == 1.0
    assert infer_params_billion("phi-14B") == 14.0


def test_unsloth_4bit_smaller_than_bf16():
    cfg = TrainConfig(backend="unsloth", model="x-8B", use_4bit=True)
    q = estimate_memory(cfg, backend="unsloth", vram_gb=16)
    cfg2 = TrainConfig(backend="unsloth", model="x-8B", use_4bit=False)
    f = estimate_memory(cfg2, backend="unsloth", vram_gb=16)
    assert q.bytes_per_param == 0.5
    assert q.total_gb < f.total_gb
    assert "QLoRA" in q.notes


def test_liger_reduces_activations_vs_titan_unsharded():
    cfg = TrainConfig(backend="liger", model="x-8B", use_4bit=False, batch_size=2, max_seq_len=2048)
    liger = estimate_memory(cfg, backend="liger", gpu_count=1, vram_gb=80)
    titan = estimate_memory(cfg, backend="torchtitan", gpu_count=1, vram_gb=80)
    assert liger.activations_gb < titan.activations_gb
    assert "Liger" in liger.notes


def test_titan_shards_across_world():
    cfg = TrainConfig(backend="torchtitan", model="x-8B")
    cfg.parallelism.data_parallel = 2
    cfg.parallelism.tensor_parallel = 2
    one = estimate_memory(cfg, backend="torchtitan", gpu_count=1, vram_gb=80)
    assert "world=" in one.notes
    assert one.to_dict()["fits"] in (True, False)


def test_resource_estimate_dict_keys():
    cfg = TrainConfig(model="x-1B")
    d = estimate_memory(cfg, backend="unsloth").to_dict()
    assert set(d) >= {"params_billion", "total_gb", "fits", "notes"}
