#!/usr/bin/env python3
"""Write q8 leftover DIMACS: type-(0,5) leftover-tight and stronger global.

  python3 write_cnf.py k30
  python3 write_cnf.py global
  python3 write_cnf.py all-certs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

from cnfutil import (  # noqa: E402
    global_leftover_cnf,
    leftover_tight_cnf,
    load_graph,
    pool_for_stars,
    star_type,
    write_dimacs,
)
from orbits import REPS  # noqa: E402

K30 = REPS["k30_n0_5"]
EMPTY_FIVE = ((2, 1), (1, 3))


def write_k30(G):
    U, local, local_g, local_miss = pool_for_stars(G, K30)
    cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
    path = HERE / "certs" / "five_k30_n0_5.cnf"
    meta = write_dimacs(cnf, path)
    rec = {
        "kind": "five-star leftover-tight",
        "name": "k30_n0_5",
        "stars": list(K30),
        "type": list(star_type(K30)),
        "k": U.bit_count(),
        "n_extras": nL,
        "n_roots": nY,
        **meta,
    }
    (HERE / "certs" / "five_k30_n0_5.cnf.json").write_text(
        json.dumps(rec, indent=2) + "\n"
    )
    print(json.dumps(rec, indent=2))
    return rec


def write_global(G):
    inst = global_leftover_cnf(
        G, k=19, min_star_cover=5, forbid_five_types=EMPTY_FIVE,
    )
    path = HERE / "certs" / "n1_k19_star5_no21_no13.cnf"
    meta = write_dimacs(inst["cnf"], path)
    rec = {
        "kind": "global leftover",
        "k": 19,
        "n1": 21,
        "need_extras": 20,
        "min_star_cover": 5,
        "forbid_five_types": inst["forbid_five_types"],
        "n_five_forbids": inst["n_five_forbids"],
        **meta,
    }
    (HERE / "certs" / "n1_k19_star5_no21_no13.cnf.json").write_text(
        json.dumps(rec, indent=2) + "\n"
    )
    print(json.dumps(rec, indent=2))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("k30", "global", "all-certs"))
    args = ap.parse_args()
    G = load_graph()
    if args.kind == "k30":
        write_k30(G)
        return 0
    if args.kind == "global":
        write_global(G)
        return 0
    write_k30(G)
    write_global(G)
    print("wrote 2 CNFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
