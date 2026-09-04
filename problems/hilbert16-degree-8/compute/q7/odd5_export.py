#!/usr/bin/env python3
"""Export the q5 odd-split graph and twists for the C size-5 sweep."""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import haas


def words(mask: int, nwords: int):
    return [(mask >> (64 * k)) & ((1 << 64) - 1)
            for k in range(nwords)]


def per_first_size5(odds, adj):
    per = []
    for a, i in enumerate(odds):
        ai = adj[i]
        cand = [odds[b] for b in range(a + 1, len(odds))
                if (ai >> odds[b]) & 1]
        count = 0
        for x, j in enumerate(cand):
            mj = ai & adj[j]
            c2 = [cand[y] for y in range(x + 1, len(cand))
                  if (mj >> cand[y]) & 1]
            for y, k in enumerate(c2):
                mk = mj & adj[k]
                c3 = [c2[z] for z in range(y + 1, len(c2))
                      if (mk >> c2[z]) & 1]
                for z, ell in enumerate(c3):
                    ml = mk & adj[ell]
                    count += sum(1 for p in c3[z + 1:]
                                 if (ml >> p) & 1)
        per.append(count)
    return per


def main():
    pts = haas.PTS
    pidx = {p: i for i, p in enumerate(pts)}
    pairs = haas.PAIRS
    pair_idx = {frozenset(e): i for i, e in enumerate(pairs)}
    cross = dn.cross_masks()
    splits = dn.splits()
    adj = dn.compat_matrix()
    odds = [i for i, s in enumerate(splits) if not s.even]
    npw = (len(pairs) + 63) // 64
    now = (len(odds) + 63) // 64
    eta = haas.signs_of([])
    per = per_first_size5(odds, adj)
    assert sum(per) == 37_632_123

    dest = HERE / "work" / "odd5.task"
    dest.parent.mkdir(exist_ok=True)
    with dest.open("w") as f:
        print(len(pts), len(pairs), len(splits), len(odds), npw, now,
              file=f)
        print(*(eta[p] for p in pts), file=f)
        for x, y in pts:
            print(x, y, file=f)
        for (u, v), mask in zip(pairs, cross):
            print(pidx[u], pidx[v], *(f"{w:016x}" for w in words(mask, npw)),
                  file=f)
        for s in splits:
            edges = sorted(pair_idx[e] for e in s.edges)
            edges += [-1] * (2 - len(edges))
            one = haas.signs_of([s])
            twist = sum(1 << k for k, p in enumerate(pts)
                        if one[p] != eta[p])
            print(len(s.edges), edges[0], edges[1], f"{twist:016x}",
                  int(s.even), file=f)
        print(*odds, file=f)
        pos = {sid: k for k, sid in enumerate(odds)}
        for sid in odds:
            mask = 0
            for other in odds:
                if (adj[sid] >> other) & 1:
                    mask |= 1 << pos[other]
            print(*(f"{w:016x}" for w in words(mask, now)), file=f)
        print(*per, file=f)
    print(f"wrote {dest.relative_to(ROOT)}: {sum(per)} tuples")


if __name__ == "__main__":
    main()
