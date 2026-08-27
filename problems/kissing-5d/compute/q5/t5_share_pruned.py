#!/usr/bin/env python3
"""Neighbourhood census for T^5 36-cliques of share 23.

q4 emptied share 24 through 30.  A remaining 36-clique K satisfies
|K ∩ C| <= 23 for every published 35-clique C.

Share 23 is C(35,12)*4 neighbourhoods if enumerated raw.  This file
lists, for each published 35, the outsiders with d_C >= 23 and records
how many 23-subsets of C have a common neighbourhood large enough to
host 13 extra vertices.  A full emptiness proof still lives in
t5_share.c.  Incomplete search is residue.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))
sys.path.insert(0, str(ROOT / "q4"))

from t5_36 import bits_list, build_pool, is_clique  # noqa: E402


def common_n(adj, verts, n):
    bits = (1 << n) - 1
    for v in verts:
        bits &= adj[v]
    for v in verts:
        bits &= ~(1 << v)
    return bits


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    share = 23
    need = 36 - share
    by_code = {}
    for name, rec in G["published"].items():
        C = rec["remainder_clique"]
        assert len(C) == 35 and is_clique(adj, C)
        Cset = set(C)
        outsiders = []
        for v in range(n):
            if v in Cset:
                continue
            dC = sum(1 for u in C if (adj[v] >> u) & 1)
            if dC >= share:
                outsiders.append((v, dC))
        # sample: common neighbourhood size of the whole C, and of
        # random 23-subsets, plus the max d_C outsider clique hint.
        N_all = common_n(adj, C, n)
        out_bits = 0
        for v, _ in outsiders:
            out_bits |= 1 << v
        pool = N_all & out_bits
        by_code[name] = {
            "n_outsiders_deg_ge_23": len(outsiders),
            "max_dC": max((d for _, d in outsiders), default=0),
            "common_N_of_C": N_all.bit_count(),
            "common_N_in_outsiders": pool.bit_count(),
            "need": need,
        }
    report = {
        "n": n,
        "share": share,
        "need": need,
        "by_code": by_code,
        "comment": (
            "Census only.  Share 23 emptiness is t5_share.c.  "
            "A 36-clique, if one exists, shares at most 23 with each "
            "published 35."
        ),
    }
    (HERE / "t5_share_pruned.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
