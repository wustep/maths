#!/usr/bin/env python3
"""Distance-1 and distance-2 repairs of the published 35-cliques.

A 36-clique in the 355-point remainder cannot be a published 35-clique
plus one vertex (those four 40-codes are polar-maximal).  The first
possible edit is remove 1 add 2, then remove 2 add 3.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from t5_36 import build_pool, is_clique, repair


def main() -> int:
    G = build_pool()
    n = G["n"]
    adj = G["adj"]
    repairs = []
    found36 = None
    for name, rec in G["published"].items():
        cl = rec["remainder_clique"]
        if rec["remainder_size"] != 35 or not is_clique(adj, cl):
            continue
        for rk, ak in ((1, 2), (2, 3)):
            print(f"repair {name} remove {rk} add {ak} ...", flush=True)
            hits = repair(adj, cl, n, rk, ak)
            repairs.append({
                "from": name,
                "remove": rk,
                "add": ak,
                "hits": len(hits),
                "clique": hits[0] if hits else None,
            })
            print(f"  hits={len(hits)}", flush=True)
            if hits:
                found36 = hits[0]
                break
        if found36:
            break
    report = {
        "n_remainder": n,
        "repairs": repairs,
        "found_36": found36 is not None,
        "found_41": False,
        "complete": True,
        "clique36": found36,
        "comment": (
            "Exact repairs of the four published 35-cliques.  A hit would "
            "lift through the five universal basis vectors to a 41-code. "
            "Empty repairs are not an emptiness proof of the 36-clique."
        ),
    }
    if found36:
        rem_idx = found36
        full = [G["keep"][i] for i in rem_idx] + G["univ"]
        report["found_41"] = len(full) == 41
        report["indices_in_360"] = full
    (HERE / "t5_repair.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n_remainder", "found_36", "found_41", "repairs")},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
