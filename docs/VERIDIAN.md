# Veridian

Machines do not have a *present*. They have a bag of tensors and a clock they do not trust.

Veridian is a **causal worldline lattice**: every claim is an observation with parents, a sensor, a generation depth, a half-life, and a content-addressed id. Belief is not the last write. Belief is **decayed, merged, and forkable**.

## Problems

| Failure | What Veridian does |
| --- | --- |
| RAG cites a page that was true last March | Half-life decay; `as_of_ns` queries |
| Agents overwrite each other | Log-odds merge; conflicts are first-class, never averaged |
| Models train on model output (collapse) | `gen_depth` + `GenerationGuard` |
| Infinite tool loops | `EnergyBudget` charges append/query |
| “What if that sensor lied?” | `without(lattice, ids)` drops a node **and its descendants** |
| Un-auditable copilots | Append-only hash chain of parents |

This is not a blockchain, not a vector database, and not a knowledge graph. It is a **physics of memory** for software that must survive disagreement.

## v0.3 runtime

Beyond the lattice core:

| Module | Role |
| --- | --- |
| `hlc` | Hybrid logical clocks so peers never go backwards |
| `merkle` | Incremental Merkle log + inclusion proofs |
| `certificate` | Compact audit: belief + Merkle path + digest |
| `kalman` | Scalar filter on numeric worldlines |
| `conformal` | Split-conformal prediction intervals |
| `temporal` | LTL-lite: always / eventually / until / next |
| `cone` | Causal past/future; incomparability |
| `federation` | Gossip ingest in causal order |
| `quorum` | Stake-weighted majority; equivocation ban |
| `datalog` | Horn-clause materialization |
| `privacy` | Laplace mechanism on numeric export |
| `geo` | Geohash spatial index |
| `watermark` | Fragile synthetic-value marks |

## Algebra (sketch)

- Observation ids are SHA-256 of canonical payload + parents.
- Confidence at time `t`: `c0 * 2^(-(t-t0)/half_life)`.
- Compatible values pool in logit space; incompatible values **fork** (`conflict=true`).
- Synthetic child depth = `1 + max(parent depths)`.

## CLI

```bash
veridian init lattice.json
veridian claim lattice.json --subject reactor.core --predicate temperature_c --object loop-a --value 312.4
veridian query lattice.json --subject reactor.core
veridian entropy lattice.json
veridian what-if lattice.json --drop <obs_id>
veridian serve --host 0.0.0.0 --port 8787
```
