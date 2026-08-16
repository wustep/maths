#!/usr/bin/env python3
"""Pack cosets of a good 2-dimensional F_7-code.

If V <= (Z/7)^5 is 2-dimensional and V ∩ {-1,0,1}^5 = {0}, then a union of
cosets a+V is independent iff the quotient points are independent in the
Cayley graph of F_7^5/V with connection set ( {-1,0,1}^5 + V )/V.
That graph has 343 vertices. Eight independent cosets would give 392 points.
"""

from __future__ import annotations

import itertools
import random
import time
from pathlib import Path

from c7_common import DIM, N, encode, format_word, residual_of
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent
SMALL = {0, 1, 6}


def apply(rows, coeffs):
    out = [0] * DIM
    for c, row in zip(coeffs, rows):
        if not c:
            continue
        for j in range(DIM):
            out[j] = (out[j] + c * row[j]) % N
    return tuple(out)


def is_good_2(rows) -> bool:
    for coeffs in itertools.product(range(N), repeat=2):
        if coeffs == (0, 0):
            continue
        w = apply(rows, coeffs)
        if all(x in SMALL for x in w):
            return False
    return True


def span2(rows):
    return [apply(rows, (a, b)) for a in range(N) for b in range(N)]


def complete_basis(rows):
    """Extend 2 rows to an F7-basis of F7^5. Return 3 complementary rows."""
    mat = [list(r) for r in rows]
    used = [False] * 5
    # mark pivot-ish columns
    r = 0
    tmp = [list(x) for x in mat]
    for c in range(5):
        piv = None
        for i in range(r, 2):
            if tmp[i][c] % N:
                piv = i
                break
        if piv is None:
            continue
        tmp[r], tmp[piv] = tmp[piv], tmp[r]
        inv = pow(tmp[r][c], -1, N)
        tmp[r] = [(x * inv) % N for x in tmp[r]]
        for i in range(2):
            if i == r:
                continue
            f = tmp[i][c]
            if f:
                tmp[i] = [(tmp[i][j] - f * tmp[r][j]) % N for j in range(5)]
        used[c] = True
        r += 1
        if r == 2:
            break
    comps = []
    for c in range(5):
        if used[c]:
            continue
        e = [0] * 5
        e[c] = 1
        comps.append(tuple(e))
    # may have 3 standard basis vectors not used; if fewer, fill remaining
    while len(comps) < 3:
        for c in range(5):
            e = [0] * 5
            e[c] = 1
            if tuple(e) not in comps and tuple(e) not in rows:
                comps.append(tuple(e))
                break
    return comps[:3]


def quotient_index(v, comps):
    """Coordinates of v along the complementary 3-space, assuming V-coords ignored.

    We identify F7^5 / V with F7^3 via a complementary subspace W. This is only
    a bijection if V ⊕ W = whole space. We check that by rank.
    """
    # solve v = a0 r0 + a1 r1 + b0 c0 + b1 c1 + b2 c2
    # We only need (b0,b1,b2) as the quotient coordinate if the 5x5 is invertible.
    return None  # filled in after we build the 5x5


def invert5(rows5):
    # Gaussian invert over F7. rows5 is 5 tuples. Return inverse as list of lists.
    a = [list(r) + [1 if i == j else 0 for j in range(5)] for i, r in enumerate(rows5)]
    for col in range(5):
        piv = None
        for i in range(col, 5):
            if a[i][col] % N:
                piv = i
                break
        if piv is None:
            return None
        a[col], a[piv] = a[piv], a[col]
        inv = pow(a[col][col], -1, N)
        a[col] = [(x * inv) % N for x in a[col]]
        for i in range(5):
            if i == col:
                continue
            f = a[i][col]
            if f:
                a[i] = [(a[i][j] - f * a[col][j]) % N for j in range(10)]
    return [row[5:] for row in a]


def matvec(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(5)) % N for i in range(len(M)))


def greedy_mis_graph(n: int, adj: list[int], rng: random.Random) -> list[int]:
    order = list(range(n))
    rng.shuffle(order)
    taken = []
    banned = 0
    # adj[i] is a bitset of neighbors (n=343 fits in a Python int)
    for v in order:
        if (banned >> v) & 1:
            continue
        taken.append(v)
        banned |= adj[v] | (1 << v)
    return taken


def local_improve(n: int, adj: list[int], taken: list[int], rounds: int, rng: random.Random) -> list[int]:
    s = set(taken)
    for _ in range(rounds):
        # 1-out: remove one, add as many as possible
        if not s:
            break
        v = rng.choice(list(s))
        s.remove(v)
        banned = 0
        for u in s:
            banned |= adj[u] | (1 << u)
        extras = [i for i in range(n) if not ((banned >> i) & 1)]
        rng.shuffle(extras)
        added = []
        for i in extras:
            if (banned >> i) & 1:
                continue
            added.append(i)
            banned |= adj[i] | (1 << i)
        if len(s) + len(added) >= len(taken):
            s.update(added)
            taken = list(s)
        else:
            s.add(v)
    return taken


