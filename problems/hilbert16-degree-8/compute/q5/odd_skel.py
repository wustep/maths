#!/usr/bin/env python3
"""Compatible odd collections of size 5.

q1 finished size at most 3. q3 finished size 4 (5,308,103 evaluations,
twelve known M-schemes, no open nest). The published a=10 nest has
seven odd splits, so size 5 is the leftover enumerable odd skeleton.

usage:
  python3 q5/odd_skel.py count
  python3 q5/odd_skel.py 5 <out.jsonl> [--minsize 5] [--shard lo:hi] [cap]
"""
import argparse
import json
import os
import sys
import time

from common import boot, known_schemes, resolve_out

boot()

import deepnest as dn
from dn_charac import shape, nest_depth
from notation import stats

TARGETS = {(4, 2, 14), (14, 2, 4)}


def ev(sp, ids):
    try:
        return dn.evaluate([sp[i] for i in ids])[:2]
    except ValueError:
        return 0, None


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("maxsize_or_count")
    p.add_argument("out", nargs="?")
    p.add_argument("cap", nargs="?", type=int, default=0)
    p.add_argument("--minsize", type=int, default=5)
    p.add_argument("--shard", default=None,
                   help="first-index range lo:hi, half-open")
    args = p.parse_args(argv)
    return args


def shard_bounds(n_odds, spec):
    if not spec:
        return 0, n_odds
    lo, hi = spec.split(":")
    return int(lo), int(hi)


def count_size5():
    sp = dn.splits()
    adj = dn.compat_matrix()
    odds = [i for i, s in enumerate(sp) if not s.even]
    t0 = time.time()
    total = 0
    per = []
    for a in range(len(odds)):
        i = odds[a]
        ai = adj[i]
        cand = [odds[b] for b in range(a + 1, len(odds))
                if (ai >> odds[b]) & 1]
        n_a = 0
        for x in range(len(cand)):
            j = cand[x]
            mj = ai & adj[j]
            c2 = [cand[y] for y in range(x + 1, len(cand))
                  if (mj >> cand[y]) & 1]
            for y in range(len(c2)):
                k = c2[y]
                mk = mj & adj[k]
                c3 = [c2[z] for z in range(y + 1, len(c2))
                      if (mk >> c2[z]) & 1]
                for z in range(len(c3)):
                    ell = c3[z]
                    ml = mk & adj[ell]
                    n_a += sum(1 for w in range(z + 1, len(c3))
                               if (ml >> c3[w]) & 1)
        per.append(n_a)
        total += n_a
        if a % 20 == 0:
            print(f"  count a={a}/{len(odds)} n={n_a} total={total}",
                  flush=True)
    print(json.dumps({
        "odd_splits": len(odds),
        "size5_tuples": total,
        "per_first": per,
        "seconds": round(time.time() - t0, 2),
    }))
    return total, per


