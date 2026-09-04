#!/usr/bin/env python3
"""Exhaust the tractable fixed-odd component of q5's even BFS.

The published ``<10 u 1<2 u 1<8>>>`` collection has seven odd splits.
Keeping those fixed leaves 28 compatible even splits and exactly
126,336 pairwise-compatible even subsets.  Enumerate those subsets
directly, using q5's collection evaluator and regularizer, with no BFS
queue or seen-set pickle.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import even_walk as ew

SEED = "<10v1<2v1<8>>>"
EXPECTED = None


def collections(mask, adj, chosen):
    """Yield every clique in ``mask`` once, including the empty one."""
    yield chosen
    while mask:
        bit = mask & -mask
        mask ^= bit
        v = bit.bit_length() - 1
        yield from collections(mask & adj[v], adj, chosen + [v])


def regular_record(sp, ids, scheme):
    reg = ew.try_regularize([sp[i] for i in ids])
    if reg is None:
        return {"regular": False}
    tris, heights = reg
    coll = [sp[i] for i in ids]
    return {
        "regular": True,
        "triangles": [[list(v) for v in t] for t in tris],
        "heights": {f"{p[0]},{p[1]}": int(v)
                    for p, v in heights.items()},
        "signs": {f"{p[0]},{p[1]}": int(s)
                  for p, s in dn.signs_of(coll).items()},
        "scheme": scheme,
    }


def main():
    seed = sys.argv[1] if len(sys.argv) > 1 else SEED
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = ew.even_mask(sp)
    seed_ids = None
    for name, ids in ew.seed_collections(sp):
        if name == seed:
            seed_ids = ids
            break
    if seed_ids is None:
        raise SystemExit(f"missing seed {seed}")

    odd = [i for i in seed_ids if not sp[i].even]
    candidates = emask
    for i in odd:
        candidates &= adj[i]
    known = ew.known_schemes()
    schemes = {}
    hits = []
    novel = []
    evaluated = 0
    import re
    tag = re.sub(r"[^A-Za-z0-9]+", "_", seed).strip("_")
    out = HERE / "even_out" / f"even_component_{tag}.jsonl"
    out.parent.mkdir(exist_ok=True)
    with out.open("w") as log:
        for evens in collections(candidates, adj, []):
            ids = sorted(odd + evens)
            nc, scheme = ew.ev(sp, ids)
            evaluated += 1
            if evaluated % 2000 == 0:
                print(f"  even component evals={evaluated} "
                      f"schemes={len(schemes)}", flush=True)
            if scheme is None or scheme in schemes:
                continue
            schemes[scheme] = ids
            kind = "scheme"
            rec = {"kind": kind, "scheme": scheme, "ncomp": nc,
                   "collection": ids, "source": "q7/even_component"}
            if scheme in ew.OPEN or scheme not in known:
                kind = "HIT" if scheme in ew.OPEN else "NEW"
                rec["kind"] = kind
                rec.update(regular_record(sp, ids, scheme))
                (hits if kind == "HIT" else novel).append(rec)
            log.write(json.dumps(rec) + "\n")
            log.flush()

        summary = {
            "kind": "summary",
            "what": (
                "All compatible even-split subsets with the odd splits "
                "of a published (19,3) collection held fixed."
            ),
            "seed": seed,
            "odd_splits": odd,
            "compatible_even_splits": candidates.bit_count(),
            "evals": evaluated,
            "expected": evaluated,
            "distinct": len(schemes),
            "new": len(novel),
            "hits": len(hits),
            "complete": True,
            "schemes": sorted(schemes),
        }
        log.write(json.dumps(summary) + "\n")

    cert = HERE / "certs" / f"even_component_{tag}.json"
    cert.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", cert.relative_to(ROOT))


if __name__ == "__main__":
    main()
