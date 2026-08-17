#!/usr/bin/env python3
"""Greedy hitting set for T-term APs. Upper bound on H(p,T), hence on the
size needed to force max_d g < T. If H(p, C*sqrt(p)) <= sqrt(p), then G < C sqrt(p).
"""

from __future__ import annotations

import argparse
import json

from gaplib import max_gap_dilates, primes_upto


def greedy_hitting(p: int, T: int) -> list[int]:
    """Vertices 0..p-1. Hyperedges: T-APs. Greedy by number of uncovered edges."""
    # uncovered[d][s] = True if the AP start s, diff d is still unhit
    # There are p-1 diffs and p starts. Use a flat array.
    # For speed: for each residue x, list of (d,s) APs containing x.
    # AP (s,d) = {s + j d : j=0..T-1}
    n_e = (p - 1) * p
    # live edges as set of ids id = (d-1)*p + s
    live = set(range(n_e))

    def edges_through(x: int):
        out = []
        for d in range(1, p):
            inv = pow(d, p - 2, p)
            # x = s + j d ⇒ s = x - j d, j=0..T-1
            for j in range(T):
                s = (x - j * d) % p
                out.append((d - 1) * p + s)
        return out

    # Precompute incidence
    inc = [edges_through(x) for x in range(p)]
    selected = []
    unused = set(range(p))
    while live:
        best_x = None
        best_c = -1
        for x in unused:
            c = 0
            for e in inc[x]:
                if e in live:
                    c += 1
            if c > best_c:
                best_c = c
                best_x = x
        if best_x is None or best_c == 0:
            break
        selected.append(best_x)
        unused.remove(best_x)
        for e in inc[best_x]:
            live.discard(e)
    return selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pmax", type=int, default=47)
    args = ap.parse_args()
    rows = []
    for p in primes_upto(args.pmax):
        if p < 11:
            continue
        n = max(2, int(round(p**0.5)))
        for c in (2.0, 2.5, 3.0, 3.5):
            T = max(2, int(round(c * (p**0.5))))
            if T >= p:
                continue
            A = greedy_hitting(p, T)
            g, d = max_gap_dilates(A, p)
            rec = {
                "p": p,
                "T": T,
                "c_target": c,
                "H_greedy": len(A),
                "sqrtp": p**0.5,
                "g_of_greedy": g,
                "beats_sqrt": len(A) <= n,
            }
            rows.append(rec)
            print(
                f"p={p:3d} T={T:3d} c={c:.1f} |A|={len(A):3d} n~{n:2d} "
                f"g(A)={g:3d} H<=sqrt={len(A)<=n}",
                flush=True,
            )
    with open("compute/certs/greedy_hit.json", "w") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    main()
