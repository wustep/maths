#!/usr/bin/env python3
"""Global leftover SAT: n1 <= 21 and star-cover at least 4.

Thin wrapper around q5/n1_leftover_sat.py.  Writes JSON here.
UNSAT without a stored DRAT is residue, not an emptiness proof.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q5 = HERE.parent / "q5"
sys.path.insert(0, str(Q5))
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))

from n1_leftover_sat import build_instance, decode_model, write_code41  # noqa: E402


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=19)
    ap.add_argument("--kmax", type=int, default=None)
    ap.add_argument("--solver", default="cadical195",
                    choices=("cadical195", "kissat404", "glucose4"))
    ap.add_argument("--write-cnf", action="store_true")
    ap.add_argument("--min-star-cover", type=int, default=4,
                    help="4 forbids 3-star U; 5 forbids 4-star U")
    args = ap.parse_args()
    kmax = args.kmax if args.kmax is not None else args.k
    min_cover = args.min_star_cover
    (HERE / "certs").mkdir(exist_ok=True)

    slices = []
    found = False
    for k in range(args.k, kmax + 1):
        print(f"==== k={k} n1={40 - k} |E|>={k + 1} "
              f"star-cover>={min_cover} ====",
              flush=True)
        inst = build_instance(k, min_star_cover=min(4, min_cover))
        cnf = inst["cnf"]
        if min_cover >= 5:
            from itertools import combinations
            from n1_leftover_sat import stars_of
            stars = stars_of(inst["D"])
            nE, nD = inst["nE"], inst["nD"]

            def vy(r):
                return nE + r + 1

            for comb in combinations(range(10), min_cover - 1):
                W = 0
                for s in comb:
                    W |= stars[s]
                outside = [vy(r) for r in range(nD) if ((W >> r) & 1) == 0]
                if outside:
                    cnf.append(outside)
        print(f"  vars={cnf.nv} clauses={len(cnf.clauses)}", flush=True)
        if args.write_cnf:
            cnf.to_file(str(HERE / "certs" / f"n1_k{k}_star{min_cover}.cnf"))

        if args.solver == "cadical195":
            from pysat.solvers import Cadical195
            slv = Cadical195(bootstrap_with=cnf, with_proof=True)
        elif args.solver == "kissat404":
            from pysat.solvers import Kissat404
            slv = Kissat404(bootstrap_with=cnf)
        else:
            from pysat.solvers import Glucose4
            slv = Glucose4(bootstrap_with=cnf)

        sat = slv.solve()
        model = slv.get_model() if sat else None
        proof = None
        if (not sat) and args.solver == "cadical195":
            proof = slv.get_proof()
        slv.delete()
        rec = {
            "k": k,
            "n1": 40 - k,
            "need_extras": k + 1,
            "min_star_cover": min_cover,
            "sat": bool(sat),
            "cnf_vars": cnf.nv,
            "cnf_clauses": len(cnf.clauses),
            "solver": args.solver,
            "proof_lines": len(proof) if proof else 0,
        }
        if sat and model:
            E, U = decode_model(inst, model)
            rec["n_extras"] = len(E)
            rec["n_U"] = len(U)
            write_code41(inst, E, U, HERE / "certs" / "code41.json")
            rec["wrote"] = "certs/code41.json"
            found = True
            slices.append(rec)
            print(f"  SAT extras={len(E)} U={len(U)}", flush=True)
            break
        if proof:
            drat = HERE / "certs" / f"n1_k{k}_star{min_cover}.drat"
            drat.write_text("\n".join(proof) + "\n")
            rec["drat"] = drat.name
        print(f"  sat={sat} proof_lines={rec['proof_lines']}", flush=True)
        slices.append(rec)

    report = {
        "solver": args.solver,
        "k_lo": args.k,
        "k_hi": kmax,
        "min_star_cover": min_cover,
        "found_41": found,
        "slices": slices,
        "comment": (
            f"Leftover n1<=21 with star-cover >= {min_cover}.  "
            "A model is a 41-set.  UNSAT without a stored DRAT is residue."
        ),
    }
    out = HERE / f"leftover_sat_k{args.k}.json"
    if args.kmax is not None:
        out = HERE / f"leftover_sat_k{args.k}_{kmax}.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    (HERE / "leftover_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out, "and leftover_sat.json found_41=", found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
