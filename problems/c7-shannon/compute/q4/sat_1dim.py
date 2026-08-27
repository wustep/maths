#!/usr/bin/env python3
"""Cadical: 53 independent cosets in each unique 1-dimensional quotient.

Reads q4/onedim_unique.conn (2401-bit connection strings). Fifty-three
cosets would be 371 vertices. Writes a set if SAT.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Cadical195

from c7_common import format_word

QN = 2401
TARGET = 53
ENC = EncType.kmtotalizer


def unpack4(i: int) -> tuple[int, int, int, int]:
    return i // 343, (i // 49) % 7, (i // 7) % 7, i % 7


def add4(a: int, b: int) -> int:
    a0, a1, a2, a3 = unpack4(a)
    b0, b1, b2, b3 = unpack4(b)
    return ((a0 + b0) % 7) * 343 + ((a1 + b1) % 7) * 49 + ((a2 + b2) % 7) * 7 + (
        a3 + b3
    ) % 7


def solve_conn(conn: str, idx: int) -> bool:
    clist = [d for d in range(1, QN) if conn[d] == "1"]
    cnf = CNF()
    # Cayley: translate so 0 is taken.
    for d in clist:
        cnf.append([-(d + 1)])
    top = QN
    lits = list(range(1, QN + 1))
    extra = CardEnc.atleast(lits=lits, bound=TARGET, top_id=top, encoding=ENC)
    cnf.extend(extra.clauses)
    top = extra.nv
    seen = set()
    for i in range(QN):
        for d in clist:
            j = add4(i, d)
            a, b = (i + 1, j + 1) if i < j else (j + 1, i + 1)
            if (a, b) in seen:
                continue
            seen.add((a, b))
            cnf.append([-a, -b])
    solver = Cadical195(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    print(f"unique={idx} deg={len(clist)} sat={sat} clauses={len(cnf.clauses)}", flush=True)
    if sat:
        model = set(solver.get_model())
        taken = [i for i in range(QN) if (i + 1) in model]
        (HERE / f"sat_1dim_{idx}.cids").write_text(" ".join(map(str, taken)) + "\n")
        print(f"SAT pack={len(taken)} wrote sat_1dim_{idx}.cids", flush=True)
        return True
    return False


def main() -> int:
    path = HERE / "onedim_unique.conn"
    if not path.exists():
        print("missing onedim_unique.conn; run search_1dim_cosets first")
        return 1
    max_graphs = 3
    if len(sys.argv) > 1:
        max_graphs = int(sys.argv[1])
    t0 = time.time()
    n_sat = 0
    n_unsat = 0
    for idx, line in enumerate(path.read_text().splitlines(), 1):
        conn = line.strip()
        if len(conn) != QN:
            continue
        if solve_conn(conn, idx):
            n_sat += 1
            break
        n_unsat += 1
        if idx >= max_graphs:
            break
    print(f"DONE sat_graphs={n_sat} unsat={n_unsat} t={time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
