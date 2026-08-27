#!/usr/bin/env python3
"""Write leftover SAT DIMACS files.

  python3 write_cnf.py five-star --name k32_n2_1
  python3 write_cnf.py five-star --stars 0,1,2,3,4
  python3 write_cnf.py global --k 19 --min-star-cover 5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cnfutil import (  # noqa: E402
    global_leftover_cnf,
    leftover_tight_cnf,
    load_graph,
    pool_for_stars,
    star_type,
    write_dimacs,
)
from orbits import Q6_CUTOFF, REPS  # noqa: E402


def write_five(G, comb, name: str):
    U, local, local_g, local_miss = pool_for_stars(G, comb)
    cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
    path = HERE / "certs" / f"five_{name}.cnf"
    meta = write_dimacs(cnf, path)
    rec = {
        "kind": "five-star leftover-tight",
        "name": name,
        "stars": list(comb),
        "type": list(star_type(comb)),
        "k": U.bit_count(),
        "n_extras": nL,
        "n_roots": nY,
        **meta,
    }
    (HERE / "certs" / f"five_{name}.cnf.json").write_text(
        json.dumps(rec, indent=2) + "\n"
    )
    print(json.dumps(rec, indent=2))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("five-star", "global", "all-certs"))
    ap.add_argument("--name", default="")
    ap.add_argument("--stars", default="")
    ap.add_argument("--k", type=int, default=19)
    ap.add_argument("--min-star-cover", type=int, default=5)
    args = ap.parse_args()
    G = load_graph()

    if args.kind == "five-star":
        if args.stars:
            comb = tuple(int(x) for x in args.stars.split(","))
            name = args.name or "s" + "".join(str(x) for x in comb)
        elif args.name in REPS:
            comb = REPS[args.name]
            name = args.name
        else:
            raise SystemExit("need --name from orbits.REPS or --stars")
        write_five(G, comb, name)
        return 0

    if args.kind == "global":
        inst = global_leftover_cnf(G, k=args.k, min_star_cover=args.min_star_cover)
        path = HERE / "certs" / f"n1_k{args.k}_star{args.min_star_cover}.cnf"
        meta = write_dimacs(inst["cnf"], path)
        rec = {
            "kind": "global leftover",
            "k": args.k,
            "n1": 40 - args.k,
            "need_extras": args.k + 1,
            "min_star_cover": args.min_star_cover,
            **meta,
        }
        (HERE / "certs" / f"n1_k{args.k}_star{args.min_star_cover}.cnf.json").write_text(
            json.dumps(rec, indent=2) + "\n"
        )
        print(json.dumps(rec, indent=2))
        return 0

    # all-certs: three orbit reps + the four q6 cutoff pools + global
    jobs = []
    for name, comb in REPS.items():
        jobs.append(write_five(G, comb, name))
    for comb in Q6_CUTOFF:
        name = "q6_" + "".join(str(x) for x in comb)
        if tuple(comb) in REPS.values():
            continue
        jobs.append(write_five(G, comb, name))
    inst = global_leftover_cnf(G, k=19, min_star_cover=5)
    path = HERE / "certs" / "n1_k19_star5.cnf"
    meta = write_dimacs(inst["cnf"], path)
    jobs.append({
        "kind": "global leftover",
        "k": 19,
        "min_star_cover": 5,
        **meta,
    })
    (HERE / "certs" / "n1_k19_star5.cnf.json").write_text(
        json.dumps(jobs[-1], indent=2) + "\n"
    )
    print("wrote", len(jobs), "CNFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
