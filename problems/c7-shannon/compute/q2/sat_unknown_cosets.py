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
    edges = []
    for i in range(QN):
        for d in range(QN):
            if d == 0 or conn[d] != "1":
                continue
            j = add_cid(i, d)
            if i < j:
                edges.append((i, j))
    lits = list(range(1, QN + 1))
    clauses = [[-u - 1, -v - 1] for u, v in edges]
    cnf = CardEnc.atleast(lits=lits, bound=8, top_id=QN, encoding=EncType.kmtotalizer)
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
    for i, conn in enumerate(lines, 1):
        if len(conn) != QN:
            raise SystemExit(f"bad line {i} len={len(conn)}")
        if has8(conn):
            n_yes += 1
            print(f"YES line {i}", flush=True)
        else:
            n_no += 1
        if i % 50 == 0 or i == len(lines):
            print(f"  {i}/{len(lines)} yes={n_yes} no={n_no} t={time.time()-t0:.1f}s", flush=True)
    text = (
        f"unknown {len(lines)} sat8 {n_yes} unsat {n_no} "
        f"seconds {time.time()-t0:.1f}\n"
    )
    print(text, end="")
    (HERE / "coset_unknown_sat_log.txt").write_text(text)


if __name__ == "__main__":
    main()
