#!/usr/bin/env python3
"""Search Haas-collection space for the two open deep nests.

  <4 u 1<2 u 1<14>>>   and   <14 u 1<2 u 1<4>>>     (22 ovals, (p,n)=(19,3))

Everything here works with COLLECTIONS of Harnack splits, not with sign
vectors on a fixed triangulation.  Haas' theorem (see deepnest.py) makes
the real scheme a function of the collection alone, so this is a search
over the combinatorics that produces the nesting, and each candidate
carries its own (designed) triangulation as a by-product.

Modes
  nbhd   <out.jsonl>              all one-split moves (add / drop / swap)
                                  around each of the 38 published 22-oval
                                  collections  -- exhaustive, deterministic
  ladder <out.jsonl>              two-split moves around the depth-3
                                  seeds only (the ladder rungs)
  beam   <seed> <minutes> <out>   width-limited best-first growth toward
                                  the target shape
  anneal <seed> <minutes> <out>   simulated annealing on collections
  pairs  <shard> <n> <out>        exhaustive over all compatible pairs

Every distinct scheme is logged once with the collection that produced
it; schemes outside census+17 are flagged NEW (they still need a regular
refinement -- dn_regular.py -- before they are T-curves).
"""

import json
import random
import sys
import time
from collections import defaultdict

import deepnest as dn
from dn_charac import shape, nest_depth

TARGETS = [(4, 2, 14), (14, 2, 4)]


def known_schemes():
    ks = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    assert len(ks) == 2367
    for c in json.load(open("certs/new_schemes.json")):
        ks.add(c["scheme"])
    return ks


def seed_collections():
    """(name, [split]) for each of the 38 published 22-oval certificates."""
    sp = dn.splits()
    key = {x.key: x for x in sp}
    idx = {x.key: i for i, x in enumerate(sp)}
    out = []
    for claimed, rec in sorted(json.load(
            open("certs/mcert_collections.json")).items()):
        ids = []
        ok = True
        for p in rec["collection"]:
            t = tuple(tuple(v) for v in p)
            k = t if t[0] < t[-1] else t[::-1]
            if k not in key:
                ok = False
                break
            ids.append(idx[k])
        if ok:
            out.append((claimed, sorted(ids)))
    return out


def score(nc, sch):
    """lower is better; 0 == a target."""
    if sch is None:
        return 1000.0
    a, b, c, junk = shape(sch)
    best = min(abs(a - ta) + abs(b - tb) + abs(c - tc)
               for ta, tb, tc in TARGETS)
    return 3.0 * (22 - nc) + best + 2.0 * junk


class Log:
    def __init__(self, path, known):
        self.f = open(path, "w")
        self.known = known
        self.seen = {}
        self.new = 0
        self.best = (1e9, None, None)
        self.evals = 0

    def add(self, ids, nc, sch, mode):
        self.evals += 1
        sc = score(nc, sch)
        if sc < self.best[0]:
            self.best = (sc, sch, list(ids))
            self.f.write(json.dumps(
                {"kind": "best", "score": sc, "scheme": sch, "ncomp": nc,
                 "collection": list(ids), "mode": mode}) + "\n")
            self.f.flush()
        if sch is None or sch in self.seen:
            return sc
        self.seen[sch] = list(ids)
        novel = sch not in self.known
        if novel:
            self.new += 1
        a, b, c, j = shape(sch)
        rec = {"kind": "NEW" if novel else "scheme", "scheme": sch,
               "ncomp": nc, "shape": [a, b, c, j],
               "depth": nest_depth(sch), "collection": list(ids),
               "mode": mode}
        self.f.write(json.dumps(rec) + "\n")
        self.f.flush()
        return sc

    def close(self, extra):
        self.f.write(json.dumps({"kind": "summary", "evals": self.evals,
                                 "distinct": len(self.seen),
                                 "new": self.new,
                                 "best_score": self.best[0],
                                 "best_scheme": self.best[1],
                                 **extra}) + "\n")
        self.f.close()


