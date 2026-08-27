#!/usr/bin/env python3
"""Independent leftover-tight Python B&B on a sample of 4-star pools.

Second algorithm (leftover_bb, not the C colouring).  Sample: every
k=28 two-axis pool and a stride of the rest.  A hit is a leftover
41-set.  complete+empty matches the C merge on that pool.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from leftover_bb import leftover_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            out.append(bits)
    return out


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    masks = G["masks"]
    thresh = G["thresh"]
    groups = G["groups"]
    seed_index = {m: i for i, m in enumerate(groups)}
    stars = stars_of(G["D"])
    merged = json.loads((HERE / "four_star_extras.json").read_text())
    c_best = {tuple(p["stars"]): p for p in merged["pools"]}

    sample = []
    for comb in combinations(range(10), 4):
        U = stars[comb[0]] | stars[comb[1]] | stars[comb[2]] | stars[comb[3]]
        k = U.bit_count()
        if k == 28 or (sum(comb) % 7 == 0):
            sample.append(comb)

    rows = []
    mismatch = 0
    found_41 = False
    for comb in sample:
        U4 = stars[comb[0]] | stars[comb[1]] | stars[comb[2]] | stars[comb[3]]
        local, local_miss = [], []
        local_g = []
        for i, m in enumerate(masks):
            if m & ~U4 == 0:
                local.append(i)
                local_miss.append(m)
                local_g.append(seed_index[m])
        nL = len(local)
        adj = [0] * nL
        for a in range(nL):
            ia = local[a]
            for b in range(a + 1, nL):
                if local_g[a] != local_g[b] and ip(extras[ia], extras[local[b]]) <= thresh:
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        hit, best, nodes, complete, _U = leftover_search(
            adj, nL, local_miss, target=20, node_limit=2_000_000,
        )
        cref = c_best[tuple(comb)]
        ok = (complete and hit is None and not cref["found_41"]
              and cref["complete"])
        if hit is not None:
            found_41 = True
            ok = False
        if not ok:
            mismatch += 1
        rows.append({
            "stars": list(comb),
            "k": U4.bit_count(),
            "n_extras": nL,
            "best": best,
            "nodes": nodes,
            "complete": complete,
            "found_41": bool(hit),
            "c_best": cref["best"],
            "c_nodes": cref["nodes"],
            "c_complete": cref["complete"],
            "ok": ok,
        })
        print(
            f"stars={list(comb)} k={U4.bit_count()} nE={nL} "
            f"best={best} complete={complete} found_41={bool(hit)} ok={ok}",
            flush=True,
        )

    report = {
        "n_sample": len(rows),
        "n_ok": sum(1 for r in rows if r["ok"]),
        "n_mismatch": mismatch,
        "found_41": found_41,
        "rows": rows,
        "comment": (
            "Python leftover-tight replay of a covering sample of 4-star "
            "pools.  ok means complete empty, matching the C merge."
        ),
    }
    (HERE / "replay_four_star.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote replay_four_star.json mismatch=", mismatch)
    return 0 if mismatch == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
