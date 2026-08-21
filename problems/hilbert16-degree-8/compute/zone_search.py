#!/usr/bin/env python3
"""Haas zone-decomposition search for degree-8 T-curves.

Every maximal T-curve C(T,sigma) arises from a compatible collection S
of Harnack splits whose edges are edges of T (Haas' theorem, as stated
in arXiv:2602.06888 v3 Thm 13), and its sign distribution is then

    sigma  =  eta  +  sum_{S in S} delta_S ,        delta_S in F_2^A

where eta is the Harnack sign distribution and delta_S is the surgical
twist of S (haas.Split.twist).  Hence, on a FIXED triangulation T, every
maximal sign distribution lies in the affine subspace

    eta + span_{F_2} { delta_S : S a Harnack split with edges in T } .

That subspace has rank r <= 26 for the census triangulations, so it can
be swept exhaustively -- which is an exhaustive classification of the
maximal T-curves supported by T, something no random sign search can
give.  Non-maximal members of the subspace are ordinary T-curves too,
and are logged when their scheme is missing from the census.

Input triangulations are always already certified: census triangulations
carry the paper's own integer MIN_WEIGHTS (re-certified exactly by
replay_census.py), random ones come from gen_triang.random_certified_
triangulation.  So every witness logged here is a regular T-curve.

Usage:
  python3 zone_search.py census <shard> <nshards> <log2cap> <out.jsonl>
  python3 zone_search.py random <seed> <ntri> <log2cap> <out.jsonl>
  python3 zone_search.py haas   <seed> <ncoll> <log2cap> <out.jsonl>
  python3 zone_search.py span   <cert-substring> <shard> <nshards> <out.jsonl>

`span` sweeps the ENTIRE affine subspace eta + span{delta_S} of one
census triangulation, sliced across shards.  Because every maximal sign
distribution on that triangulation lies in this subspace, a finished
span sweep is an exhaustive classification of the maximal T-curves that
the triangulation supports.

The `haas` mode drops the regularity requirement: it draws a random
MAXIMAL compatible collection of Harnack splits straight from the
compatibility graph and refines it to an arbitrary unimodular
triangulation.  Haas' theorem needs no regularity, so this samples the
full combinatorial maximal-T-curve space -- an upper bound for the
regular (= algebraic) question.  Witnesses from this mode are flagged
`regular: false` and are NOT dents until a regular refinement with an
exact convexity certificate is found for them.
"""

import json
import pickle
import random
import sys
import time

import haas
from fastcx import Complex

D8 = 8


def edgeset(tris):
    e = set()
    for t in tris:
        tt = [tuple(v) for v in t]
        for i in range(3):
            e.add(frozenset((tt[i], tt[(i + 1) % 3])))
    return e


def delta_bits(s, pts):
    v = 0
    for k, p in enumerate(pts):
        if p in s.zplus and (s.eps + s.ti * p[0] + s.tj * p[1]) % 2:
            v |= 1 << k
    return v


def f2_basis(vs):
    basis = []
    for v in vs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return basis


def sweep(tris, heights, label, splits, out, census, seen, cap, rng,
          stats, shard=0, nshards=1):
    tris = [tuple(tuple(v) for v in t) for t in tris]
    cx = Complex(D8, tris)
    pts = cx.base_pts
    E = edgeset(tris)
    S = [s for s in splits if s.edges <= E]
    if not S:
        return
    basis = f2_basis([delta_bits(s, pts) for s in S])
    r = len(basis)
    eta = haas.eta()
    base = [1 if eta[p] == 0 else -1 for p in pts]
    if r > cap:
        # random cap-dimensional slice of the span, plus a random shift
        rng.shuffle(basis)
        shift = 0
        for b in basis[cap:]:
            if rng.random() < 0.5:
                shift ^= b
        use = basis[:cap]
    else:
        shift, use = 0, basis
    k = len(use)
    lo = (1 << k) * shard // nshards
    hi = (1 << k) * (shard + 1) // nshards
    signs = list(base)
    for j in range(len(pts)):
        if shift >> j & 1:
            signs[j] = -signs[j]
    g0 = lo ^ (lo >> 1)
    for j in range(len(pts)):
        pass
    acc = 0
    for i in range(k):
        if g0 >> i & 1:
            acc ^= use[i]
    for j in range(len(pts)):
        if acc >> j & 1:
            signs[j] = -signs[j]
    prev = g0
    for m in range(lo, hi):
        g = m ^ (m >> 1)
        diff = g ^ prev
        while diff:
            low = diff & -diff
            b = use[low.bit_length() - 1]
            for j in range(len(pts)):
                if b >> j & 1:
                    signs[j] = -signs[j]
            diff ^= low
        prev = g
        nc, sch = cx.eval(signs)
        stats["evals"] += 1
        if sch is None:
            continue
        key = sch
        novel = sch not in census
        if novel:
            stats["new_evals"] += 1
        if nc == 22:
            stats["maximal_evals"] += 1
        if key in seen:
            continue
        seen.add(key)
        if not (novel or nc == 22):
            continue
        rec = {"kind": "NEW" if novel else "MAX", "scheme": sch,
               "ncomp": nc, "tri": label, "rank": r, "nsplits": len(S),
               "sweep_index": m,
               "regular": heights is not None,
               "triangles": [[list(v) for v in t] for t in tris],
               "heights": None if heights is None else
                          {f"{p[0]},{p[1]}": int(v)
                           for p, v in heights.items()},
               "signs": {f"{pts[j][0]},{pts[j][1]}": signs[j]
                         for j in range(len(pts))}}
        out.write(json.dumps(rec) + "\n")
        out.flush()
        stats["logged"] += 1


