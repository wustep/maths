#!/usr/bin/env python3
"""Compatible odd collections of size 4.

q1 finished size <= 3 (368,936 evaluations, 12 known M-schemes, no
open nest).  The published a=10 nest has seven odd splits, so size 4
is the next skeleton that can see a larger odd part while staying
enumerable.

usage: python3 q2/odd_skel.py <maxsize> <out.jsonl> [max_evals]
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
    maxsize = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    out = resolve_out(sys.argv[2] if len(sys.argv) > 2
                      else "even_out/odd_skel4.jsonl")
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sp = dn.splits()
    adj = dn.compat_matrix()
    odds = [i for i, s in enumerate(sp) if not s.even]
    print(f"{len(odds)} odd splits, maxsize={maxsize} cap={cap}", flush=True)
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

    visit([])
    for i in odds:
        visit([i])
        if stop:
            break
    print(f"size 1 done evals={evals} schemes={len(seen_sch)} "
          f"({time.time()-t0:.0f}s)", flush=True)
    if maxsize >= 2 and not stop:
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
    if maxsize >= 3 and not stop:
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
    if maxsize >= 4 and not stop:
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
    f.write(json.dumps({"kind": "summary", "evals": evals,
                        "distinct": len(seen_sch), "hits": hits,
                        "pn193": pn193, "maxsize": maxsize,
                        "complete": not stop,
                        "seconds": round(time.time() - t0, 1)}) + "\n")
    f.close()
    print(f"odd_skel: evals={evals} schemes={len(seen_sch)} hits={hits} "
          f"pn193_evals={pn193} complete={not stop}")


if __name__ == "__main__":
    main()
