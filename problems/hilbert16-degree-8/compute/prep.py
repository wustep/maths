#!/usr/bin/env python3
"""Build the derived inputs that zone_search.py needs.

Writes (all gitignored, all cheap to rebuild):
  haas_adj.pkl     compatibility graph of the 1,254 Harnack splits
  census_tris.pkl  the 184 distinct triangulations of deg8.pcoms.txz
  span_tasks.json  one entry per distinct census triangulation, with the
                   number of Harnack splits it carries and the F_2 rank
                   of their surgical twists (= log2 of the size of its
                   maximal-T-curve stratum), sorted by rank

and, committed, certs/mcert_collections.json: for each of the 38
published 22-oval certificates, an explicit collection of Harnack
splits whose surgical twists carry the Harnack sign distribution to
that certificate's signs -- the direct check of Haas' theorem against
the paper's data.

Usage: python3 prep.py
"""

import hashlib
import json
import os
import pickle
import tarfile

import haas
from replay_census import parse_pcom, ARCHIVE


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


def f2_reduce(vs):
    """Row-reduce, keeping the subset mask that produced each pivot."""
    basis = []
    for i, v in enumerate(vs):
        m = 1 << i
        for bv, bm in basis:
            if v ^ bv < v:
                v, m = v ^ bv, m ^ bm
        if v:
            basis.append((v, m))
            basis.sort(key=lambda t: -t[0])
    return basis


def solve(target, vs):
    basis = f2_reduce(vs)
    t, um = target, 0
    for bv, bm in basis:
        if t ^ bv < t:
            t, um = t ^ bv, um ^ bm
    return um if t == 0 else None


def main():
    splits = haas.all_splits()
    pts = haas.PTS
    n = len(splits)
    print(f"{n} Harnack splits")

    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if haas.compatible(splits[i], splits[j]):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    pickle.dump({"paths": [s.path for s in splits], "adj": adj},
                open("haas_adj.pkl", "wb"))
    print(f"{sum(bin(a).count('1') for a in adj) // 2} compatible pairs")

    DB = [delta_bits(s, pts) for s in splits]
    eta = haas.eta()
    etab = 0
    for k, p in enumerate(pts):
        if eta[p]:
            etab |= 1 << k

    tar = tarfile.open(ARCHIVE)
    names = sorted(x for x in tar.getnames() if x.endswith(".pcom"))
    tris_by_key, tasks, mcerts = {}, [], {}
    for nm in names:
        tris, hfrac, signs, claimed = parse_pcom(
            tar.extractfile(nm).read().decode())
        key = hashlib.sha1(json.dumps(
            sorted(sorted(map(tuple, tr)) for tr in tris)).encode()
        ).hexdigest()[:12]
        E = edgeset(tris)
        idx = [i for i, s in enumerate(splits) if s.edges <= E]
        if key not in tris_by_key:
            tris_by_key[key] = (tris, {p: int(v) for p, v in hfrac.items()},
                                nm)
            tasks.append({"cert": nm, "rank": len(f2_reduce([DB[i]
                                                             for i in idx])),
                          "nsplits": len(idx)})
        if "/o22-" not in nm:
            continue
        sb = 0
        for k, p in enumerate(pts):
            if signs[p] == -1:
                sb |= 1 << k
        for e in (0, 1):
            for a in (0, 1):
                for b in (0, 1):
                    tb = 0
                    for k, p in enumerate(pts):
                        if (sb >> k & 1) ^ e ^ (a * p[0] % 2) \
                                ^ (b * p[1] % 2):
                            tb |= 1 << k
                    m = solve(tb ^ etab, [DB[i] for i in idx])
                    if m is None:
                        continue
                    mcerts[claimed] = {
                        "cert": nm, "nsplits": len(idx),
                        "sign_equivalence": {"eps": e, "i": a, "j": b},
                        "collection": [list(map(list, splits[idx[k]].path))
                                       for k in range(len(idx))
                                       if m >> k & 1]}
                    break
                if claimed in mcerts:
                    break
            if claimed in mcerts:
                break
    tasks.sort(key=lambda d: d["rank"])
    pickle.dump(tris_by_key, open("census_tris.pkl", "wb"))
    json.dump(tasks, open("span_tasks.json", "w"), indent=0)
    os.makedirs("certs", exist_ok=True)
    json.dump(mcerts, open("certs/mcert_collections.json", "w"), indent=1)
    n22 = sum(1 for x in names if "/o22-" in x)
    print(f"{len(tris_by_key)} distinct triangulations, "
          f"ranks {tasks[0]['rank']}-{tasks[-1]['rank']}")
    print(f"Haas collections recovered for {len(mcerts)}/{n22} "
          f"published 22-oval certificates")


if __name__ == "__main__":
    main()