def main() -> None:
    t0 = time.time()
    rng = random.Random(0)
    # Enumerate RREF 2x5
    mats = []
    for pivots in itertools.combinations(range(5), 2):
        free = [j for j in range(5) if j not in pivots]
        for fill in itertools.product(range(N), repeat=2 * len(free)):
            rows = []
            idx = 0
            for p in pivots:
                row = [0] * 5
                row[p] = 1
                for j in free:
                    row[j] = fill[idx]
                    idx += 1
                rows.append(tuple(row))
            mats.append(tuple(rows))
    print(f"2x5 rref {len(mats)}", flush=True)
    best_cosets = 0
    best_total = 0
    n_good = 0
    lines = []
    checked = 0
    for rows in mats:
        checked += 1
        if not is_good_2(rows):
            if checked % 100000 == 0:
                print(f"checked {checked} good={n_good} best_cosets={best_cosets}", flush=True)
            continue
        n_good += 1
        comps = []
        # complementary standard basis columns
        piv = [i for i, x in enumerate(rows[0]) if x == 1][:1]
        # simpler: try standard basis triples until 5x5 invertible
        inv = None
        chosen = None
        for triple in itertools.combinations(range(5), 3):
            cand = [tuple(1 if j == t else 0 for j in range(5)) for t in triple]
            M = list(rows) + cand
            invM = invert5(M)
            if invM is not None:
                chosen = cand
                inv = invM
                break
        if inv is None:
            continue
        # quotient coord of a vector x is the last 3 coords of inv * x
        def qcoord(x):
            y = matvec(inv, x)
            return y[2] * 49 + y[3] * 7 + y[4]

        # forbidden quotient points: images of {-1,0,1}^5
        forbidden = set()
        for deltas in itertools.product((-1, 0, 1), repeat=5):
            forbidden.add(qcoord(tuple(d % N for d in deltas)))
        # Cayley graph on 343 points, edge if difference in forbidden\{0}
        adj = [0] * 343
        forb = [f for f in forbidden if f != 0]
        for i in range(343):
            bits = 0
            for f in forb:
                # difference in F7^3
                a0, r = divmod(i, 49)
                a1, a2 = divmod(r, 7)
                b0, r = divmod(f, 49)
                b1, b2 = divmod(r, 7)
                d0 = (a0 - b0) % 7
                d1 = (a1 - b1) % 7
                d2 = (a2 - b2) % 7
                j = d0 * 49 + d1 * 7 + d2
                if j != i:
                    bits |= 1 << j
            adj[i] = bits
        # several greedy + local
        best_here = []
        for trial in range(12):
            pack = greedy_mis_graph(343, adj, rng)
            pack = local_improve(343, adj, pack, 80, rng)
            if len(pack) > len(best_here):
                best_here = pack
        ncos = len(best_here)
        total = 49 * ncos
        if ncos > best_cosets or total > best_total:
            best_cosets = max(best_cosets, ncos)
            best_total = max(best_total, total)
            print(f"good V={rows} forbidden={len(forbidden)} cosets={ncos} total={total}", flush=True)
            lines.append(f"{rows} forb={len(forbidden)} cosets={ncos} total={total}")
        if total >= 368:
            # materialize the union
            V = span2(rows)
            # map quotient index -> a representative in W
            reps = {}
            for b in itertools.product(range(N), repeat=3):
                w = apply(chosen, b)
                reps[qcoord(w)] = w
            pts = []
            for qi in best_here:
                w = reps[qi]
                for v in V:
                    pts.append(encode(tuple((w[j] + v[j]) % N for j in range(5))))
            pts = sorted(set(pts))
            if first_conflict(pts) is None:
                out = HERE / f"R{len(pts)}_cosets.txt"
                out.write_text("\n".join(format_word(v) for v in pts) + "\n")
                print(f"WROTE {out} size={len(pts)}")
                (HERE / "coset_search.txt").write_text(
                    f"HIT size {len(pts)}\n" + "\n".join(lines) + "\n"
                )
                return
        if n_good <= 3 or n_good % 20 == 0:
            print(f"  good={n_good} checked={checked} best_cosets={best_cosets}", flush=True)
    (HERE / "coset_search.txt").write_text(
        f"good {n_good}\nbest_cosets {best_cosets}\nbest_total {best_total}\n"
        f"seconds {time.time()-t0:.1f}\n" + "\n".join(lines) + "\n"
    )
    print(f"done good={n_good} best_cosets={best_cosets} best_total={best_total} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
