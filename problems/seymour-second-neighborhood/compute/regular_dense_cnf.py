#!/usr/bin/env python3
"""CNF + Cadical proof for: no Eulerian Seymour-counterexample at n=2δ+3.

Independent of the OR-Tools model.  Uses PySAT cardinality encodings and
Cadical.  On UNSAT, writes a DRAT-style proof if the solver supports it,
plus the DIMACS instance so a third checker can replay.

Claim encoded:
    oriented graph, d^+(v)=d^-(v)=δ for every v, |N2^+(v)| ≤ δ-1 for every v.
UNSAT ⇒ every Eulerian oriented graph on n=2δ+3 vertices has a Seymour vertex.
"""

from __future__ import annotations

import argparse
import json
import time
from itertools import combinations
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Cadical195, Glucose42


def build_cnf(delta: int, n2_bound: int | None = None) -> tuple[CNF, dict]:
    n = 2 * delta + 3
    if n2_bound is None:
        n2_bound = delta - 1
    cnf = CNF()
    pairs = list(combinations(range(n), 2))
    # variables: fwd[i,j], bwd[i,j], miss[i,j]  (i<j)
    # then sec[v,w], wit[v,u,w]
    vmap = {}
    nextv = 1

    def new():
        nonlocal nextv
        x = nextv
        nextv += 1
        return x

    fwd, bwd, miss = {}, {}, {}
    for i, j in pairs:
        f, b, m = new(), new(), new()
        fwd[i, j], bwd[i, j], miss[i, j] = f, b, m
        # exactly one
        cnf.append([f, b, m])
        cnf.append([-f, -b])
        cnf.append([-f, -m])
        cnf.append([-b, -m])

    def arc(u, v):
        return fwd[u, v] if u < v else bwd[v, u]

    def bump(formula):
        nonlocal nextv
        cnf.extend(formula.clauses)
        used = formula.nv
        if used >= nextv:
            nextv = used + 1

    for v in range(n):
        outs = [arc(v, w) for w in range(n) if w != v]
        ins = [arc(w, v) for w in range(n) if w != v]
        enc_o = CardEnc.equals(
            lits=outs, bound=delta, top_id=nextv - 1, encoding=EncType.kmtotalizer
        )
        bump(enc_o)
        enc_i = CardEnc.equals(
            lits=ins, bound=delta, top_id=nextv - 1, encoding=EncType.kmtotalizer
        )
        bump(enc_i)

    # second neighbourhood
    for v in range(n):
        secs = []
        for w in range(n):
            if w == v:
                continue
            s = new()
            secs.append(s)
            # s -> not arc(v,w)
            cnf.append([-s, -arc(v, w)])
            wits = []
            for u in range(n):
                if u == v or u == w:
                    continue
                b = new()
                wits.append(b)
                # b <-> arc(v,u) & arc(u,w)
                cnf.append([-b, arc(v, u)])
                cnf.append([-b, arc(u, w)])
                cnf.append([b, -arc(v, u), -arc(u, w)])
                # wit => s  (provided not first; already s -> not first,
                # and if first then wit is still possible... if v->w, then
                # w not in N2.  Force: wit & not arc(v,w) => s)
                cnf.append([-b, arc(v, w), s])
            # s => some wit
            cnf.append([-s] + wits)
        if n2_bound < n - 1:
            enc = CardEnc.atmost(
                lits=secs, bound=n2_bound, top_id=nextv - 1, encoding=EncType.kmtotalizer
            )
            bump(enc)

    meta = {
        "delta": delta,
        "n": n,
        "n2_bound": n2_bound,
        "n_vars": nextv - 1,
        "n_clauses": len(cnf.clauses),
        "pairs": len(pairs),
    }
    return cnf, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=int, required=True)
    ap.add_argument("--n2-bound", type=int, default=None,
                    help="upper bound on |N2|; default delta-1 (counterexample). "
                         "Use delta to allow tight graphs; omit N2 with -1.")
    ap.add_argument("--out-dir", type=str, default=None)
    ap.add_argument("--time", type=int, default=300)
    args = ap.parse_args()
    out_dir = Path(args.out_dir or Path(__file__).resolve().parent / "certs")
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    n2b = args.n2_bound
    if n2b is not None and n2b < 0:
        n2b = 10 ** 9
    cnf, meta = build_cnf(args.delta, n2_bound=n2b)
    tag = f"eulerian_n{meta['n']}_d{args.delta}_n2le{meta['n2_bound']}"
    dimacs = out_dir / f"{tag}.cnf"
    cnf.to_file(str(dimacs))
    proof = out_dir / f"{tag}.drat"
    t1 = time.time()

    status = None
    proof_lines = None
    solver = Cadical195(bootstrap_with=cnf.clauses, use_timer=True, with_proof=True)
    sat = solver.solve()
    status = "SAT" if sat else "UNSAT"
    stats = {"cadical_time": solver.time() if hasattr(solver, "time") else None}
    if not sat:
        try:
            proof_lines = solver.get_proof()
        except Exception as exc:
            stats["proof_error"] = str(exc)
    solver.delete()
    # Independent second solver
    g = Glucose42(bootstrap_with=cnf.clauses, use_timer=True)
    gsat = g.solve()
    stats["glucose_status"] = "SAT" if gsat else "UNSAT"
    stats["glucose_time"] = g.time() if hasattr(g, "time") else None
    if (gsat is True) != (sat is True):
        stats["solver_disagreement"] = True
    g.delete()
    if proof_lines is not None:
        proof.write_text("\n".join(proof_lines) + "\n")
        rec_proof_len = len(proof_lines)
    else:
        rec_proof_len = None

    rec = {
        **meta,
        "status": status,
        "build_time": t1 - t0,
        "solve_time": time.time() - t1,
        "dimacs": str(dimacs),
        "proof": str(proof) if rec_proof_len else None,
        "proof_lines": rec_proof_len,
        "stats": stats,
        "claim": (
            "UNSAT means every Eulerian oriented graph on n=2δ+3 vertices "
            "has a Seymour vertex"
        ),
    }
    recp = out_dir / f"{tag}_pysat.json"
    recp.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
