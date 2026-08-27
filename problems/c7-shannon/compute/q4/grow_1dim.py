#!/usr/bin/env python3
"""Harder local search for 53 cosets on a few 1-dimensional quotients.

Replays the generators that produced the C census best (43). Writes a
371-set if a 53-pack appears.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from c7_common import encode, format_word

QN = 2401
TARGET = 53
CUBE = []
for o0 in range(-1, 2):
    for o1 in range(-1, 2):
        for o2 in range(-1, 2):
            for o3 in range(-1, 2):
                for o4 in range(-1, 2):
                    CUBE.append((o0, o1, o2, o3, o4))


def pack4(x):
    return ((x[0] * 7 + x[1]) * 7 + x[2]) * 7 + x[3]


def cid_of(c, g, pivot):
    s = c[pivot]
    x = [(c[i] - s * g[i]) % 7 for i in range(5)]
    rest = [x[i] for i in range(5) if i != pivot]
    return pack4(rest)


def add4(a, b):
    a0, a1, a2, a3 = a // 343, (a // 49) % 7, (a // 7) % 7, a % 7
    b0, b1, b2, b3 = b // 343, (b // 49) % 7, (b // 7) % 7, b % 7
    return ((a0 + b0) % 7) * 343 + ((a1 + b1) % 7) * 49 + ((a2 + b2) % 7) * 7 + (
        a3 + b3
    ) % 7


def build_conn(g, pivot):
    conn = set()
    for s in range(7):
        for cub in CUBE:
            c = tuple((s * g[i] + cub[i]) % 7 for i in range(5))
            conn.add(cid_of(c, g, pivot))
    conn.discard(0)
    return conn


def neigh_list(conn):
    clist = list(conn)
    adj = [set() for _ in range(QN)]
    for i in range(QN):
        for d in clist:
            adj[i].add(add4(i, d))
    return adj


def greedy(adj, rng):
    order = list(range(QN))
    rng.shuffle(order)
    used = [False] * QN
    taken = []
    for v in order:
        if used[v]:
            continue
        taken.append(v)
        used[v] = True
        for u in adj[v]:
            used[u] = True
    return taken


def eject(adj, S, rng, steps=3000):
    blocked = [0] * QN
    inset = set(S)
    for v in S:
        blocked[v] += 1
        for u in adj[v]:
            blocked[u] += 1
    for _ in range(steps):
        if not S:
            break
        v = rng.choice(S)
        S.remove(v)
        inset.remove(v)
        blocked[v] -= 1
        for u in adj[v]:
            blocked[u] -= 1
        free = [u for u in range(QN) if blocked[u] == 0]
        rng.shuffle(free)
        packed = []
        banned = set()
        for u in free:
            if u in banned:
                continue
            packed.append(u)
            banned.add(u)
            banned.update(adj[u])
        if len(S) + len(packed) >= len(inset):
            for u in packed:
                S.append(u)
                inset.add(u)
                blocked[u] += 1
                for w in adj[u]:
                    blocked[w] += 1
        else:
            S.append(v)
            inset.add(v)
            blocked[v] += 1
            for u in adj[v]:
                blocked[u] += 1
    return S


def expand(cids, g, pivot):
    words = []
    rest_idx = [i for i in range(5) if i != pivot]
    for cid in cids:
        rest = [cid // 343, (cid // 49) % 7, (cid // 7) % 7, cid % 7]
        rep = [0] * 5
        for t, i in enumerate(rest_idx):
            rep[i] = rest[t]
        for s in range(7):
            words.append(encode((rep[i] + s * g[i]) % 7 for i in range(5)))
    return words


def hunt(g, pivot, trials=40):
    t0 = time.time()
    conn = build_conn(g, pivot)
    adj = neigh_list(conn)
    print(f"g={g} pivot={pivot} deg={len(conn)}", flush=True)
    best = []
    rng = random.Random(1)
    for t in range(trials):
        S = greedy(adj, rng)
        S = eject(adj, S, rng)
        if len(S) > len(best):
            best = list(S)
            print(f"  pack={len(best)} trial={t} t={time.time()-t0:.1f}s", flush=True)
            if len(best) >= TARGET:
                words = expand(best, g, pivot)
                out = HERE / f"R{len(words)}_1dim.txt"
                out.write_text("\n".join(format_word(v) for v in words) + "\n")
                print(f"wrote {out}")
                return len(best)
    print(f"done best={len(best)} t={time.time()-t0:.1f}s")
    return len(best)


def main():
    gens = [
        ((1, 1, 5, 1, 0), 0),
        ((1, 4, 2, 0, 0), 0),
        ((1, 6, 2, 1, 0), 0),
        ((0, 1, 2, 3, 4), 1),
        ((0, 0, 1, 2, 4), 2),
    ]
    best = 0
    for g, p in gens:
        best = max(best, hunt(g, p))
    print(f"ALL best_pack={best}")


if __name__ == "__main__":
    main()
