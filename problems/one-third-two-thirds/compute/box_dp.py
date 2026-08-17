#!/usr/bin/env python3
"""Linear extensions of a 3-dimensional box C_a × C_b × C_c via plane partitions.

An order ideal is a plane partition: h[x][y] in 0..c, weakly decreasing in x,y
(min-corner at (0,0,0)). F[h] = e(ideal h). We also count e(P + u<v) for the
two atoms
    u = (1,0,0), v = (0,1,0)
by restricting to ideals that contain u whenever they contain v.

States are encoded as tuples of length a*b (row-major).
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from math import gcd
from pathlib import Path


def enumerate_plane_partitions(a: int, b: int, c: int):
    """All weakly decreasing a×b matrices with entries in 0..c."""
    out = []
    cell = a * b
    cur = [0] * cell

    def val(x, y):
        return cur[x * b + y]

    def rec(pos):
        if pos == cell:
            out.append(tuple(cur))
            return
        x, y = divmod(pos, b)
        hi = c
        if x:
            hi = min(hi, val(x - 1, y))
        if y:
            hi = min(hi, val(x, y - 1))
        for t in range(hi + 1):
            cur[pos] = t
            rec(pos + 1)

    rec(0)
    return out


def maxima_of(h, a, b, c):
    """Maximal cells (x,y,z) of the ideal h."""
    mx = []
    for x in range(a):
        for y in range(b):
            k = h[x * b + y]
            if k == 0:
                continue
            # (x,y,k-1) is maximal iff no larger x or y keeps height ≥ k
            if x + 1 < a and h[(x + 1) * b + y] >= k:
                continue
            if y + 1 < b and h[x * b + y + 1] >= k:
                continue
            mx.append((x, y, k - 1))
    return mx


def remove_cell(h, a, b, x, y):
    lst = list(h)
    lst[x * b + y] -= 1
    return tuple(lst)


def contains_cell(h, b, x, y, z):
    return h[x * b + y] > z


def box_counts(a: int, b: int, c: int):
    """Return e(P), e(P+u<v), e(P+v<u) for u=(1,0,0), v=(0,1,0)."""
    assert a >= 2 and b >= 2 and c >= 1
    pps = enumerate_plane_partitions(a, b, c)
    # map state -> index for optional dense tables; we just use dict recursion
    states = set(pps)

    @lru_cache(maxsize=None)
    def F(h):
        if all(t == 0 for t in h):
            return 1
        tot = 0
        for x, y, z in maxima_of(h, a, b, c):
            tot += F(remove_cell(h, a, b, x, y))
        return tot

    full = pps[-1] if pps and pps[-1] == tuple([c] * (a * b)) else None
    # enumerate_plane_partitions ends with the full box (all c) because we
    # fill increasing positions; the last one is not necessarily full.
    full = tuple([c] * (a * b))
    assert full in states
    e = F(full)

    # Q = P + u<v. Q-ideals: P-ideals with (v in I => u in I).
    # u in I iff h[1,0] ≥ 1; v in I iff h[0,1] ≥ 1.
    def is_Q_ideal(h):
        u_in = h[1 * b + 0] >= 1
        v_in = h[0 * b + 1] >= 1
        return (not v_in) or u_in

    def maxima_Q(h):
        """Maximal cells in I wrt Q = P+u<v."""
        out = []
        for x, y, z in maxima_of(h, a, b, c):
            # extra: u is not Q-maximal if v is still in I
            if (x, y, z) == (1, 0, 0) and contains_cell(h, b, 0, 1, 0):
                continue
            out.append((x, y, z))
        return out

    @lru_cache(maxsize=None)
    def FQ(h):
        if all(t == 0 for t in h):
            return 1
        tot = 0
        for x, y, z in maxima_Q(h):
            hp = remove_cell(h, a, b, x, y)
            if is_Q_ideal(hp) or all(t == 0 for t in hp):
                tot += FQ(hp)
        return tot

    # R = P + v<u
    def is_R_ideal(h):
        u_in = h[1 * b + 0] >= 1
        v_in = h[0 * b + 1] >= 1
        return (not u_in) or v_in

    def maxima_R(h):
        out = []
        for x, y, z in maxima_of(h, a, b, c):
            if (x, y, z) == (0, 1, 0) and contains_cell(h, b, 1, 0, 0):
                continue
            out.append((x, y, z))
        return out

    @lru_cache(maxsize=None)
    def FR(h):
        if all(t == 0 for t in h):
            return 1
        tot = 0
        for x, y, z in maxima_R(h):
            hp = remove_cell(h, a, b, x, y)
            if is_R_ideal(hp) or all(t == 0 for t in hp):
                tot += FR(hp)
        return tot

    e_uv = FQ(full)
    e_vu = FR(full)
    if e_uv + e_vu != e:
        raise AssertionError(
            f"C{a}xC{b}xC{c}: e_uv+e_vu={e_uv}+{e_vu} != e={e}"
        )
    return e, e_uv, e_vu, F.cache_info(), len(pps)


def delta_of_pair(e, e_uv, e_vu):
    mn = min(e_uv, e_vu)
    g = gcd(mn, e)
    return mn // g, e // g, mn, e


def main():
    rows = []
    # All a≤b, a≥2, abc not too huge. State count = # plane partitions.
    jobs = []
    for a in range(2, 6):
        for b in range(a, 7):
            for c in range(1, 11):
                # #PP(a,b,c) ~ polynomial of degree ab
                if a * b * c > 48 and a >= 4:
                    continue
                if a == 3 and b >= 5 and c >= 7:
                    continue
                if a == 4 and b >= 4 and c >= 5:
                    continue
                jobs.append((a, b, c))
    print(f"{len(jobs)} jobs")
    for a, b, c in jobs:
        e, uv, vu, info, nst = box_counts(a, b, c)
        frac = delta_of_pair(e, uv, vu)
        rec = {
            "dims": [a, b, c],
            "n": a * b * c,
            "e": e,
            "e_uv": uv,
            "e_vu": vu,
            "uv_frac": [frac[0], frac[1]],
            "uv_float": uv / e,
            "states": nst,
        }
        rows.append(rec)
        flag = "  *** <1/3 ***" if uv < e / 3 and vu < e / 3 else ""
        print(
            f"  C{a}xC{b}xC{c} n={a*b*c} e={e} uv={uv}/{e}={uv/e:.6f}"
            f" red={frac[0]}/{frac[1]} states={nst}{flag}"
        )
        sys.stdout.flush()

    path = Path(__file__).resolve().parent / "boxes.json"
    path.write_text(json.dumps({"boxes": rows}, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