def main():
    mode = sys.argv[1]
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    stats = {"evals": 0, "new_evals": 0, "maximal_evals": 0,
             "logged": 0, "tris": 0}
    seen = set()
    t0 = time.time()
    if mode == "census":
        shard, nshards, cap = (int(sys.argv[2]), int(sys.argv[3]),
                               int(sys.argv[4]))
        out = open(sys.argv[5], "w")
        ct = pickle.load(open("census_tris.pkl", "rb"))
        items = sorted(ct.items())
        rng = random.Random(1000 + shard)
        for i, (k, (tris, heights, name)) in enumerate(items):
            if i % nshards != shard:
                continue
            stats["tris"] += 1
            sweep(tris, heights, name, splits, out, census, seen, cap,
                  rng, stats)
    elif mode == "spanall":
        shard, nshards, maxrank = (int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]))
        out = open(sys.argv[5], "w")
        import tarfile
        from replay_census import parse_pcom, ARCHIVE
        tar = tarfile.open(ARCHIVE)
        todo = [d for d in json.load(open("span_tasks.json"))
                if d["rank"] <= maxrank]
        for i, d in enumerate(todo):
            if i % nshards != shard:
                continue
            tris, hfrac, _s, _c = parse_pcom(
                tar.extractfile(d["cert"]).read().decode())
            before = stats["evals"]
            sweep(tris, {p: int(v) for p, v in hfrac.items()}, d["cert"],
                  splits, out, census, seen, 99, random.Random(i), stats)
            stats["tris"] += 1
            out.write(json.dumps(
                {"kind": "tri_done", "cert": d["cert"], "rank": d["rank"],
                 "nsplits": d["nsplits"],
                 "evals": stats["evals"] - before}) + "\n")
            out.flush()
    elif mode == "span":
        sub, shard, nshards = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        out = open(sys.argv[5], "w")
        import tarfile
        from replay_census import parse_pcom, ARCHIVE
        tar = tarfile.open(ARCHIVE)
        hits = [n for n in tar.getnames() if n.endswith(sub + ".pcom")]
        if len(hits) != 1:
            raise SystemExit(f"{len(hits)} certificates match {sub!r}")
        name = hits[0]
        tris, hfrac, _sg, _cl = parse_pcom(
            tar.extractfile(name).read().decode())
        heights = {p: int(v) for p, v in hfrac.items()}
        stats["tris"] = 1
        sweep(tris, heights, name, splits, out, census, seen, 99,
              random.Random(shard), stats, shard, nshards)
    elif mode == "haas":
        seed, ncoll, cap = (int(sys.argv[2]), int(sys.argv[3]),
                            int(sys.argv[4]))
        out = open(sys.argv[5], "w")
        adj = pickle.load(open("haas_adj.pkl", "rb"))["adj"]
        n = len(splits)
        rng = random.Random(seed)
        for i in range(ncoll):
            order = list(range(n))
            rng.shuffle(order)
            cur, mask = [], (1 << n) - 1
            for v in order:
                if mask >> v & 1:
                    cur.append(v)
                    mask &= adj[v]
            coll = [splits[v] for v in cur]
            try:
                tris = haas.refine(coll, rng)
            except ValueError:
                continue
            if len(tris) != 64:
                continue
            stats["tris"] += 1
            sweep(tris, None, f"haas-{seed}-{i}", splits, out, census,
                  seen, cap, rng, stats)
    else:
        seed, ntri, cap = (int(sys.argv[2]), int(sys.argv[3]),
                           int(sys.argv[4]))
        out = open(sys.argv[5], "w")
        from gen_triang import random_certified_triangulation
        rng = random.Random(seed)
        for i in range(ntri):
            got = random_certified_triangulation(
                D8, rng, noise_num=rng.choice([1, 1, 2, 3, 5, 8, 13]),
                noise_den=rng.choice([50, 20, 10, 5, 3]))
            if got is None:
                continue
            tris, heights = got
            stats["tris"] += 1
            sweep(tris, {p: int(v) for p, v in heights.items()},
                  f"random-{seed}-{i}", splits, out, census, seen, cap,
                  rng, stats)
    stats["seconds"] = round(time.time() - t0, 1)
    stats["distinct_schemes"] = len(seen)
    out.write(json.dumps({"kind": "summary", **stats}) + "\n")
    out.close()
    print(sys.argv[-1], stats)


if __name__ == "__main__":
    main()
