#!/usr/bin/env python3
"""The layer lemma for sigma with a c-dimensional fixed space.

Write V = M (+) T with T the fixed space, dim T = c.  sigma acts only on the
M-part, so every sigma-orbit of size p sits in one "layer" t in T, each layer
holds the same number L of orbits, and the layer of any sum is forced:

  membership -> t_i    inside orbit i -> 0    orbits i,j -> t_i + t_j
  orbit i with fixed g -> t_i + g

In a layer t that receives no cross-orbit sum, the only orbits available are
one per chosen orbit i (from the unique g = t + t_i, if it is in the chosen
fixed set) plus, when t = 0, the internal sums.  So such a layer can hold at
most k covered orbits (plus W internal ones when t = 0), and if that is less
than L the configuration is impossible.  Counting layers gives the lemma:

  #layers needing a cross pair  <=  C(k,2).

This script measures L and W for a given sigma and reports the verdict.

Usage: layer_lemma.py <sigma-file> <n>
"""
import sys
from math import comb


def main():
    path, n = sys.argv[1], int(sys.argv[2])
    tok = open(path).read().split()
    r = int(tok[0])
    cols = [int(x) for x in tok[1:1 + r]]
    N = 1 << r

    def sig(v):
        out = 0
        for i in range(r):
            if (v >> i) & 1:
                out ^= cols[i]
        return out

    fixed = [v for v in range(1, N) if sig(v) == v]
    F = fixed + [0]
    assert len(F) & (len(F) - 1) == 0, "fixed set is not a subspace"
    c = len(F).bit_length() - 1
    fset = set(F)

    oid, reps = {}, []
    for v in range(1, N):
        if v in fset or v in oid:
            continue
        k = len(reps)
        u = v
        while u not in oid:
            oid[u] = k
            u = sig(u)
        reps.append(v)
    p = (N - len(F)) // len(reps)

    # sigma has odd order, so V = M (+) T canonically and the projection onto
    # the fixed space T is the averaging map, which over F_2 is just the sum
    # of the p translates.
    def proj(v):
        out, u = 0, v
        for _ in range(p):
            out ^= u
            u = sig(u)
        return out

    assert all(proj(g) == g for g in F), "projector wrong on the fixed space"
    layer = {i: proj(reps[i]) for i in range(len(reps))}
    lays = sorted(set(layer.values()))
    nlay = len(lays)
    counts = {t: 0 for t in lays}
    for i in range(len(reps)):
        counts[layer[i]] += 1
    L = min(counts.values())
    assert L == max(counts.values()), f"layers uneven: {sorted(counts.values())}"
    assert nlay == len(F)

    # W = orbits reachable from one orbit's internal sums (all in layer of 0)
    W = 0
    for i in range(len(reps)):
        v, u, hit = reps[i], sig(reps[i]), set()
        for _ in range(p - 1):
            s = v ^ u
            if s not in fset:
                hit.add(oid[s])
            u = sig(u)
        W = max(W, len(hit))

    print(f"r={r} p={p} c={c} orbits={len(reps)} layers={nlay} "
          f"orbits-per-layer L={L} max-internal W={W}")
    print(f"{'k':>3} {'m':>4} {'C(k,2)':>7} {'need':>6}  verdict")
    for k in range(n // p + 1):
        m = n - p * k
        if not (0 <= m <= len(fixed)):
            continue
        # a cross-free layer t != 0 holds at most k covered orbits (one per
        # chosen orbit); layer 0 also gets the internal sums, at most W*k more
        short_nonzero = k < L
        zero_ok = k + W * k >= L
        need = (nlay - 1 if short_nonzero else 0) + (0 if zero_ok else 1)
        verdict = "IMPOSSIBLE" if comb(k, 2) < need else "possible"
        extra = ""
        if verdict == "possible" and short_nonzero and comb(k, 2) == nlay - 1:
            extra = "  (tight: the k layers must be a Sidon set)"
        print(f"{k:>3} {m:>4} {comb(k, 2):>7} {need:>6}  {verdict}{extra}")


if __name__ == "__main__":
    main()
