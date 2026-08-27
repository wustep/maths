#!/usr/bin/env python3
"""Add a nested pair of odd splits to each published (19,3) collection.

Theorem 17: even splits keep (p, n).  Remark 20: nested odd splits
cancel, so a nested odd pair can stay on the (19,3) row while changing
the odd skeleton — the move an even-only walk cannot see.

usage: python3 q1/odd_cancel.py <out.jsonl> [max_pairs_per_seed]
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
OPEN = {"<4 u 1<2 u 1<14>>>", "<14 u 1<2 u 1<4>>>"}


def nested(a, b):
    """True if the Z+ zones are comparable (one nestable in the other)."""
    return a.zplus <= b.zplus or b.zplus <= a.zplus


def ev(sp, ids):
    try:
        return dn.evaluate([sp[i] for i in ids])[:2]
    except ValueError:
        return 0, None


def seed_193(sp):
    key = {x.key: i for i, x in enumerate(sp)}
    out = []
    for claimed, rec in sorted(json.load(
            open("certs/mcert_collections.json")).items()):
        if "p19-n03" not in rec.get("cert", ""):
            continue
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
            out.append((claimed, sorted(ids)))
    return out


def main():
    out = resolve_out(sys.argv[1] if len(sys.argv) > 1
                      else "even_out/odd_cancel.jsonl")
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sp = dn.splits()
    adj = dn.compat_matrix()
    odds = [i for i, s in enumerate(sp) if not s.even]
    known = known_schemes()
    seeds = seed_193(sp)
    print(f"{len(seeds)} (19,3) seeds, {len(odds)} odd splits", flush=True)
    f = open(out, "w")
    seen_sch = {}
    t0 = time.time()
    evals = hits = pn193 = 0

    def visit(ids, tag):
        nonlocal evals, hits, pn193
        evals += 1
        nc, sch = ev(sp, ids)
        if sch is None:
            return
        ov, p, n = stats(sch)
        a, b, c, junk = shape(sch)
        rec = {"kind": "scheme", "scheme": sch, "ncomp": nc,
               "pn": [p, n], "shape": [a, b, c, junk],
               "depth": nest_depth(sch), "collection": list(ids),
               "tag": tag}
        if (p, n) == (19, 3):
            pn193 += 1
            rec["kind"] = "pn193"
        if sch in OPEN or (a, b, c) in TARGETS:
            rec["kind"] = "HIT"
            hits += 1
        if sch not in seen_sch:
            seen_sch[sch] = list(ids)
            rec["new_scheme"] = sch not in known
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"  {rec['kind']} {sch} shape={(a, b, c, junk)} "
                  f"|S|={len(ids)} {tag}", flush=True)

    for name, ids in seeds:
        visit(ids, f"seed/{name}")
        have = set(ids)
        mask = (1 << len(sp)) - 1
        for i in ids:
            mask &= adj[i] | (1 << i)
        cand = [j for j in odds if j not in have and (mask >> j) & 1]
        pairs = 0
        for x in range(len(cand)):
            jx = cand[x]
            mx = mask & adj[jx]
            for y in range(x + 1, len(cand)):
                jy = cand[y]
                if not (mx >> jy) & 1:
                    continue
                if not nested(sp[jx], sp[jy]):
                    continue
                visit(sorted(ids + [jx, jy]), f"cancel/{name}")
                pairs += 1
                if cap and pairs >= cap:
                    break
            if cap and pairs >= cap:
                break
        print(f"  {name}: nested-odd-pairs={pairs} evals={evals} "
              f"schemes={len(seen_sch)} hits={hits} "
              f"({time.time() - t0:.0f}s)", flush=True)

    f.write(json.dumps({"kind": "summary", "evals": evals,
                        "distinct": len(seen_sch), "hits": hits,
                        "pn193": pn193, "seconds": round(time.time() - t0, 1),
                        "seeds": len(seeds)}) + "\n")
    f.close()
    print(f"odd_cancel: evals={evals} schemes={len(seen_sch)} "
          f"hits={hits} pn193={pn193}")


if __name__ == "__main__":
    main()