def ev(sp, ids, rng=None):
    try:
        return dn.evaluate([sp[i] for i in ids], rng)[:2]
    except ValueError:
        return 0, None


def run_nbhd(out):
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    seeds = seed_collections()
    t0 = time.time()
    for name, ids in seeds:
        mask = (1 << len(sp)) - 1
        for i in ids:
            mask &= adj[i] | (1 << i)
        # drop
        for k in range(len(ids)):
            sub = ids[:k] + ids[k + 1:]
            nc, s = ev(sp, sub)
            lg.add(sub, nc, s, f"drop/{name}")
        # add
        for j in range(len(sp)):
            if j in ids or not (mask >> j) & 1:
                continue
            new = sorted(ids + [j])
            nc, s = ev(sp, new)
            lg.add(new, nc, s, f"add/{name}")
        # swap
        for k in range(len(ids)):
            sub = ids[:k] + ids[k + 1:]
            m2 = (1 << len(sp)) - 1
            for i in sub:
                m2 &= adj[i] | (1 << i)
            for j in range(len(sp)):
                if j in sub or not (m2 >> j) & 1:
                    continue
                new = sorted(sub + [j])
                nc, s = ev(sp, new)
                lg.add(new, nc, s, f"swap/{name}")
        print(f"  {name}: {lg.evals} evals, {len(lg.seen)} schemes, "
              f"{lg.new} new, best {lg.best[0]} {lg.best[1]} "
              f"({time.time()-t0:.0f}s)", flush=True)
    lg.close({"mode": "nbhd"})
    print(f"nbhd: {lg.evals} evals, {len(lg.seen)} schemes, {lg.new} new")


def run_ladder(out, seconds=3600):
    """Two-split moves around the twelve depth-3 seeds."""
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    seeds = [(n, i) for n, i in seed_collections()
             if nest_depth(n.replace("v", " u ").replace("<", "<")) or True]
    # keep only depth-3 schemes
    keep = []
    for name, ids in seeds:
        nc, s = ev(sp, ids)
        if s is not None and nest_depth(s) >= 3:
            keep.append((name, ids, s))
    print(f"{len(keep)} depth-3 seeds")
    t0 = time.time()
    for name, ids, s0 in keep:
        n = len(sp)
        # drop one, add two
        for k in range(len(ids) + 1):
            sub = ids if k == len(ids) else ids[:k] + ids[k + 1:]
            m = (1 << n) - 1
            for i in sub:
                m &= adj[i] | (1 << i)
            cand = [j for j in range(n) if (m >> j) & 1 and j not in sub]
            for x in range(len(cand)):
                jx = cand[x]
                mx = m & adj[jx]
                for y in range(x + 1, len(cand)):
                    jy = cand[y]
                    if not (mx >> jy) & 1:
                        continue
                    new = sorted(sub + [jx, jy])
                    nc, s = ev(sp, new)
                    lg.add(new, nc, s, f"add2/{name}")
                if time.time() - t0 > seconds:
                    break
            if time.time() - t0 > seconds:
                break
        print(f"  {name} ({s0}): {lg.evals} evals, {len(lg.seen)} schemes,"
              f" {lg.new} new, best {lg.best[0]} {lg.best[1]}"
              f" ({time.time()-t0:.0f}s)", flush=True)
        if time.time() - t0 > seconds:
            break
    lg.close({"mode": "ladder"})


