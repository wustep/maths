#!/usr/bin/env python3
"""Split leftover-tight k=30 SAT into |U|=u cubes (q8 leftover_tight_cnf)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q8 = HERE.parent / "q8"
sys.path.insert(0, str(Q8))
sys.path.insert(0, str(HERE))

from cnfutil import leftover_tight_cnf, load_graph, pool_for_stars, write_dimacs  # noqa: E402
from orbits import REPS  # noqa: E402

K30 = REPS["k30_n0_5"]
CERTS = HERE / "certs"


def cube_cnf(G, u: int):
    """Same leftover-tight CNF plus CardEnc.equals on the 30 host-root bits."""
    from pysat.card import CardEnc, EncType

    U, local, local_g, local_miss = pool_for_stars(G, K30)
    cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
    if not 19 <= u <= nY:
        raise ValueError(f"u={u} out of range for nY={nY}")
    y = list(range(nL + 1, nL + nY + 1))
    extra = CardEnc.equals(
        lits=y, bound=u, top_id=cnf.nv, encoding=EncType.seqcounter,
    )
    cnf.extend(extra.clauses)
    return cnf, nL, nY, local


def write_cubes(us: list[int]) -> list[dict]:
    G = load_graph()
    CERTS.mkdir(exist_ok=True)
    rows = []
    for u in us:
        cnf, nL, nY, _ = cube_cnf(G, u)
        path = CERTS / f"five_k30_u{u}.cnf"
        meta = write_dimacs(cnf, path)
        rec = {
            "name": f"k30_u{u}",
            "u": u,
            "need_extras": u + 1,
            "n_extras": nL,
            "n_roots": nY,
            **meta,
        }
        (CERTS / f"five_k30_u{u}.cnf.json").write_text(
            json.dumps(rec, indent=2) + "\n"
        )
        rows.append(rec)
        print(json.dumps(rec, sort_keys=True), flush=True)
    out = {
        "n_cubes": len(rows),
        "cubes": rows,
        "comment": (
            "Type-(0,5) leftover-tight split by |U|=u. Same leftover_tight_cnf "
            "as q8. All cubes unsat with verified DRAT empties the "
            "representative. One SAT cube is a leftover 41-set."
        ),
    }
    (CERTS / "k30_cubes.json").write_text(json.dumps(out, indent=2) + "\n")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["write", "solve"])
    ap.add_argument("--u", type=int, default=19)
    ap.add_argument("--solver", default="kissat", choices=("kissat", "cadical"))
    ap.add_argument("--no-proof", action="store_true")
    args = ap.parse_args()
    CERTS.mkdir(exist_ok=True)
    if args.cmd == "write":
        write_cubes(list(range(19, 31)))
        return 0

    from native_sat import run_cadical, run_kissat  # noqa: E402

    cnf_path = CERTS / f"five_k30_u{args.u}.cnf"
    if not cnf_path.is_file():
        write_cubes([args.u])
    if args.solver == "kissat":
        rec = run_kissat(cnf_path, CERTS / f"five_k30_u{args.u}.kissat.log")
    else:
        proof = None if args.no_proof else CERTS / f"five_k30_u{args.u}.native.drat"
        rec = run_cadical(
            cnf_path, proof, CERTS / f"five_k30_u{args.u}.cadical.log",
        )
    out = {"u": args.u, "solver": args.solver, **rec}
    (CERTS / f"five_k30_u{args.u}.{args.solver}.sat.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print(json.dumps({k: out[k] for k in out if k != "stdout"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
