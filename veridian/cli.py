from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from veridian.counterfactual import without
from veridian.errors import VeridianError
from veridian.factory import claim
from veridian.lattice import Lattice
from veridian.logging_config import configure_logging
from veridian.observation import Triple
from veridian.query import Query, QueryEngine
from veridian.store import load, save

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="veridian", description="Causal worldline lattice")
    sub = p.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="Create an empty lattice file")
    init.add_argument("path", type=Path)

    add = sub.add_parser("claim", help="Append a claim")
    add.add_argument("path", type=Path)
    add.add_argument("--subject", required=True)
    add.add_argument("--predicate", required=True)
    add.add_argument("--object", required=True, dest="obj")
    add.add_argument("--value", required=True)
    add.add_argument("--agent", default="cli")
    add.add_argument("--sensor", default="human")
    add.add_argument("--confidence", type=float, default=0.8)
    add.add_argument("--depth", type=int, default=0)

    q = sub.add_parser("query", help="Query beliefs")
    q.add_argument("path", type=Path)
    q.add_argument("--subject")
    q.add_argument("--predicate")
    q.add_argument("--min-conf", type=float, default=0.0)

    ent = sub.add_parser("entropy", help="Synthetic-collapse risk")
    ent.add_argument("path", type=Path)

    bel = sub.add_parser("belief", help="Merged belief for one triple")
    bel.add_argument("path", type=Path)
    bel.add_argument("--subject", required=True)
    bel.add_argument("--predicate", required=True)
    bel.add_argument("--object", required=True, dest="obj")

    fork = sub.add_parser("what-if", help="Drop observation ids and reprint entropy")
    fork.add_argument("path", type=Path)
    fork.add_argument("--drop", nargs="+", required=True)

    pr = sub.add_parser("prove", help="Merkle inclusion proof for an observation id")
    pr.add_argument("path", type=Path)
    pr.add_argument("--id", required=True)

    cert = sub.add_parser("certify", help="Audit certificate for a triple")
    cert.add_argument("path", type=Path)
    cert.add_argument("--subject", required=True)
    cert.add_argument("--predicate", required=True)
    cert.add_argument("--object", required=True, dest="obj")

    kf = sub.add_parser("kalman", help="Kalman filter a numeric worldline")
    kf.add_argument("path", type=Path)
    kf.add_argument("--subject", required=True)
    kf.add_argument("--predicate", required=True)
    kf.add_argument("--object", required=True, dest="obj")

    serve = sub.add_parser("serve", help="Local lattice console")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8787)
    serve.add_argument("--path", type=Path, default=Path("lattice.json"))
    return p


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = build_parser().parse_args(argv)
    try:
        return _dispatch(args)
    except VeridianError as exc:
        logger.error("cli_error err=%s", exc)
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _open(path: Path) -> Lattice:
    if path.exists():
        return load(path)
    return Lattice()


def _dispatch(args: argparse.Namespace) -> int:
    if args.cmd == "init":
        save(Lattice(), args.path)
        print(args.path)
        return 0
    if args.cmd == "claim":
        lat = _open(args.path)
        obs = claim(
            lat,
            subject=args.subject,
            predicate=args.predicate,
            obj=args.obj,
            value=_coerce(args.value),
            agent_id=args.agent,
            sensor_id=args.sensor,
            confidence=args.confidence,
            gen_depth=args.depth,
        )
        save(lat, args.path)
        print(obs.obs_id)
        return 0
    if args.cmd == "query":
        lat = _open(args.path)
        rows = QueryEngine(lat).run(
            Query(subject=args.subject, predicate=args.predicate, min_confidence=args.min_conf)
        )
        json.dump(rows, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "entropy":
        lat = _open(args.path)
        json.dump(lat.entropy().to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "belief":
        lat = _open(args.path)
        b = lat.belief(Triple(args.subject, args.predicate, args.obj))
        json.dump(None if b is None else b.__dict__, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "what-if":
        lat = _open(args.path)
        fork = without(lat, set(args.drop))
        json.dump(fork.entropy().to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "prove":
        lat = _open(args.path)
        proof = lat.merkle.prove(args.id)
        json.dump(proof.to_dict() | {"ok": proof.verify()}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "certify":
        from veridian.certificate import issue

        lat = _open(args.path)
        cert = issue(lat, Triple(args.subject, args.predicate, args.obj))
        json.dump(None if cert is None else cert.to_dict(), sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "kalman":
        lat = _open(args.path)
        k = lat.kalman(Triple(args.subject, args.predicate, args.obj))
        json.dump(None if k is None else k.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "serve":
        from veridian.server import serve

        serve(args.host, args.port, args.path)
        return 0
    return 1


def _coerce(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


if __name__ == "__main__":
    raise SystemExit(main())
