#!/usr/bin/env python3
"""Search Reed-Solomon orbits {t*(1,q,...,q^{4})} in Z/n for a direct C7 fold.

If min_t max_i circ_dist(t q^i, 0) >= 2n/7, the floor(2i/k) map lands in C7
and the image is independent. Report any image of size >= 368.
Also records near-misses (ratio n/k just above 7/2) for fold-and-repair.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def circ(x: int, n: int) -> int:
    x %= n
    return x if x <= n - x else n - x


def min_max_circ(n: int, q: int, d: int = 5) -> int:
    pows = [1]
    for _ in range(d - 1):
        pows.append((pows[-1] * q) % n)
    best = n
    # t and n-t give the same distances
    for t in range(1, n):
        mx = 0
        acc = t
        for p in pows:
            x = (t * p) % n
            dist = x if x <= n - x else n - x
            if dist > mx:
                mx = dist
                if mx >= best:
                    break
        if mx < best:
            best = mx
            # hopeless for C7 if already below 2n/7 - 2; keep going for logging
    return best


def search(n_lo: int, n_hi: int, out_path: Path) -> None:
    t0 = time.time()
    hits = []
    near = []
    for n in range(n_lo, n_hi + 1):
        need = (2 * n + 6) // 7  # smallest integer k with k >= 2n/7
        # q and n-q, and q=0,1 give degenerate orbits
        seen_k = -1
        best_q = None
        best_k = -1
        for q in range(2, n - 1):
            k = min_max_circ(n, q)
            if k > best_k:
                best_k = k
                best_q = q
            if k >= need:
                hits.append((n, q, k, need, n / k if k else None))
                break
        ratio = n / best_k if best_k else None
        near.append((n, best_q, best_k, need, ratio))
        if n % 10 == 0:
            print(f"n={n} best_k={best_k} need={need} ratio={ratio:.5f} hits={len(hits)}", flush=True)
    dt = time.time() - t0
    lines = ["# n q k need n/k"]
    lines.append("# HITS (direct C7 homomorphism)")
    for row in hits:
        lines.append("HIT " + " ".join(str(x) for x in row))
    lines.append("# BEST per n")
    for n, q, k, need, ratio in near:
        tag = "OK" if k >= need else "MISS"
        lines.append(f"{tag} {n} {q} {k} {need} {ratio:.6f}")
    lines.append(f"# seconds {dt:.2f}")
    out_path.write_text("\n".join(lines) + "\n")
    print(f"hits={len(hits)} wrote {out_path} in {dt:.1f}s")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-lo", type=int, default=368)
    ap.add_argument("--n-hi", type=int, default=420)
    ap.add_argument("-o", type=Path, default=HERE / "orbit_search.txt")
    args = ap.parse_args()
    search(args.n_lo, args.n_hi, args.o)


if __name__ == "__main__":
    main()
