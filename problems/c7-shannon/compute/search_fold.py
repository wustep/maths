#!/usr/bin/env python3
"""Fold-and-repair over nearby circular orbits, Polak-Schrijver style.

For n,q with n/k(n,q) close to 7/2, try a few shifts and the fold
i |-> floor(2i/k0) into Z/7, keep isolated image vertices, extend the residual.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from c7_common import DIM, encode, format_word
from reconstruct_polak import isolated_vertices, max_independent_set, residual_vertices, induced_edges
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent


def circ(x: int, n: int) -> int:
    x %= n
    return x if x <= n - x else n - x


def k_of(n: int, q: int) -> int:
    pows = [pow(q, i, n) for i in range(DIM)]
    best = n
    for t in range(1, n):
        mx = 0
        for p in pows:
            x = (t * p) % n
            d = x if x <= n - x else n - x
            if d > mx:
                mx = d
                if mx >= best:
                    break
        if mx < best:
            best = mx
    return best


def fold_orbit(n: int, q: int, shift: tuple[int, ...], den: int) -> list[int]:
    pows = [pow(q, i, n) for i in range(DIM)]
    out = []
    for t in range(n):
        coords = [((t * p + shift[j]) % n) * 2 // den for j, p in enumerate(pows)]
        if any(c > 6 for c in coords):
            return []
        out.append(encode(coords))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-lo", type=int, default=360)
    ap.add_argument("--n-hi", type=int, default=400)
    ap.add_argument("--max-q", type=int, default=40)
    args = ap.parse_args()
    t0 = time.time()
    best = 0
    lines = []
    # Prefer n with some q giving k close to 2n/7
    for n in range(args.n_lo, args.n_hi + 1):
        need = (2 * n + 6) // 7
        cands = []
        qmax = min(args.max_q, n - 2)
        for q in range(2, qmax + 1):
            k = k_of(n, q)
            if k >= need - 4:
                cands.append((k, q))
        cands.sort(reverse=True)
        cands = cands[:4]
        if not cands:
            continue
        print(f"n={n} need={need} cands={cands}", flush=True)
        for k, q in cands:
            dens = sorted(set([2 * k, 2 * k - 1, 2 * k + 1, 109, 108, 110]))
            shifts = [
                (0, 0, 0, 0, 0),
                (40, 123, 40, 123, 40) if n == 382 else (n // 9, n // 3, n // 9, n // 3, n // 9),
                (1, 0, 0, 0, 0),
            ]
            for den in dens:
                if den <= 0:
                    continue
                for shift in shifts:
                    folded = fold_orbit(n, q, shift, den)
                    if not folded:
                        continue
                    M = isolated_vertices(folded)
                    residual = residual_vertices(M)
                    if len(residual) > 90:
                        # exact MIS still ok-ish, but skip huge residuals this pass
                        I = []
                    else:
                        I = max_independent_set(residual)
                    total = len(M) + len(I)
                    if total > best:
                        best = total
                        print(
                            f"  best {total} n={n} q={q} k={k} den={den} shift={shift} "
                            f"|M|={len(M)} res={len(residual)} |I|={len(I)}",
                            flush=True,
                        )
                    lines.append(
                        f"{n} {q} {k} {den} {shift} M={len(M)} res={len(residual)} I={len(I)} total={total}"
                    )
                    if total >= 368:
                        R = sorted(set(M) | set(I))
                        if first_conflict(R) is None:
                            out = HERE / f"R{len(R)}_fold.txt"
                            out.write_text("\n".join(format_word(v) for v in R) + "\n")
                            print(f"WROTE {out}")
    (HERE / "fold_search.txt").write_text(
        f"best {best}\nseconds {time.time()-t0:.1f}\n" + "\n".join(lines) + "\n"
    )
    print(f"done best={best} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
