#!/usr/bin/env python3
"""Decide leftover unique 8-coset Cayley graphs.

Each line of q3/coset_leftover.conn is a 343-bit connection set of 0
in F7^3. Replay the Hoffman bound independently, then ask Cadical
whether the Cayley graph has an independent set of size 8 (force 0,
look for 7 more). A yes would be 392 vertices.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
QN = 343
COS = [math.cos(2 * math.pi * k / 7) for k in range(7)]


def add_cid(i: int, d: int) -> int:
    i0, i1, i2 = i // 49, (i // 7) % 7, i % 7
    d0, d1, d2 = d // 49, (d // 7) % 7, d % 7
    return ((i0 + d0) % 7) * 49 + ((i1 + d1) % 7) * 7 + (i2 + d2) % 7


def hoffman(conn: str) -> tuple[int, float]:
    clist = [c for c in range(1, QN) if conn[c] == "1"]
    deg = len(clist)
    if deg == 0:
        return 0, float(QN)
    mu = float(deg)
    for a in range(1, QN):
        a0, a1, a2 = a // 49, (a // 7) % 7, a % 7
        sr = 0.0
        for c in clist:
            c0, c1, c2 = c // 49, (c // 7) % 7, c % 7
            sr += COS[(a0 * c0 + a1 * c1 + a2 * c2) % 7]
        if sr < mu:
            mu = sr
    if mu >= -1e-12:
        return deg, float(QN)
    return deg, 343.0 * (-mu) / (deg - mu)


def has8(conn: str) -> bool:
    n0 = {0}
    for d in range(QN):
        if conn[d] == "1":
            n0.add(d)
    cand = [i for i in range(QN) if i not in n0]
    if len(cand) < 7:
        return False
    idx = {v: i + 1 for i, v in enumerate(cand)}
    clauses: list[list[int]] = []
    for a_i, a in enumerate(cand):
        for b in cand[a_i + 1 :]:
            d0 = (b // 49 - a // 49) % 7
            d1 = ((b // 7) % 7 - (a // 7) % 7) % 7
            d2 = (b % 7 - a % 7) % 7
            d = d0 * 49 + d1 * 7 + d2
            if conn[d] == "1":
                clauses.append([-idx[a], -idx[b]])
    lits = list(idx.values())
    cnf = CardEnc.atleast(
        lits=lits, bound=7, top_id=len(cand), encoding=EncType.kmtotalizer
    )
    clauses.extend(cnf.clauses)
    return bool(Cadical195(bootstrap_with=clauses).solve())


def main() -> None:
    path = HERE / "coset_leftover.conn"
    log_path = HERE / "coset_sat_log.txt"
    if not path.exists():
        text = "no leftover file\n"
        print(text, end="")
        log_path.write_text(text)
        return
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    t0 = time.time()
    n_yes = 0
    n_no = 0
    n_hoff = 0
    lines_ok = []
    for i, conn in enumerate(lines, 1):
        if len(conn) != QN or any(ch not in "01" for ch in conn):
            raise SystemExit(f"bad line {i} len={len(conn)}")
        deg, hoff = hoffman(conn)
        if hoff < 7.9:
            n_no += 1
            n_hoff += 1
            continue
        lines_ok.append((i, conn, deg, hoff))
    print(
        f"leftover {len(lines)} hoffman_lt8 {n_hoff} sat_queue {len(lines_ok)}",
        flush=True,
    )
    if lines_ok:
        from concurrent.futures import ProcessPoolExecutor, as_completed

        workers = min(4, len(lines_ok))
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(has8, conn): (i, deg, hoff) for i, conn, deg, hoff in lines_ok}
            done = 0
            for fut in as_completed(futs):
                i, deg, hoff = futs[fut]
                if fut.result():
                    n_yes += 1
                    print(f"YES line {i} deg={deg} hoff={hoff:.4f}", flush=True)
                else:
                    n_no += 1
                done += 1
                if done % 10 == 0 or done == len(lines_ok):
                    print(
                        f"  sat {done}/{len(lines_ok)} yes={n_yes} no={n_no} "
                        f"t={time.time()-t0:.1f}s",
                        flush=True,
                    )
    text = (
        f"leftover {len(lines)} sat8 {n_yes} unsat {n_no} "
        f"hoffman_replay {n_hoff} seconds {time.time()-t0:.1f}\n"
    )
    print(text, end="")
    log_path.write_text(text)
    if n_yes:
        raise SystemExit("found an 8-coset pack; materialise it")


if __name__ == "__main__":
    main()
