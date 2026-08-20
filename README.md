# Veridian

**A causal worldline lattice for software that must remember *why*.**

Neural nets have weights. Databases have rows. Neither has a **physics of memory**: claims that decay, disagree, cite their parents, and refuse to train on their own exhaust.

Veridian is that physics.

```
sensor ──► observation ──► worldline ──► lattice
                │              │
           half-life      log-odds merge
                │              │
           gen_depth      counterfactual fork
```

v0.3 is a **runtime**, not a notebook: hybrid logical clocks, Merkle inclusion proofs, Kalman worldlines, LTL-lite, gossip federation, Byzantine equivocation bans, datalog inference, conformal intervals, Laplace export, geohash, synthetic watermarks, and compact audit certificates.

Not a blockchain. Not a vector DB. Not a knowledge graph. An **append-only DAG of observations** with:

1. **Content-addressed provenance** — SHA-256 of canonical payload + causal parents
2. **Exponential half-life** — last March’s wiki page is not “true,” it is *cold*
3. **Conflict as a first-class value** — incompatible payloads fork; they are never averaged into mush
4. **Generation depth** — human/sensor = 0; a model quoting a model is 2; policy can refuse 3+ (synthetic collapse)
5. **Energy budgets** — every append/query costs joule-equivalents so agent loops terminate
6. **What-if** — drop a lying sensor and *all descendants* vanish with it

## Why this exists

Future stacks (robot fleets, multi-agent labs, regulated copilots, continual pretrain) fail in the same ways:

| Failure mode | Veridian primitive |
| --- | --- |
| Stale RAG | `decayed_confidence(now)` / `as_of_ns` |
| Agents clobber shared state | worldlines + logit merge |
| Model-on-model data collapse | `GenerationGuard` |
| Infinite tool use | `EnergyBudget` |
| Un-auditable decisions | parent hash chain |
| “Ignore that sensor” | `without(lattice, ids)` |

TitanFuse (Unsloth / Liger / TorchTitan router) remains in-tree as a *training* sidecar. Veridian is the **memory substrate** those trainers do not have.

## Install from a fresh clone

Requires Python 3.11+. No GPU, database, or cloud account.

```bash
git clone https://github.com/nyadaryt5/Codes.git
cd Codes
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.lock
pip install -e ".[dev]"
```

## Test

The suite must be green on that venv:

```bash
pytest -q --cov=veridian --cov=titanfuse --cov-report=term-missing --cov-fail-under=60
```

Or `make ci` (ruff + mypy + pytest). The same jobs are defined in [docs/ci.yml](docs/ci.yml) (copy to `.github/workflows/ci.yml` if the GitHub App has `workflows` permission).

```bash
python examples/reactor_worldline.py
```

## One-command app

```bash
docker compose up --build
```

- Veridian console: `http://localhost:8787/`
- TitanFuse planner: `http://localhost:8765/`

## CLI

```bash
veridian init lattice.json
veridian claim lattice.json --subject reactor.core --predicate temperature_c --object loop-a --value 312.4
veridian query lattice.json --subject reactor.core
veridian entropy lattice.json
veridian prove lattice.json --id <obs_id>
veridian certify lattice.json --subject reactor.core --predicate temperature_c --object loop-a
veridian kalman lattice.json --subject reactor.core --predicate temperature_c --object loop-a
veridian serve --host 0.0.0.0 --port 8787
```

## Library

```python
from veridian.factory import claim
from veridian.lattice import Lattice
from veridian.observation import Triple

lat = Lattice()
claim(lat, subject="dock.3", predicate="occupied", obj="berth", value=True, agent_id="lidar")
print(lat.belief(Triple("dock.3", "occupied", "berth")))
print(lat.entropy())
```

## Docs

- [docs/VERIDIAN.md](docs/VERIDIAN.md) — algebra and threat model
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — TitanFuse router (optional)
- [SECURITY.md](SECURITY.md) — no tokens, localhost by default
- [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT. Original work. Upstream LLM trainers keep their own licenses.
