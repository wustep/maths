#!/usr/bin/env python3
"""Enumerate small odd-split skeletons that stay in (p,n)=(19,3).

Even twists of the published (19,3) collections only realise the five
known (19,3) M-schemes (see even_walk probe).  Remark 20: nested odd
splits cancel, so a different odd skeleton with net effect 0 can stay
in (19,3) and is invisible to an even-only walk.  This enumerates
compatible odd collections of size <= maxsize, evaluates C(S), and
keeps every (19,3) scheme, especially depth-3 ones with a near 4 or 14.

usage: python3 q1/odd_skel.py <maxsize> <out.jsonl>
"""
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


def main():
    maxsize = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = resolve_out(sys.argv[2] if len(sys.argv) > 2 else "even_out/odd_skel.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sp = dn.splits()
    adj = dn.compat_matrix()
    odds = [i for i, s in enumerate(sp) if not s.even]
    print(f"{len(odds)} odd splits, maxsize={maxsize}", flush=True)
    known = known_schemes()
    f = open(out, "w")
    seen_sch = {}
    t0 = time.time()
    evals = 0
    hits = 0
    pn193 = 0

    def visit(ids):
        nonlocal evals, hits, pn193
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
                print(f"  {rec['kind']} {sch} shape={(a,b,c,junk)} "
                      f"|S|={len(ids)}", flush=True)

    visit([])
    # size 1
    for i in odds:
        visit([i])
    print(f"size 1 done evals={evals} schemes={len(seen_sch)} "
          f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize < 2:
        f.write(json.dumps({"kind": "summary", "evals": evals,
                            "distinct": len(seen_sch), "hits": hits,
                            "pn193": pn193, "maxsize": maxsize}) + "\n")
        return
    # size 2
    for a in range(len(odds)):
        i = odds[a]
        ai = adj[i]
        for b in range(a + 1, len(odds)):
            j = odds[b]
            if not (ai >> j) & 1:
                continue
            visit([i, j])
        if a % 20 == 0:
            print(f"  size2 {a}/{len(odds)} evals={evals} "
                  f"schemes={len(seen_sch)}", flush=True)
    print(f"size 2 done evals={evals} schemes={len(seen_sch)} "
          f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize >= 3:
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
            if a % 10 == 0:
                print(f"  size3 {a}/{len(odds)} evals={evals} "
                      f"schemes={len(seen_sch)} hits={hits}", flush=True)
        print(f"size 3 done evals={evals} schemes={len(seen_sch)} "
              f"({time.time()-t0:.0f}s)", flush=True)
    f.write(json.dumps({"kind": "summary", "evals": evals,
                        "distinct": len(seen_sch), "hits": hits,
                        "pn193": pn193, "maxsize": maxsize,
                        "seconds": round(time.time() - t0, 1)}) + "\n")
    f.close()
    print(f"odd_skel: evals={evals} schemes={len(seen_sch)} hits={hits} "
          f"pn193_evals={pn193}")


if __name__ == "__main__":
    main()
