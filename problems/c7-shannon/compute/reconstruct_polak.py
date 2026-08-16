#!/usr/bin/env python3
"""Reconstruct the Polak-Schrijver pipeline (IPL 2019, section 3).

S = { t*(1,7,7^2,7^3,7^4) | t in Z/382 } is independent in C_{108,382}^5.
Shift by (40,123,40,123,40), fold i |-> floor(2i/109) into Z/7, keep isolated
vertices of the image (M, size 327), then take a maximum independent set in
the residual graph of vertices still addable to M.
"""

from __future__ import annotations

from pathlib import Path

from c7_common import DIM, adjacent, encode, format_word, residual_of
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent
MOD = 382
Q = 7
SHIFT = (40, 123, 40, 123, 40)
FOLD_DEN = 109


def fold_letter(i: int) -> int:
    return (2 * i) // FOLD_DEN


def geometric_orbit() -> list[tuple[int, ...]]:
    pows = [pow(Q, i, MOD) for i in range(DIM)]
    out = []
    for t in range(MOD):
        out.append(tuple((t * p + SHIFT[j]) % MOD for j, p in enumerate(pows)))
    return out


def fold_words(orbit: list[tuple[int, ...]]) -> list[int]:
    return [encode(fold_letter(x) for x in w) for w in orbit]


def isolated_vertices(words: list[int]) -> list[int]:
    uniq = sorted(set(words))
    isolated = []
    for i, u in enumerate(uniq):
        if any(adjacent(u, v) for j, v in enumerate(uniq) if j != i):
            continue
        isolated.append(u)
    return isolated


def residual_vertices(base: list[int]) -> list[int]:
    return residual_of(base)


def induced_edges(verts: list[int]) -> list[tuple[int, int]]:
    edges = []
    for i, u in enumerate(verts):
        for v in verts[i + 1 :]:
            if adjacent(u, v):
                edges.append((u, v))
    return edges


def max_independent_set(verts: list[int]) -> list[int]:
    n = len(verts)
    idx = {v: i for i, v in enumerate(verts)}
    neigh = [0] * n
    for u, v in induced_edges(verts):
        i, j = idx[u], idx[v]
        neigh[i] |= 1 << j
        neigh[j] |= 1 << i
    best: list[int] = []

    def rec(cand: int, cur: int) -> None:
        nonlocal best
        if cand.bit_count() + cur.bit_count() <= len(best):
            return
        if cand == 0:
            if cur.bit_count() > len(best):
                best = [verts[i] for i in range(n) if (cur >> i) & 1]
            return
        v = max(
            (i for i in range(n) if (cand >> i) & 1),
            key=lambda i: (neigh[i] & cand).bit_count(),
        )
        rec(cand & ~neigh[v] & ~(1 << v), cur | (1 << v))
        rec(cand & ~(1 << v), cur)

    rec((1 << n) - 1, 0)
    return best


def main() -> None:
    orbit = geometric_orbit()
    assert len(orbit) == MOD
    folded = fold_words(orbit)
    print(f"folded unique={len(set(folded))} raw={len(folded)}")
    M = isolated_vertices(folded)
    print(f"|M|={len(M)}")
    residual = residual_vertices(M)
    edges = induced_edges(residual)
    print(f"residual verts={len(residual)} edges={len(edges)}")
    I = max_independent_set(residual)
    print(f"|I|={len(I)}")
    R = sorted(set(M) | set(I))
    print(f"|R|={len(R)}")
    conflict = first_conflict(R)
    if conflict is not None:
        a, b = conflict
        raise SystemExit(f"reconstructed set is adjacent: {format_word(a)} {format_word(b)}")
    out = HERE / "R_reconstructed.txt"
    out.write_text("\n".join(format_word(v) for v in R) + "\n")
    print(f"wrote {out}")
    (HERE / "reconstruct_stats.txt").write_text(
        f"folded_unique {len(set(folded))}\n"
        f"M {len(M)}\n"
        f"residual_verts {len(residual)}\n"
        f"residual_edges {len(edges)}\n"
        f"I {len(I)}\n"
        f"R {len(R)}\n"
    )


if __name__ == "__main__":
    main()
