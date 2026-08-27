#!/usr/bin/env python3
"""3--6 letter support is too small for a 368-set.

An adjacent pair of letters in one coordinate induces a copy of
K2 ⊠ C7^{⊠4}. Its independence number equals α(C7^{⊠4}) ≤ 115
(Baumert et al. via Polak–Schrijver Table 1). Any independent set
that misses a letter in some coordinate therefore has size ≤ 345.

This finishes the 4-support shape that q1 left as a local-search
residue. It also rules out 5- and 6-support. A 368-set is
7-surjective in every coordinate.
"""

from __future__ import annotations

import itertools
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from c7_common import circ_dist, decode
from verify_set import first_conflict, load_set

# Published: α(C7^{⊠3}) = 33, Baumert lemma α(C_n^d) ≤ α(C_n^{d-1}) n/2.
ALPHA4_UB = 115  # 33 * 7 / 2 = 115.5, so <= 115
PAIR_UB = ALPHA4_UB  # alpha(K2 box C7^box4) = alpha(C7^box4)


def circ_adj(a: int, b: int) -> bool:
    return a != b and circ_dist(a, b) <= 1


def matching_number(letters: frozenset[int]) -> int:
    verts = sorted(letters)
    edges = [
        (verts[i], verts[j])
        for i in range(len(verts))
        for j in range(i + 1, len(verts))
        if circ_adj(verts[i], verts[j])
    ]
    best = 0
    m = len(edges)

    def rec(i: int, used: int, taken: int) -> None:
        nonlocal best
        if taken + (m - i) <= best:
            return
        if i == m:
            if taken > best:
                best = taken
            return
        rec(i + 1, used, taken)
        a, b = edges[i]
        bit = (1 << verts.index(a)) | (1 << verts.index(b))
        if used & bit == 0:
            rec(i + 1, used | bit, taken + 1)

    rec(0, 0, 0)
    return best


def support_bound(letters: frozenset[int]) -> tuple[int, str]:
    """Upper bound on an independent set using only these letters in one coord."""
    k = len(letters)
    nu = matching_number(letters)
    leftover = k - 2 * nu
    bound = nu * PAIR_UB + leftover * ALPHA4_UB
    why = f"matching={nu} leftover={leftover} {nu}*115+{leftover}*115={bound}"
    return bound, why


def drop_coord(v: int, axis: int) -> int:
    """Encode the 4-tuple obtained by deleting one coordinate."""
    coords = list(decode(v))
    coords.pop(axis)
    out = 0
    for c in coords:
        out = out * 7 + c
    return out


def pair_projections_ok(words: list[int]) -> list[str]:
    """The two-fiber projection of the seed is independent in C7^{⊠4}."""
    lines = []
    for axis in range(5):
        for a in range(7):
            b = (a + 1) % 7
            proj = []
            for v in words:
                c = decode(v)[axis]
                if c == a or c == b:
                    proj.append(drop_coord(v, axis))
            # Independence in the 4-dimensional strong product.
            conflict = None
            for i, u in enumerate(proj):
                for w in proj[i + 1 :]:
                    # adjacent in C7^{⊠4}: circ ≤ 1 in every remaining coord
                    x, y = u, w
                    adj = True
                    if x == y:
                        adj = True
                    else:
                        for _ in range(4):
                            if circ_dist(x % 7, y % 7) > 1:
                                adj = False
                                break
                            x //= 7
                            y //= 7
                    if adj:
                        conflict = (u, w)
                        break
                if conflict:
                    break
            ok = conflict is None
            lines.append(
                f"axis={axis} letters={a}{b} pair_fiber={len(proj)} "
                f"proj_indep={ok}"
            )
            if not ok:
                raise SystemExit(f"projection lemma failed on axis {axis} {a}{b}")
    return lines


def exact_alpha_small(nverts: int, adj_pred) -> int:
    """Exact α for nverts ≤ 64."""
    if nverts > 64:
        raise ValueError("bitset cap 64")
    neigh = [0] * nverts
    for i in range(nverts):
        for j in range(i + 1, nverts):
            if adj_pred(i, j):
                neigh[i] |= 1 << j
                neigh[j] |= 1 << i
    best = 0

    def rec(cand: int, cur: int) -> None:
        nonlocal best
        if cand.bit_count() + cur.bit_count() <= best:
            return
        if cand == 0:
            best = max(best, cur.bit_count())
            return
        v = (cand & -cand).bit_length() - 1
        rec(cand & ~neigh[v] & ~(1 << v), cur | (1 << v))
        rec(cand & ~(1 << v), cur)

    rec((1 << nverts) - 1, 0)
    return best


def check_k2_box_c7() -> int:
    """α(K2 ⊠ C7) = α(C7) = 3. Vertices (s,x), s in {0,1}, x in Z/7."""

    def adj(i, j):
        s0, x0 = divmod(i, 7)
        s1, x1 = divmod(j, 7)
        if i == j:
            return False
        # strong product K2 ⊠ C7
        ok_s = s0 == s1 or abs(s0 - s1) == 1
        ok_x = x0 == x1 or circ_dist(x0, x1) <= 1
        return ok_s and ok_x

    return exact_alpha_small(14, adj)


