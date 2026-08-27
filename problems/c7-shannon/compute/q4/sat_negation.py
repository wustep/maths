#!/usr/bin/env python3
"""Cadical: 184 negation-pairs {v,-v} (size 368).

Translation can put 0 in a set, but a negation-symmetric 368-set cannot
contain 0. Each var is a pair of distinct nonzero antipodes.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from c7_common import NVERTS, adjacent, closed_neighbors, decode, encode, format_word

ENC = EncType.kmtotalizer
TARGET = 184


def neg(v: int) -> int:
    return encode((-c) % 7 for c in decode(v))


def main() -> int:
    t0 = time.time()
    pair_of = [-1] * NVERTS
    pairs = []
    for v in range(1, NVERTS):
        w = neg(v)
        if w == v:
            continue
        a, b = (v, w) if v < w else (w, v)
        if pair_of[a] >= 0:
            continue
        if adjacent(a, b):
            continue
        pair_of[a] = pair_of[b] = len(pairs)
        pairs.append((a, b))
    print(f"good_pairs={len(pairs)}", flush=True)
    lits = list(range(1, len(pairs) + 1))
    clauses = []
    # Two pairs conflict if some cross-edge exists.
    for i, (a, b) in enumerate(pairs):
        blocked = set(closed_neighbors(a)) | set(closed_neighbors(b))
        for u in blocked:
            if u == a or u == b:
                continue
            j = pair_of[u]
            if j < 0 or j <= i:
                continue
            clauses.append([-(i + 1), -(j + 1)])
    extra = CardEnc.atleast(lits=lits, bound=TARGET, top_id=len(pairs), encoding=ENC)
    clauses.extend(extra.clauses)
    print(f"clauses={len(clauses)} vars={extra.nv} t={time.time() - t0:.1f}s", flush=True)
    solver = Cadical195(bootstrap_with=clauses)
    sat = solver.solve()
    print(f"sat={sat} t={time.time() - t0:.1f}s", flush=True)
    lines = [f"good_pairs {len(pairs)}", f"clauses {len(clauses)}", f"sat {sat}"]
    if sat:
        model = set(solver.get_model())
        words = []
        for i, (a, b) in enumerate(pairs):
            if (i + 1) in model:
                words.extend((a, b))
        words = sorted(set(words))
        out = HERE / f"R{len(words)}_negation.txt"
        out.write_text("\n".join(format_word(v) for v in words) + "\n")
        lines.append(f"wrote {out} size {len(words)}")
        print(f"wrote {out} size={len(words)}")
    else:
        lines.append("no 368 negation-symmetric set")
    (HERE / "negation_sat_log.txt").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
