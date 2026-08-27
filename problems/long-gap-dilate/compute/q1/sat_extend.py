#!/usr/bin/env python3
"""Exact G(p, round √p) past the stored p=71 table.

Uses Glucose4 (same encoding as compute/sat_exact.py). A row is exact only
when the binary search finishes: one SAT witness at T* and UNSAT at T*-1.
A timeout is residue, not a lower bound.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import signal
import time

import pathutil
from gaplib import max_gap_dilates, primes_upto, shakan_lower
from sat_exact import hits_all_T_cnf

try:
    from pysat.solvers import Glucose4, Glucose42
except ImportError:
    print("need compute/.venv with python-sat", file=__import__("sys").stderr)
    raise

try:
    from pysat.solvers import Cadical195
except ImportError:
    Cadical195 = None


def _solver_ctor(name: str):
    table = {
        "glucose4": Glucose4,
        "glucose42": Glucose42,
    }
    if Cadical195 is not None:
        table["cadical"] = Cadical195
    if name not in table:
        raise ValueError(name)
    return table[name]


def _solve_child(q, p, n, T, solver):
    cnf = hits_all_T_cnf(p, n, T)
    ctor = _solver_ctor(solver)
    try:
        slv = ctor(bootstrap_with=cnf, use_timer=True)
    except TypeError:
        slv = ctor(bootstrap_with=cnf)
    try:
        ok = slv.solve()
        if not ok:
            q.put((False, None))
            return
        pos = {x for x in slv.get_model() if x > 0}
        A = [i for i in range(p) if (i + 1) in pos]
        q.put((True, A))
    finally:
        slv.delete()


def exists_hitting(p: int, n: int, T: int, timeout: float | None, solver: str):
    if timeout is None or timeout <= 0:
        q = mp.Queue()
        _solve_child(q, p, n, T, solver)
        ok, A = q.get()
        return ok, A, False
    q = mp.Queue()
    proc = mp.Process(target=_solve_child, args=(q, p, n, T, solver))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.terminate()
        proc.join(2)
        if proc.is_alive():
            os.kill(proc.pid, signal.SIGKILL)
            proc.join(1)
        return None, None, True
    if q.empty():
        return None, None, True
    ok, A = q.get()
    return ok, A, False


def exact_G_timeout(
    p: int,
    n: int,
    timeout: float,
    solver: str,
    t_lo: int | None = None,
    t_hi: int | None = None,
) -> dict:
    t0 = time.time()
    sh = shakan_lower(p, n)
    sh_ceil = math.ceil(sh - 1e-12)
    if t_lo is None:
        t_lo = max(1, sh_ceil)
    if t_hi is None:
        t_hi = p - n
    L, R = t_lo, t_hi + 1
    best_A = None
    sat_T = None
    log = []
    unknown = False
    while L < R:
        mid = (L + R) // 2
        t1 = time.time()
        ok, A, to = exists_hitting(p, n, mid, timeout, solver)
        dt = time.time() - t1
        log.append({"T": mid, "sat": ok, "timeout": to, "sec": round(dt, 4)})
        if to:
            unknown = True
            break
        if ok:
            sat_T = mid
            best_A = A
            R = mid
        else:
            L = mid + 1
    G = None if sat_T is None else sat_T - 1
    witness_g = witness_d = None
    if best_A is not None:
        witness_g, witness_d = max_gap_dilates(best_A, p)
    exact = (not unknown) and sat_T is not None and any(
        (e["T"] == sat_T - 1 and e["sat"] is False) for e in log
    )
    # binary search ending at sat_T with L==R also implies UNSAT below when
    # the last unsat raise of L reached sat_T
    if not exact and not unknown and sat_T is not None:
        # certify the floor by one extra UNSAT call if the log missed it
        need = sat_T - 1
        if need >= 1 and not any(e["T"] == need for e in log):
            t1 = time.time()
            ok, _, to = exists_hitting(p, n, need, timeout, solver)
            log.append({"T": need, "sat": ok, "timeout": to, "sec": round(time.time() - t1, 4)})
            if to:
                unknown = True
            elif ok is False:
                exact = True
        elif any(e["T"] == need and e["sat"] is False for e in log):
            exact = True
    return {
        "p": p,
        "n": n,
        "G": G if exact else None,
        "G_upper": None if best_A is None else witness_g,
        "shakan": sh,
        "shakan_ceil": sh_ceil,
        "ratio_over_mean": None if not exact or G is None else G / (p / n),
        "ratio_over_sqrt": None if not exact or G is None else G / (p**0.5),
        "sat_T": sat_T,
        "witness": best_A,
        "witness_g": witness_g,
        "witness_d": witness_d,
        "exact": exact,
        "unknown": unknown,
        "log": log,
        "solver": solver,
        "timeout": timeout,
        "sec": round(time.time() - t0, 4),
    }


def walk_down(p: int, n: int, timeout: float, solver: str, t_hi: int | None = None) -> dict:
    """SAT is cheap near the local-search upper bound; walk T down until UNSAT or timeout."""
    t0 = time.time()
    sh = shakan_lower(p, n)
    sh_ceil = math.ceil(sh - 1e-12)
    T = p - n if t_hi is None else t_hi
    log = []
    best_A = None
    sat_T = None
    unknown = False
    unsat_T = None
    while T >= sh_ceil:
        t1 = time.time()
        ok, A, to = exists_hitting(p, n, T, timeout, solver)
        dt = time.time() - t1
        entry = {"T": T, "sat": ok, "timeout": to, "sec": round(dt, 4)}
        if A is not None:
            g, d = max_gap_dilates(A, p)
            entry["witness_g"] = g
            entry["witness_d"] = d
            entry["nA"] = len(A)
            best_A = A
            sat_T = T
        log.append(entry)
        print(entry, flush=True)
        if to:
            unknown = True
            break
        if ok is False:
            unsat_T = T
            break
        T -= 1
    exact = (unsat_T is not None) and (sat_T == unsat_T + 1)
    G = sat_T - 1 if sat_T is not None else None
    witness_g = witness_d = None
    if best_A is not None:
        witness_g, witness_d = max_gap_dilates(best_A, p)
    return {
        "p": p,
        "n": n,
        "G": G if exact else None,
        "G_upper": witness_g,
        "shakan": sh,
        "shakan_ceil": sh_ceil,
        "ratio_over_mean": None if not exact or G is None else G / (p / n),
        "ratio_over_sqrt": None if not exact or G is None else G / (p**0.5),
        "sat_T": sat_T,
        "unsat_T": unsat_T,
        "witness": best_A,
        "witness_g": witness_g,
        "witness_d": witness_d,
        "exact": exact,
        "unknown": unknown,
        "log": log,
        "solver": solver,
        "timeout": timeout,
        "sec": round(time.time() - t0, 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmin", type=int, default=73)
    ap.add_argument("--pmax", type=int, default=83)
    ap.add_argument("--timeout", type=float, default=180.0)
    ap.add_argument("--solver", type=str, default="glucose4")
    ap.add_argument("--walk", action="store_true", help="walk T down from p-n")
    ap.add_argument("--thi", type=int, default=None)
    ap.add_argument("--out", type=str, default=str(pathutil.CERTS / "sat_extend.jsonl"))
    args = ap.parse_args()
    with open(args.out, "a") as f:
        for p in primes_upto(args.pmax):
            if p < args.pmin:
                continue
            n = max(2, int(round(p**0.5)))
            if args.walk:
                rec = walk_down(p, n, timeout=args.timeout, solver=args.solver, t_hi=args.thi)
            else:
                rec = exact_G_timeout(p, n, timeout=args.timeout, solver=args.solver)
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(
                f"p={p} n={n} exact={rec['exact']} G={rec['G']} "
                f"G_upper={rec['G_upper']} unknown={rec['unknown']} sec={rec['sec']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
