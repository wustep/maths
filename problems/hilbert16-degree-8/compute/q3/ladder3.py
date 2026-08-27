#!/usr/bin/env python3
"""Three-split moves around the published (19,3) and depth-3 M-collections.

q1 finished the one-split neighbourhood of all 38 M-collections and the
two-split ladder around the twelve depth-3 M-collections.  This is the
next distance: from each seed, drop at most one split and add three
compatible splits.

A hit in collection space is a PL curve, not a T-curve, until
``haas.regularize`` plus exact ``tcurve.check_convexity``.

usage: python3 q3/ladder3.py <out.jsonl> [seconds] [seeds=193|depth3|all]
"""
import json
import os
import sys
import time

from common import boot, known_schemes, resolve_out

boot()

import deepnest as dn
from dn_charac import shape, nest_depth

TARGETS = [(4, 2, 14), (14, 2, 4)]
OPEN = {"<4 u 1<2 u 1<14>>>", "<14 u 1<2 u 1<4>>>"}


def ev(sp, ids):
    try:
        return dn.evaluate([sp[i] for i in ids])[:2]
    except ValueError:
        return 0, None


def score(nc, sch):
    if sch is None:
        return 1000.0
    a, b, c, junk = shape(sch)
    best = min(abs(a - ta) + abs(b - tb) + abs(c - tc)
               for ta, tb, tc in TARGETS)
    return 3.0 * (22 - nc) + best + 2.0 * junk


def seed_collections():
    sp_idx = None
    sp = dn.splits()
    key = {x.key: i for i, x in enumerate(sp)}
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
            ids.append(key[k])
        if ok:
            out.append((claimed, sorted(ids), rec.get("cert", "")))
    return sp, out


def main():
    out = resolve_out(sys.argv[1] if len(sys.argv) > 1 else "dn_out/ladder3.jsonl")
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 7200
    which = sys.argv[3] if len(sys.argv) > 3 else "193"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sp, seeds = seed_collections()
    adj = dn.compat_matrix()
    n = len(sp)
    keep = []
    for name, ids, cert in seeds:
        nc, sch = ev(sp, ids)
        if sch is None:
            continue
        is_193 = "p19-n03" in cert
        is_d3 = nest_depth(sch) >= 3
        if which == "193" and not is_193:
            continue
        if which == "depth3" and not is_d3:
            continue
        if which == "all" and not (is_193 or is_d3):
            continue
        keep.append((name, ids, sch))
    print(f"ladder3 seeds={len(keep)} which={which} seconds={seconds}",
          flush=True)
    known = known_schemes()
    f = open(out, "w")
    seen = {}
    evals = hits = new = 0
    best = (1e9, None)
    t0 = time.time()

    def add(ids, tag):
        nonlocal evals, hits, new, best
        evals += 1
        nc, sch = ev(sp, ids)
        sc = score(nc, sch)
        if sc < best[0]:
            best = (sc, sch)
            f.write(json.dumps({"kind": "best", "score": sc, "scheme": sch,
                                "ncomp": nc, "collection": list(ids),
                                "mode": tag}) + "\n")
            f.flush()
        if sch is None or sch in seen:
            return
        seen[sch] = list(ids)
        rec = {"kind": "scheme", "scheme": sch, "ncomp": nc,
               "shape": list(shape(sch)), "depth": nest_depth(sch),
               "collection": list(ids), "mode": tag}
        if sch in OPEN:
            rec["kind"] = "HIT"
            hits += 1
        if sch not in known:
            rec["kind"] = "NEW"
            new += 1
        f.write(json.dumps(rec) + "\n")
        f.flush()
        if rec["kind"] in ("HIT", "NEW"):
            print(f"  {rec['kind']} {sch}", flush=True)

    for name, ids, s0 in keep:
        add(ids, f"seed/{name}")
        # drop 0 or 1, then add 3 compatible
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
                    my = mx & adj[jy]
                    for z in range(y + 1, len(cand)):
                        jz = cand[z]
                        if not (my >> jz) & 1:
                            continue
                        add(sorted(sub + [jx, jy, jz]), f"add3/{name}")
                    if time.time() - t0 > seconds:
                        break
                if time.time() - t0 > seconds:
                    break
            if time.time() - t0 > seconds:
                break
        print(f"  {name} ({s0}): evals={evals} schemes={len(seen)} "
              f"new={new} hits={hits} best={best[0]} {best[1]} "
              f"({time.time()-t0:.0f}s)", flush=True)
        if time.time() - t0 > seconds:
            break
    f.write(json.dumps({"kind": "summary", "evals": evals,
                        "distinct": len(seen), "new": new, "hits": hits,
                        "best_score": best[0], "best_scheme": best[1],
                        "mode": "ladder3", "which": which,
                        "complete": time.time() - t0 <= seconds,
                        "seconds": round(time.time() - t0, 1)}) + "\n")
    f.close()
    print(f"ladder3: evals={evals} schemes={len(seen)} new={new} "
          f"hits={hits} best={best[0]} {best[1]}")


if __name__ == "__main__":
    main()
