#!/usr/bin/env python3
"""Build worker task files for nest_search.py.

Seed selection (all from the replayed census archive):
  * every certificate on the four "deep-nest" triangulations (the ones
    that produced <10 u 1<2 u 1<8>>>, <1 u 1<2 u 1<15>>>,
    <15 u 1<2 u 1<2>>>, <17 u 1<2 u 1<1>>>) with >= 19 ovals,
  * every 22-oval certificate (all 38 M-scheme witnesses),
  * every census certificate anywhere whose scheme is a pure
    <a u 1<b u 1<c>>> with b <= 3 and a+c >= 12 (the family the two
    open schemes live in).

Phases:
  balls    key deep-nest certs radius 4, everything else radius 3
  beams    directed beams from family certs toward missing (a,c) pairs
  windowN  exhaustive 21-bit window over the <10 u 1<2 u 1<8>>> witness
           (bits = union of sign disagreements among the deep-nest
           family on that triangulation, padded), sliced across workers

Usage: python3 make_tasks.py <phase> <nworkers> <outdir>
"""

import hashlib
import json
import os
import sys
import tarfile

from replay_census import parse_pcom, ARCHIVE
from nest_search import profile

KEY_R4 = ["(10v1(2v1(8)))", "(9v1(2v1(8)))", "(10v1(2v1(7)))",
          "(16v1(2v1(1)))", "(15v1(2v1(2)))", "(17v1(2v1(1)))",
          "(1v1(2v1(15)))", "(2v1(1v1(15)))", "(16v3(1))",
          "(17v1(1)v1(2))", "(18v1(3))"]

BEAM_TARGETS = {
    "(10v1(2v1(8)))": [(14, 4), (4, 14), (9, 9), (12, 6), (11, 7)],
    "(9v1(2v1(8)))": [(9, 9), (10, 8)],
    "(10v1(2v1(7)))": [(14, 4), (11, 7)],
    "(16v1(2v1(1)))": [(14, 4), (16, 2)],
    "(15v1(2v1(2)))": [(14, 4), (15, 3)],
    "(17v1(2v1(1)))": [(14, 4), (16, 2)],
    "(1v1(2v1(15)))": [(4, 14), (3, 15), (2, 16)],
    "(2v1(1v1(15)))": [(4, 14), (2, 16)],
}


def canon_scheme_name(path):
    return path.split("/")[-1][:-5]


def load_seeds():
    tar = tarfile.open(ARCHIVE)
    tris_by_key, seeds = {}, {}
    names = [n for n in tar.getnames() if n.endswith(".pcom")]
    # first pass: find the four deep-nest triangulation keys
    keyfor = {}
    parsed = {}
    for n in names:
        raw = tar.extractfile(n).read().decode()
        tris, heights, signs, claimed = parse_pcom(raw)
        k = hashlib.sha1(json.dumps(
            sorted(sorted(map(tuple, tr)) for tr in tris)).encode()
        ).hexdigest()[:12]
        keyfor[n] = k
        parsed[n] = (tris, signs, claimed)
    nest_keys = {keyfor[n] for n in names
                 if canon_scheme_name(n) in ("(10v1(2v1(8)))",
                                             "(1v1(2v1(15)))",
                                             "(15v1(2v1(2)))",
                                             "(17v1(2v1(1)))")}
    for n in names:
        tris, signs, claimed = parsed[n]
        name = canon_scheme_name(n)
        odir = n.split("/")[1]
        ovals = int(odir.split("-")[0][1:])
        a, b, c, junk = profile(claimed)
        pick = (ovals == 22
                or (keyfor[n] in nest_keys and ovals >= 19)
                or (junk == 0 and b <= 3 and a + c >= 12 and c >= 1))
        if not pick:
            continue
        if name in seeds:      # scheme names unique in census
            continue
        tris_by_key.setdefault(keyfor[n], tris)
        seeds[name] = {
            "tri": keyfor[n], "ovals": ovals, "scheme": claimed,
            "signs": {f"{p[0]},{p[1]}": s for p, s in signs.items()},
        }
    return tris_by_key, seeds


def task_of(seed, tris_by_key, **kw):
    t = {"triangles": [[list(v) for v in tr]
                       for tr in tris_by_key[seed["tri"]]],
         "signs": seed["signs"]}
    t.update(kw)
    return t


def ball_size(r, n=45):
    from math import comb
    return sum(comb(n, k) for k in range(r + 1))


def main():
    phase, nw, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    tris_by_key, seeds = load_seeds()
    print(f"{len(seeds)} seeds on {len(set(s['tri'] for s in seeds.values()))} triangulations")

    tasks = []   # (cost, task)
    if phase == "balls":
        for name, seed in seeds.items():
            r = 4 if name in KEY_R4 else 3
            tasks.append((ball_size(r), task_of(
                seed, tris_by_key, mode="ball", radius=r,
                seed_name=name)))
    elif phase == "beams":
        for name, targets in BEAM_TARGETS.items():
            if name not in seeds:
                print(f"beam seed {name} missing!")
                continue
            for tg in targets:
                tasks.append((64 * 45 * 30, task_of(
                    seeds[name], tris_by_key, mode="beam",
                    seed_name=name, target=list(tg), width=64,
                    depth=30)))
        # every strong family seed also gets a generic "grow" beam
        for name, seed in seeds.items():
            if name in BEAM_TARGETS:
                continue
            a, b, c, junk = profile(seed["scheme"])
            if junk == 0 and b in (1, 2, 3) and a + c >= 15:
                tasks.append((48 * 45 * 24, task_of(
                    seed, tris_by_key, mode="beam", seed_name=name,
                    target=[a + 2, c + 2], width=48, depth=24)))
    elif phase.startswith("window"):
        wname = "(10v1(2v1(8)))"
        seed = seeds[wname]
        tri = seed["tri"]
        # active bits: disagreements among >=19-oval certs on this tri
        pts = sorted(tuple(int(x) for x in k.split(","))
                     for k in seed["signs"])
        family = [s for s in seeds.values() if s["tri"] == tri]
        base = seed["signs"]
        active = set()
        for s in family:
            for k in base:
                if s["signs"][k] != base[k]:
                    active.add(tuple(int(x) for x in k.split(",")))
        bits = sorted(active)
        nbits = 21
        if len(bits) > nbits:
            bits = bits[:nbits]
        else:
            for p in pts:
                if len(bits) >= nbits:
                    break
                if p not in active:
                    bits.append(p)
        print(f"window bits ({len(bits)}): {bits}")
        total = 1 << len(bits)
        step = (total + nw - 1) // nw
        for w in range(nw):
            tasks.append((step, task_of(
                seed, tris_by_key, mode="window", seed_name=wname,
                bits=[list(b) for b in bits],
                lo=w * step, hi=min((w + 1) * step, total))))
    else:
        raise SystemExit(f"unknown phase {phase}")

    # balance by cost, largest first
    tasks.sort(key=lambda t: -t[0])
    buckets = [[] for _ in range(nw)]
    load = [0] * nw
    for cost, task in tasks:
        i = load.index(min(load))
        buckets[i].append(task)
        load[i] += cost
    for w in range(nw):
        with open(f"{outdir}/tasks_{phase}_{w}.json", "w") as f:
            json.dump(buckets[w], f)
    print(f"{len(tasks)} tasks, est evals/worker: {sorted(load)}")


if __name__ == "__main__":
    main()