def run_beam(seedno, minutes, out, width=40, depth=14):
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    rng = random.Random(seedno)
    n = len(sp)
    deadline = time.time() + minutes * 60
    starts = [ids for _, ids in seed_collections()]
    starts.append([])
    frontier = []
    for ids in starts:
        nc, s = ev(sp, ids)
        frontier.append((lg.add(ids, nc, s, "beam0"), tuple(ids)))
    seen_coll = {tuple(x[1]) for x in frontier}
    for d in range(depth):
        cand = []
        for sc, ids in frontier:
            m = (1 << n) - 1
            for i in ids:
                m &= adj[i] | (1 << i)
            pool = [j for j in range(n) if (m >> j) & 1 and j not in ids]
            rng.shuffle(pool)
            moves = [sorted(list(ids) + [j]) for j in pool]
            moves += [sorted(list(ids)[:k] + list(ids)[k + 1:])
                      for k in range(len(ids))]
            for nw in moves:
                t = tuple(nw)
                if t in seen_coll:
                    continue
                seen_coll.add(t)
                nc, s = ev(sp, nw)
                cand.append((lg.add(nw, nc, s, f"beam{d}"), t))
                if time.time() > deadline:
                    break
            if time.time() > deadline:
                break
        if not cand:
            break
        cand.sort(key=lambda x: (x[0], len(x[1])))
        frontier = cand[:width]
        print(f"  depth {d}: {lg.evals} evals, {len(lg.seen)} schemes, "
              f"{lg.new} new, best {lg.best[0]} {lg.best[1]}", flush=True)
        if time.time() > deadline:
            break
    lg.close({"mode": "beam", "seed": seedno})


def run_anneal(seedno, minutes, out):
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    rng = random.Random(seedno)
    n = len(sp)
    deadline = time.time() + minutes * 60
    starts = [ids for _, ids in seed_collections()] + [[]]
    rounds = 0
    while time.time() < deadline:
        rounds += 1
        ids = list(starts[rng.randrange(len(starts))])
        nc, s = ev(sp, ids)
        e = lg.add(ids, nc, s, "anneal")
        steps = 3000
        for step in range(steps):
            if step % 128 == 0 and time.time() > deadline:
                break
            T = 3.0 * (0.03 / 3.0) ** (step / steps)
            m = (1 << n) - 1
            for i in ids:
                m &= adj[i] | (1 << i)
            r = rng.random()
            if r < 0.45 or not ids:
                pool = [j for j in range(n) if (m >> j) & 1 and j not in ids]
                if not pool:
                    continue
                nw = sorted(ids + [rng.choice(pool)])
            elif r < 0.75:
                k = rng.randrange(len(ids))
                nw = ids[:k] + ids[k + 1:]
            else:
                k = rng.randrange(len(ids))
                sub = ids[:k] + ids[k + 1:]
                m2 = (1 << n) - 1
                for i in sub:
                    m2 &= adj[i] | (1 << i)
                pool = [j for j in range(n) if (m2 >> j) & 1 and j not in sub]
                if not pool:
                    continue
                nw = sorted(sub + [rng.choice(pool)])
            nc2, s2 = ev(sp, nw)
            e2 = lg.add(nw, nc2, s2, "anneal")
            if e2 <= e or rng.random() < pow(2.718281828, (e - e2) / T):
                ids, e = nw, e2
    lg.close({"mode": "anneal", "seed": seedno, "rounds": rounds})


def run_rand(seedno, minutes, out):
    """Uniform-ish random MAXIMAL compatible collections: the widest net
    over the combinatorial (non-regular) maximal-T-curve space."""
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    rng = random.Random(seedno)
    n = len(sp)
    deadline = time.time() + minutes * 60
    sizes = defaultdict(int)
    while time.time() < deadline:
        order = list(range(n))
        rng.shuffle(order)
        cur, mask = [], (1 << n) - 1
        for v in order:
            if (mask >> v) & 1:
                cur.append(v)
                mask &= adj[v]
        cur.sort()
        nc, s = ev(sp, cur)
        lg.add(cur, nc, s, "rand")
        sizes[len(cur)] += 1
    lg.close({"mode": "rand", "seed": seedno,
              "sizes": dict(sorted(sizes.items()))})
    print(f"rand {seedno}: {lg.evals} evals, {len(lg.seen)} schemes, "
          f"{lg.new} new")


