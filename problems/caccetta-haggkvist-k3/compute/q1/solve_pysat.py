#!/usr/bin/env python3
"""Second solver: pysat Cadical195 / Glucose42, no DRAT.

Used to hunt SAT models on leftover cubes. A SAT assignment is checked
by verify_model.check. UNKNOWN/timeout is residue.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from encode import encode
from verify_model import check, var_id


def solve_pysat(n, d, indeg0, engine, secs):
    clauses, nvars = encode(n, d, exact=True, sb=True, indeg0=indeg0)
    if engine == "cadical":
        from pysat.solvers import Cadical195 as S
    elif engine == "glucose":
        from pysat.solvers import Glucose42 as S
    else:
        raise SystemExit(engine)
    slv = S(bootstrap_with=clauses, use_timer=True)
    slv.conf_budget(10**9)
    t0 = time.time()
    # pysat has no wall-clock timeout on all engines; interrupt via budget + poll
    sat = slv.solve()
    dt = time.time() - t0
    if dt > secs and sat is None:
        status = "UNKNOWN"
        model = None
    elif sat is False:
        status = "UNSAT"
        model = None
    elif sat is True:
        status = "SAT"
        m = slv.get_model()
        pos = {lit for lit in m if lit > 0}
        info = check(n, d, pos)
        model = info
    else:
        status = "UNKNOWN"
        model = None
    slv.delete()
    rec = {
        "n": n,
        "d": d,
        "indeg0": indeg0,
        "engine": engine,
        "nvars": nvars,
        "nclauses": len(clauses),
        "status": status,
        "time_s": round(dt, 3),
        "timeout_s": secs,
    }
    if model:
        rec["verified_model"] = bool(model["ok"])
        rec["min_out"] = model["min_out"]
        rec["outdeg"] = model["outdeg"]
        rec["indeg"] = model["indeg"]
        rec["two_cycles"] = model["two_cycles"]
        rec["triangles"] = model["triangles"]
        rec["arcs"] = model["arcs"]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--d", type=int, default=6)
    ap.add_argument("--indeg0", type=int, required=True)
    ap.add_argument("--engine", default="cadical", choices=("cadical", "glucose"))
    ap.add_argument("--time", type=int, default=120)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()
    rec = solve_pysat(args.n, args.d, args.indeg0, args.engine, args.time)
    print(json.dumps({k: v for k, v in rec.items() if k != "arcs"}, indent=2))
    if args.json_out:
        args.json_out.write_text(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
