# Contributing

1. Keep the three backends **adapters** — do not vendor TorchTitan, Liger, or Unsloth.
2. Validation lives in `TrainConfig.validate`. User errors raise `TitanFuseError` subclasses, never stack traces from the CLI.
3. Memory numbers in `estimate.py` are heuristics; tests should assert **ordering** (QLoRA < bf16), not exact GB.
4. Run `pytest -q` before opening a PR.
5. Python 3.10+, type hints on public APIs, no GPU required for tests.
