#!/usr/bin/env python3
"""SAT the Cayley graphs C dumped as unknown (exists8 node cap).

Each line of q2/coset_unknown.conn is a 343-bit connection set of 0.
Ask Cadical whether the Cayley graph on F7^3 has an independent set
of size 8. A yes would be 392 vertices.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

QN = 343


def add_cid(i: int, d: int) -> int:
    i0, i1, i2 = i // 49, (i // 7) % 7, i % 7
    d0, d1, d2 = d // 49, (d // 7) % 7, d % 7
    return ((i0 + d0) % 7) * 49 + ((i1 + d1) % 7) * 7 + (i2 + d2) % 7


def has8(conn: str) -> bool:
    """Cayley: force 0 into the set and look for 7 more non-neighbours."""
    # closed neighbourhood of 0
    n0 = {0}
    for d in range(QN):
        if conn[d] == "1":
            n0.add(d)
    cand = [i for i in range(QN) if i not in n0]
    if len(cand) < 7:
        return False
    # map cand -> SAT vars 1..m
    idx = {v: i + 1 for i, v in enumerate(cand)}
    clauses = []
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
    path = HERE / "coset_unknown.conn"
    if not path.exists():
        print("no unknown file")
        (HERE / "coset_unknown_sat_log.txt").write_text("no unknown file\n")
        return
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    t0 = time.time()
    n_yes = 0
    n_no = 0
    workers = min(4, max(1, len(lines)))
    if len(lines) >= 8:
        from concurrent.futures import ProcessPoolExecutor, as_completed

        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(has8, conn): i for i, conn in enumerate(lines, 1)}
            done = 0
            for fut in as_completed(futs):
                i = futs[fut]
                if len(lines[i - 1]) != QN:
                    raise SystemExit(f"bad line {i} len={len(lines[i - 1])}")
                if fut.result():
                    n_yes += 1
                    print(f"YES line {i}", flush=True)
                else:
                    n_no += 1
                done += 1
                if done % 50 == 0 or done == len(lines):
                    print(
                        f"  {done}/{len(lines)} yes={n_yes} no={n_no} "
                        f"t={time.time()-t0:.1f}s",
                        flush=True,
                    )
    else:
        for i, conn in enumerate(lines, 1):
            if len(conn) != QN:
                raise SystemExit(f"bad line {i} len={len(conn)}")
            if has8(conn):
                n_yes += 1
                print(f"YES line {i}", flush=True)
            else:
                n_no += 1
    text = (
        f"unknown {len(lines)} sat8 {n_yes} unsat {n_no} "
        f"seconds {time.time()-t0:.1f}\n"
    )
    print(text, end="")
    (HERE / "coset_unknown_sat_log.txt").write_text(text)


if __name__ == "__main__":
    main()