def sat_has_indep(n: int, edges: list[tuple[int, int]], k: int) -> bool:
    """True iff the n-vertex graph has an independent set of size k."""
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Cadical195

    lits = list(range(1, n + 1))
    clauses = [[-u - 1, -v - 1] for u, v in edges]
    cnf = CardEnc.atleast(lits=lits, bound=k, top_id=n, encoding=EncType.kmtotalizer)
    clauses.extend(cnf.clauses)
    solver = Cadical195(bootstrap_with=clauses)
    return bool(solver.solve())


def check_k2_box_c7_sq() -> tuple[int, int]:
    """α(C7^{⊠2}) by bitset, α(K2 ⊠ C7^{⊠2}) by SAT (no 11-set)."""

    def adj2(u, v):
        if u == v:
            return False
        a0, b0 = divmod(u, 7)
        a1, b1 = divmod(v, 7)
        return circ_dist(a0, a1) <= 1 and circ_dist(b0, b1) <= 1

    alpha2 = exact_alpha_small(49, adj2)
    edges = []
    for i in range(98):
        for j in range(i + 1, 98):
            s0, rest0 = divmod(i, 49)
            s1, rest1 = divmod(j, 49)
            if not (s0 == s1 or abs(s0 - s1) == 1):
                continue
            a0, b0 = divmod(rest0, 7)
            a1, b1 = divmod(rest1, 7)
            if circ_dist(a0, a1) <= 1 and circ_dist(b0, b1) <= 1:
                edges.append((i, j))
    has11 = sat_has_indep(98, edges, 11)
    has10 = sat_has_indep(98, edges, 10)
    if has11 or not has10:
        raise SystemExit(f"K2 box C7^box2 SAT failed has10={has10} has11={has11}")
    return alpha2, 10


def main() -> None:
    t0 = time.time()
    lines: list[str] = []
    seed = load_set(ROOT / "R367.txt")
    assert first_conflict(seed) is None
    lines.append(f"seed size={len(seed)} independent=True")

    fibers = [[0] * 7 for _ in range(5)]
    for v in seed:
        w = decode(v)
        for ax, c in enumerate(w):
            fibers[ax][c] += 1
    lines.append(f"R367 fibers {fibers}")
    for ax, row in enumerate(fibers):
        if min(row) == 0 or sum(row) != 367:
            raise SystemExit(f"seed not 7-surjective on axis {ax}")
    lines.append("R367 is 7-surjective on every coordinate")

    proj_lines = pair_projections_ok(seed)
    pair_sizes = []
    for row in proj_lines:
        # "pair_fiber=N"
        n = int(row.split("pair_fiber=")[1].split()[0])
        pair_sizes.append(n)
        if n > PAIR_UB:
            raise SystemExit(f"pair fiber {n} exceeds 115")
    lines.append(f"pair-fiber sizes min={min(pair_sizes)} max={max(pair_sizes)}")
    lines.append(f"pair projections independent in C7^box4: {len(proj_lines)} pairs")

    a_k2c7 = check_k2_box_c7()
    lines.append(f"alpha(K2 box C7)={a_k2c7} (expect 3)")
    if a_k2c7 != 3:
        raise SystemExit("K2 box C7 failed")

    a2, a_pair2 = check_k2_box_c7_sq()
    lines.append(f"alpha(C7 box2)={a2} alpha(K2 box C7^box2)={a_pair2} (expect 10,10)")
    if a2 != 10 or a_pair2 != 10:
        raise SystemExit("small-dimension pair-slice failed")

    worst = 0
    n_ok = 0
    by_k: dict[int, list[tuple[frozenset[int], int, str]]] = defaultdict(list)
    for k in range(1, 7):
        for letters in itertools.combinations(range(7), k):
            s = frozenset(letters)
            bound, why = support_bound(s)
            by_k[k].append((s, bound, why))
            worst = max(worst, bound)
            if bound < 368:
                n_ok += 1
    lines.append(f"subsets of size 1..6: {n_ok} all have bound < 368")
    lines.append(f"worst missing-letter bound {worst}")
    for k in range(1, 7):
        bounds = sorted({b for _, b, _ in by_k[k]})
        sample = by_k[k][0]
        lines.append(
            f"  k={k} n={len(by_k[k])} bounds={bounds} "
            f"e.g. {sorted(sample[0])} {sample[2]}"
        )
        if max(bounds) >= 368:
            raise SystemExit(f"k={k} bound {max(bounds)} does not rule out 368")

    lines.append(
        "conclusion: a 368-set uses all 7 letters in every coordinate. "
        "4-support (and 3,5,6) is impossible, not a search residue."
    )
    lines.append(f"seconds {time.time() - t0:.2f}")
    text = "\n".join(lines) + "\n"
    print(text, end="")
    (HERE / "support_bound_log.txt").write_text(text)


if __name__ == "__main__":
    main()
