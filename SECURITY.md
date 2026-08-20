# Security

- Do not commit API keys, Hugging Face tokens, or GitHub PATs.
- `titanfuse serve` is a **local planner**. It does not run models, does not execute YAML, and does not fetch remote weights.
- Bind to `127.0.0.1` unless you have a reverse proxy and an allowlist.
- Never paste a GitHub personal access token into third-party “score my repo” sites that store tokens for “sales follow-up.” Use a **public repository URL** only.

Report issues via GitHub; do not open issues that contain secrets.
