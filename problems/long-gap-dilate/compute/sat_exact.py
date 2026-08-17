#!/usr/bin/env python3
"""Exact G(p,n) = min_{|A|=n} max_d g(dA) via SAT.

A has max_d g(dA) < T  iff  A hits every T-term AP.
We binary-search T. Symmetry: 0,1 in A.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from gaplib import gap, max_gap_dilates, shakan_lower, uniq_mod

try:
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF
    from pysat.solvers import Glucose4
except ImportError:
    print("need compute/.venv with python-sat", file=sys.stderr)
    raise


def hits_all_T_cnf(p: int, n: int, T: int, fix01: bool = True) -> CNF:
    """SAT: exists A, |A|=n, 0,1 in A (optional), every T-AP meets A."""
    # vars 1..p correspond to residues 0..p-1
    cnf = CNF()
    if T <= 0:
        # gap < 0 is impossible unless we allow empty misses of negative length
        cnf.append([])  # unsat
        return cnf
    if T == 1:
        # every singleton AP hits A ⇒ A = all of F_p, so n must be p
        if n != p:
            cnf.append([])
        else:
            for i in range(1, p + 1):
                cnf.append([i])
        return cnf

    lits = list(range(1, p + 1))
    # exactly n
    cnf.extend(CardEnc.equals(lits=lits, bound=n, encoding=EncType.seqcounter))

    if fix01 and n >= 2:
        cnf.append([1])  # 0 in A
        cnf.append([2])  # 1 in A

    # every T-term AP
    for d in range(1, p):
        for s in range(p):
            clause = []
            x = s
            for _ in range(T):
                clause.append(x + 1)
                x = (x + d) % p
            cnf.append(clause)
    return cnf


def exists_hitting(p: int, n: int, T: int, timeout: float | None = None) -> tuple[bool, list[int] | None]:
    cnf = hits_all_T_cnf(p, n, T)
    with Glucose4(bootstrap_with=cnf, use_timer=True) as slv:
        if timeout is not None:
            slv.solve() if False else None
        ok = slv.solve()
        if not ok:
            return False, None
        model = slv.get_model()
        A = [i for i in range(p) if (i + 1) in set(x for x in model if x > 0) and i + 1 <= p]
        # model may include auxiliary card vars; keep only 1..p
        pos = {x for x in model if x > 0}
        A = [i for i in range(p) if (i + 1) in pos]
        return True, A


def exact_G(p: int, n: int, t_lo: int | None = None, t_hi: int | None = None) -> dict:
    t0 = time.time()
    sh = shakan_lower(p, n)
    # G >= ceil(sh) if sh not integer? Shakan is a real lower bound; G is integer
    # so G >= ceil(2p/n - 2)
    import math

    sh_ceil = math.ceil(sh - 1e-12)
    if t_lo is None:
        t_lo = max(0, sh_ceil)
    if t_hi is None:
        # equally-spaced AP has some dilate that is an interval, gap p-n
        t_hi = p - n

    # G < T iff hitting-T is sat. We want the min T such that hitting-T is UNSAT?
    # max_d g < T iff hits all T-APs.
    # G = min max g = min { t : exists A with max g <= t } = min { t : exists A with max g < t+1 }
    # exists A with max g < T  iff  hitting T is sat.
    # so G = min { T-1 : hitting T sat } = (min sat T) - 1
    # Shakan: G >= sh, so hitting T is unsat for all T <= sh (i.e. T-1 < sh).

    lo, hi = t_lo, t_hi + 1  # search T in [lo, hi], G = T*-1 where T* min sat
    # We know hitting T=p is sat (A any n-set, every p-AP is the whole field).
    best_A = None
    sat_T = None
    log = []
    # binary search the minimal T such that hitting-T is SAT
    L, R = max(1, t_lo), p
    while L < R:
        mid = (L + R) // 2
        t1 = time.time()
        ok, A = exists_hitting(p, n, mid)
        dt = time.time() - t1
        log.append({"T": mid, "sat": ok, "sec": round(dt, 4), "nA": None if A is None else len(A)})
        if ok:
            sat_T = mid
            best_A = A
            R = mid
        else:
            L = mid + 1
    if sat_T is None:
        ok, A = exists_hitting(p, n, L)
        sat_T = L if ok else None
        best_A = A
    G = None if sat_T is None else sat_T - 1
    witness_g = None
    witness_d = None
    if best_A is not None:
        witness_g, witness_d = max_gap_dilates(best_A, p)
        # The SAT A realises max g <= sat_T-1. It may be strictly smaller.
        # To certify G we also need unsat at sat_T-1, which binary search gives
        # when L ends at sat_T.
    return {
        "p": p,
        "n": n,
        "G": G,
        "shakan": sh,
        "shakan_ceil": sh_ceil,
        "ratio_over_mean": None if G is None else G / (p / n),
        "ratio_over_sqrt": None if G is None else G / (p**0.5),
        "sat_T": sat_T,
        "witness": best_A,
        "witness_g": witness_g,
        "witness_d": witness_d,
        "log": log,
        "sec": round(time.time() - t0, 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    p = args.p
    n = args.n if args.n is not None else max(2, int(round(p**0.5)))
    rec = exact_G(p, n)
    if args.json:
        print(json.dumps(rec))
    else:
        print(
            f"p={p} n={n} G={rec['G']} shakan={rec['shakan']:.4f} "
            f"G/(p/n)={rec['ratio_over_mean']} sec={rec['sec']}"
        )
        print("log", rec["log"])
        if rec["witness"] is not None:
            print("witness", rec["witness"], "g", rec["witness_g"], "d", rec["witness_d"])


if __name__ == "__main__":
    main()
