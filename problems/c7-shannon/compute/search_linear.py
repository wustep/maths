#!/usr/bin/env python3
"""F_7-linear 3-dimensional codes in (Z/7)^5, then residual extension.

A 3-dim subspace of size 343 is independent iff it meets {-1,0,1}^5 only at 0.
Enumerate generator matrices in row-echelon form, keep good codes, compute
the residual graph, and take a maximum (or greedy) independent set there.
"""

from __future__ import annotations

import itertools
import time
from pathlib import Path

from c7_common import DIM, N, adjacent, encode, format_word, residual_of
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent
SMALL = {0, 1, 6}


def mat_apply(rows: tuple[tuple[int, ...], ...], coeffs: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * DIM
    for c, row in zip(coeffs, rows):
        if c == 0:
            continue
        for j in range(DIM):
            out[j] = (out[j] + c * row[j]) % N
    return tuple(out)


def subspace(rows: tuple[tuple[int, ...], ...]) -> list[int]:
    pts = []
    for coeffs in itertools.product(range(N), repeat=len(rows)):
        pts.append(encode(mat_apply(rows, coeffs)))
    return pts


def is_good(rows: tuple[tuple[int, ...], ...]) -> bool:
    for coeffs in itertools.product(range(N), repeat=len(rows)):
        if all(c == 0 for c in coeffs):
            continue
        w = mat_apply(rows, coeffs)
        if all(x in SMALL for x in w):
            return False
    return True


def echelon_3x5() -> list[tuple[tuple[int, ...], ...]]:
    """3x5 full-rank matrices in RREF, pivots increasing."""
    mats = []
    for pivots in itertools.combinations(range(DIM), 3):
        free = [j for j in range(DIM) if j not in pivots]
        # each free column: 3 entries in F7
        for fill in itertools.product(range(N), repeat=3 * len(free)):
            rows = []
            idx = 0
            for r, p in enumerate(pivots):
                row = [0] * DIM
                row[p] = 1
                for j in free:
                    row[j] = fill[idx]
                    idx += 1
                rows.append(tuple(row))
            mats.append(tuple(rows))
    return mats


def residual_vertices(base: list[int]) -> list[int]:
    return residual_of(base)


def greedy_mis(verts: list[int]) -> list[int]:
    if not verts:
        return []
    deg = []
    vset = set(verts)
    # cheap degree: count adjacencies among residual
    adj = {v: [] for v in verts}
    for i, u in enumerate(verts):
        for v in verts[i + 1 :]:
            if adjacent(u, v):
                adj[u].append(v)
                adj[v].append(u)
    order = sorted(verts, key=lambda v: len(adj[v]))
    taken = []
    banned = set()
    for v in order:
        if v in banned:
            continue
        taken.append(v)
        banned.add(v)
        banned.update(adj[v])
    return taken


def main() -> None:
    t0 = time.time()
    mats = echelon_3x5()
    print(f"rref matrices {len(mats)}", flush=True)
    best_ext = 0
    best_total = 0
    n_good = 0
    lines = ["# rows residual extension total"]
    # There are Gaussian [5 choose 3]_7 = 14008? Wait RREF count is smaller.
    # 3 free columns * 3 rows = 9 entries: 7^9 = 40353618 if all pivot sets...
    # 10 pivot triples * 7^6 (2 free cols * 3) = 10 * 117649 = 1.17e6. Feasible.
    checked = 0
    for rows in mats:
        checked += 1
        if not is_good(rows):
            if checked % 20000 == 0:
                print(f"checked {checked}/{len(mats)} good={n_good} best_total={best_total}", flush=True)
            continue
        n_good += 1
        pts = subspace(rows)
        assert len(set(pts)) == 343
        residual = residual_vertices(pts)
        ext = greedy_mis(residual)
        total = 343 + len(ext)
        if total > best_total:
            best_total = total
            best_ext = len(ext)
            print(f"good code residual={len(residual)} ext={len(ext)} total={total}", flush=True)
            if total >= 368:
                R = sorted(set(pts) | set(ext))
                if first_conflict(R) is None:
                    out = HERE / f"R{len(R)}_linear.txt"
                    out.write_text("\n".join(format_word(v) for v in R) + "\n")
                    print(f"WROTE {out}")
        lines.append(f"{rows} {len(residual)} {len(ext)} {total}")
        if checked % 20000 == 0:
            print(f"checked {checked}/{len(mats)} good={n_good} best_total={best_total}", flush=True)
    (HERE / "linear_search.txt").write_text(
        f"matrices {len(mats)}\ngood {n_good}\nbest_total {best_total}\nbest_ext {best_ext}\n"
        f"seconds {time.time()-t0:.1f}\n" + "\n".join(lines[:50]) + "\n"
    )
    print(f"done good={n_good} best_total={best_total} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