def main(argv):
    args = parse_args(argv)
    if args.maxsize_or_count == "count":
        count_size5()
        return
    maxsize = int(args.maxsize_or_count)
    out = resolve_out(args.out or "even_out/odd_skel5.jsonl")
    cap = args.cap
    minsize = args.minsize
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sp = dn.splits()
    adj = dn.compat_matrix()
    odds = [i for i, s in enumerate(sp) if not s.even]
    lo, hi = shard_bounds(len(odds), args.shard)
    print(f"{len(odds)} odd splits, maxsize={maxsize} minsize={minsize} "
          f"shard=[{lo},{hi}) cap={cap}", flush=True)
    known = known_schemes()
    f = open(out, "w")
    seen_sch = {}
    t0 = time.time()
    evals = hits = pn193 = 0
    stop = False

    def visit(ids):
        nonlocal evals, hits, pn193, stop
        if cap and evals >= cap:
            stop = True
            return
        evals += 1
        nc, sch = ev(sp, ids)
        if sch is None:
            return
        ov, p, n = stats(sch)
        a, b, c, junk = shape(sch)
        rec = {"kind": "scheme", "scheme": sch, "ncomp": nc,
               "pn": [p, n], "shape": [a, b, c, junk],
               "depth": nest_depth(sch), "collection": list(ids)}
        if (p, n) == (19, 3):
            pn193 += 1
            rec["kind"] = "pn193"
        if (a, b, c) in TARGETS:
            rec["kind"] = "HIT"
            hits += 1
        if sch not in seen_sch:
            seen_sch[sch] = list(ids)
            rec["new_scheme"] = sch not in known
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if rec["kind"] in ("HIT", "pn193") or sch not in known:
                print(f"  {rec['kind']} {sch} shape={(a, b, c, junk)} "
                      f"|S|={len(ids)}", flush=True)

    if minsize <= 0:
        visit([])
    if maxsize >= 1 and minsize <= 1 and not stop:
        for i in odds:
            visit([i])
            if stop:
                break
        print(f"size 1 done evals={evals} schemes={len(seen_sch)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize >= 2 and minsize <= 2 and not stop:
        for a in range(len(odds)):
            i = odds[a]
            ai = adj[i]
            for b in range(a + 1, len(odds)):
                j = odds[b]
                if not (ai >> j) & 1:
                    continue
                visit([i, j])
                if stop:
                    break
            if stop:
                break
        print(f"size 2 done evals={evals} schemes={len(seen_sch)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize >= 3 and minsize <= 3 and not stop:
        for a in range(len(odds)):
            i = odds[a]
            ai = adj[i]
            cand = [odds[b] for b in range(a + 1, len(odds))
                    if (ai >> odds[b]) & 1]
            for x in range(len(cand)):
                j = cand[x]
                mj = ai & adj[j]
                for y in range(x + 1, len(cand)):
                    k = cand[y]
                    if not (mj >> k) & 1:
                        continue
                    visit(sorted([i, j, k]))
                    if stop:
                        break
                if stop:
                    break
            if stop:
                break
            if a % 20 == 0:
                print(f"  size3 {a}/{len(odds)} evals={evals} "
                      f"schemes={len(seen_sch)}", flush=True)
        print(f"size 3 done evals={evals} schemes={len(seen_sch)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize >= 4 and minsize <= 4 and not stop:
        for a in range(len(odds)):
            i = odds[a]
            ai = adj[i]
            cand = [odds[b] for b in range(a + 1, len(odds))
                    if (ai >> odds[b]) & 1]
            for x in range(len(cand)):
                j = cand[x]
                mj = ai & adj[j]
                c2 = [cand[y] for y in range(x + 1, len(cand))
                      if (mj >> cand[y]) & 1]
                for y in range(len(c2)):
                    k = c2[y]
                    mk = mj & adj[k]
                    for z in range(y + 1, len(c2)):
                        ell = c2[z]
                        if not (mk >> ell) & 1:
                            continue
                        visit(sorted([i, j, k, ell]))
                        if stop:
                            break
                    if stop:
                        break
                if stop:
                    break
            if stop:
                break
            if a % 5 == 0:
                print(f"  size4 {a}/{len(odds)} evals={evals} "
                      f"schemes={len(seen_sch)} hits={hits}", flush=True)
        print(f"size 4 done evals={evals} schemes={len(seen_sch)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize >= 5 and minsize <= 5 and not stop:
        for a in range(lo, hi):
            i = odds[a]
            ai = adj[i]
            cand = [odds[b] for b in range(a + 1, len(odds))
                    if (ai >> odds[b]) & 1]
            for x in range(len(cand)):
                j = cand[x]
                mj = ai & adj[j]
                c2 = [cand[y] for y in range(x + 1, len(cand))
                      if (mj >> cand[y]) & 1]
                for y in range(len(c2)):
                    k = c2[y]
                    mk = mj & adj[k]
                    c3 = [c2[z] for z in range(y + 1, len(c2))
                          if (mk >> c2[z]) & 1]
                    for z in range(len(c3)):
                        ell = c3[z]
                        ml = mk & adj[ell]
                        for w in range(z + 1, len(c3)):
                            p = c3[w]
                            if not (ml >> p) & 1:
                                continue
                            visit(sorted([i, j, k, ell, p]))
                            if stop:
                                break
                        if stop:
                            break
                    if stop:
                        break
                if stop:
                    break
            if stop:
                break
            print(f"  size5 {a}/{len(odds)} shard=[{lo},{hi}) "
                  f"evals={evals} schemes={len(seen_sch)} hits={hits} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        print(f"size 5 done evals={evals} schemes={len(seen_sch)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    f.write(json.dumps({"kind": "summary", "evals": evals,
                        "distinct": len(seen_sch), "hits": hits,
                        "pn193": pn193, "maxsize": maxsize,
                        "minsize": minsize,
                        "shard": [lo, hi], "n_odds": len(odds),
                        "complete": not stop,
                        "seconds": round(time.time() - t0, 1)}) + "\n")
    f.close()
    print(f"odd_skel: evals={evals} schemes={len(seen_sch)} hits={hits} "
          f"pn193_evals={pn193} complete={not stop} shard=[{lo},{hi})")


if __name__ == "__main__":
    main(sys.argv[1:])
