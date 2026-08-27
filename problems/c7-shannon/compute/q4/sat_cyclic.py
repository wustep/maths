#!/usr/bin/env python3
"""Cadical: 74 cyclic-coordinate 5-orbits (size 370).

Rebuilds the orbit graph. Constants are excluded. A SAT model is 370
vertices. Also tries 73 orbits plus {00000,22222,44444} (size 368).
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

from c7_common import NVERTS, closed_neighbors, decode, encode, format_word

ENC = EncType.kmtotalizer


def rotate(v: int) -> int:
    c = decode(v)
    return encode(c[1:] + c[:1])


def orbit_tables():
    orbit_of = [-1] * NVERTS
    orbit_min = []
    constants = []
    for v in range(NVERTS):
        c = decode(v)
        if len(set(c)) == 1:
            constants.append(v)
            continue
        if orbit_of[v] >= 0:
            continue
        w, mn, seen = v, v, []
        for _ in range(5):
            seen.append(w)
            if w < mn:
                mn = w
            w = rotate(w)
        oid = len(orbit_min)
        orbit_min.append(mn)
        for u in seen:
            orbit_of[u] = oid
    return orbit_of, orbit_min, constants


def build_adj(orbit_of, n_orb):
    alive = [True] * n_orb
    edges = [set() for _ in range(n_orb)]
    for v in range(NVERTS):
        a = orbit_of[v]
        if a < 0:
            continue
        for u in closed_neighbors(v):
            if u == v:
                continue
            b = orbit_of[u]
            if b < 0:
                continue
            if a == b:
                alive[a] = False
            else:
                edges[a].add(b)
                edges[b].add(a)
    return alive, edges


def solve(alive, edges, forced_off, target, tag):
    n = len(alive)
    lits = []
    lit_of = {}
    vid = 0
    for i in range(n):
        if not alive[i] or i in forced_off:
            continue
        vid += 1
        lit_of[i] = vid
        lits.append(vid)
    clauses = []
    for i, lit in lit_of.items():
        for j in edges[i]:
            if j <= i or j not in lit_of:
                continue
            clauses.append([-lit, -lit_of[j]])
    extra = CardEnc.atleast(lits=lits, bound=target, top_id=vid, encoding=ENC)
    clauses.extend(extra.clauses)
    print(f"{tag} vars={len(lits)} clauses={len(clauses)} target={target}", flush=True)
    solver = Cadical195(bootstrap_with=clauses)
    sat = solver.solve()
    print(f"{tag} sat={sat}", flush=True)
    if not sat:
        return None
    model = set(solver.get_model())
    return [i for i, lit in lit_of.items() if lit in model]


def expand(ids, orbit_min, extra_const=()):
    words = list(extra_const)
    for i in ids:
        w = orbit_min[i]
        for _ in range(5):
            words.append(w)
            w = rotate(w)
    return sorted(set(words))


def main() -> int:
    t0 = time.time()
    orbit_of, orbit_min, constants = orbit_tables()
    n_orb = len(orbit_min)
    print(f"n_orb={n_orb} constants={len(constants)}", flush=True)
    alive, edges = build_adj(orbit_of, n_orb)
    print(f"alive={sum(alive)} t={time.time() - t0:.1f}s", flush=True)

    found = solve(alive, edges, set(), 74, "orb74")
    if found:
        words = expand(found, orbit_min)
        out = HERE / f"R{len(words)}_cyclic.txt"
        out.write_text("\n".join(format_word(v) for v in words) + "\n")
        print(f"wrote {out} size={len(words)}")
        return 0

    # 73 orbits plus the independent constants 00000,22222,44444.
    c024 = [constants[0], constants[2], constants[4]]
    blocked = set()
    for c in c024:
        blocked.update(closed_neighbors(c))
    forced_off = set()
    for i, mn in enumerate(orbit_min):
        w = mn
        for _ in range(5):
            if w in blocked:
                forced_off.add(i)
                break
            w = rotate(w)
    found = solve(alive, edges, forced_off, 73, "orb73_024")
    if found:
        words = expand(found, orbit_min, extra_const=c024)
        out = HERE / f"R{len(words)}_cyclic024.txt"
        out.write_text("\n".join(format_word(v) for v in words) + "\n")
        print(f"wrote {out} size={len(words)}")
        return 0

    print(f"DONE no cyclic 368 t={time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