def run_family(seedno, minutes, out):
    """Annealing that *pins the shape to the family* <a u 1<2 u 1<c>>>
    and then drives a from 17 (realized) toward 14 (the open scheme).

    Rationale: the census realizes the b=2 rungs a=17,c=1 and a=10,c=8;
    every a strictly between is absent, and a=14 is one of the two
    algebraically open M-schemes.  So the family is the corridor.
    """
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    rng = random.Random(seedno)
    n = len(sp)
    deadline = time.time() + minutes * 60

    def energy(nc, sch):
        if sch is None:
            return 500.0
        a, b, c, junk = shape(sch)
        return 8.0 * abs(b - 2) + 6.0 * junk + 1.0 * abs(a - 14) \
            + 3.0 * (22 - nc)

    # seeds: the 12 depth-3 singletons, plus the census depth-3 collections
    starts = [[i] for i, x in enumerate(sp)]
    rng.shuffle(starts)
    starts = starts[:200] + [ids for _, ids in seed_collections()]
    rounds = 0
    while time.time() < deadline:
        rounds += 1
        ids = list(starts[rng.randrange(len(starts))])
        nc, s = ev(sp, ids)
        lg.add(ids, nc, s, "family")
        e = energy(nc, s)
        steps = 2500
        for step in range(steps):
            if step % 128 == 0 and time.time() > deadline:
                break
            T = 4.0 * (0.05 / 4.0) ** (step / steps)
            m = (1 << n) - 1
            for i in ids:
                m &= adj[i] | (1 << i)
            r = rng.random()
            if r < 0.5 or not ids:
                pool = [j for j in range(n) if (m >> j) & 1 and j not in ids]
                if not pool:
                    continue
                nw = sorted(ids + [rng.choice(pool)])
            elif r < 0.8:
                k = rng.randrange(len(ids))
                nw = ids[:k] + ids[k + 1:]
            else:
                k = rng.randrange(len(ids))
                sub = ids[:k] + ids[k + 1:]
                m2 = (1 << n) - 1
                for i in sub:
                    m2 &= adj[i] | (1 << i)
                pool = [j for j in range(n) if (m2 >> j) & 1 and j not in sub]
                if not pool:
                    continue
                nw = sorted(sub + [rng.choice(pool)])
            nc2, s2 = ev(sp, nw)
            lg.add(nw, nc2, s2, "family")
            e2 = energy(nc2, s2)
            if e2 <= e or rng.random() < pow(2.718281828, (e - e2) / T):
                ids, e = nw, e2
    lg.close({"mode": "family", "seed": seedno, "rounds": rounds})
    print(f"family {seedno}: {lg.evals} evals, {len(lg.seen)} schemes, "
          f"{lg.new} new")


def run_pairs(shard, nshards, out):
    sp = dn.splits()
    adj = dn.compat_matrix()
    lg = Log(out, known_schemes())
    n = len(sp)
    k = 0
    for i in range(n):
        ai = adj[i]
        for j in range(i + 1, n):
            if not (ai >> j) & 1:
                continue
            k += 1
            if k % nshards != shard:
                continue
            nc, s = ev(sp, [i, j])
            lg.add([i, j], nc, s, "pair")
    lg.close({"mode": "pairs", "shard": shard, "nshards": nshards})
    print(f"pairs shard {shard}: {lg.evals} evals, {len(lg.seen)} schemes,"
          f" {lg.new} new")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "nbhd":
        run_nbhd(sys.argv[2])
    elif m == "ladder":
        run_ladder(sys.argv[2], float(sys.argv[3]) * 60)
    elif m == "beam":
        run_beam(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif m == "anneal":
        run_anneal(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif m == "pairs":
        run_pairs(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif m == "rand":
        run_rand(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif m == "family":
        run_family(int(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    else:
        raise SystemExit(__doc__)
