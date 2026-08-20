# Architecture

```
YAML / CLI / HTTP
        │
        ▼
  TrainConfig.validate
        │
        ▼
  resolved_backend(auto | unsloth | liger | torchtitan)
        │
        ├── UnslothBackend   consumer QLoRA snippets
        ├── LigerBackend     HF + Triton kernel snippets
        └── TorchTitanBackend  4D mesh + torchrun
        │
        ▼
  estimate_memory  →  plan JSON
```

TitanFuse never launches distributed jobs. It is a **policy + recipe** layer so a single config can follow a model from laptop SFT to cluster pretrain.
