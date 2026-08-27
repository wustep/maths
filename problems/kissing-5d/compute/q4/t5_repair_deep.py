#!/usr/bin/env python3
"""Deeper exact repairs of the published 35-cliques.

q3 emptied remove-1-add-2 and remove-2-add-3 (candidate cap 28).
A 36-clique that shares 32 vertices with a published 35 is a
remove-3-add-4.  Share 31 is remove-4-add-5.

These are exact.  A hit lifts through the five universal basis vectors
to a 41-code.  Empty repairs at these distances are not an emptiness
proof of the 36-clique.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from t5_36 import bits_list, build_pool, common_neighbours, is_clique


def repair(adj, clique, n, remove_k, add_k, cand_cap=40):
    C = list(clique)
    Cset = set(C)
    hits = 0
    tried = 0
    for drop in combinations(range(len(C)), remove_k):
        keep = [C[i] for i in range(len(C)) if i not in drop]
        cand_bits = common_neighbours(adj, keep, n)
        cand = [v for v in bits_list(cand_bits) if v not in Cset]
        if len(cand) < add_k:
            continue
        tried += 1
        if add_k >= 4 and len(cand) > cand_cap:
            continue
        for add in combinations(cand, add_k):
            if is_clique(adj, add):
                new = keep + list(add)
                if len(new) >= 36 and is_clique(adj, new):
                    return {
                        "hits": hits + 1,
                        "tried": tried,
                        "clique": new[:36],
                    }
                hits += 1
    return {"hits": hits, "tried": tried, "clique": None}


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    report = {"n": n, "repairs": [], "found_36": False, "clique36": None}
    for name, rec in G["published"].items():
        C = rec["remainder_clique"]
        if len(C) != 35 or not is_clique(adj, C):
            continue
        for remove_k, add_k, cap in ((3, 4, 36), (4, 5, 24)):
            print(f"{name} remove {remove_k} add {add_k} ...", flush=True)
            rec = repair(adj, C, n, remove_k, add_k, cand_cap=cap)
            rec.update({"from": name, "remove": remove_k, "add": add_k})
            report["repairs"].append(rec)
            print(f"  tried={rec['tried']} hits={rec['hits']}", flush=True)
            if rec["clique"]:
                report["found_36"] = True
                report["clique36"] = rec["clique"]
                break
        if report["found_36"]:
            break
    (HERE / "t5_repair_deep.json").write_text(
        json.dumps({k: v for k, v in report.items() if k != "clique36"},
                   indent=2) + "\n"
    )
    if report["found_36"]:
        univ = G["univ"]
        keep = G["keep"]
        pool = G["pool"]
        idx = [keep[i] for i in report["clique36"]] + list(univ)
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / "code41.json").write_text(json.dumps({
            "n": 41,
            "source": "T5 deep repair plus 5 universal basis vectors",
            "remainder_clique": report["clique36"],
            "points": [list(map(str, pool[i])) for i in idx],
        }, indent=2) + "\n")
    print("found_36", report["found_36"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
