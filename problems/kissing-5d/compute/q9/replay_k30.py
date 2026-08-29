#!/usr/bin/env python3
"""Independent leftover-tight CNF rebuild; must match q8 sha256."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q8 = HERE.parent / "q8"
sys.path.insert(0, str(Q8))
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import leftover_tight_cnf, load_graph, pool_for_stars, cnf_sha256  # noqa: E402
from leftover_bb import leftover_search  # noqa: E402
from orbits import REPS  # noqa: E402
from sphere import ip  # noqa: E402

K30_SHA = "cdec5e76ef58cddadf999f77ec31f7e319764ab867454cdac0ae74f2e53f078c"

K30 = REPS["k30_n0_5"]


def main() -> int:
    G = load_graph()
    U, local, local_g, local_miss = pool_for_stars(G, K30)
    cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
    sha = cnf_sha256(cnf)
    rec = {
        "name": "k30_n0_5",
        "stars": list(K30),
        "k": U.bit_count(),
        "n_extras": nL,
        "n_roots": nY,
        "cnf_vars": cnf.nv,
        "cnf_clauses": len(cnf.clauses),
        "cnf_sha256": sha,
        "sha_match_q8": sha == K30_SHA,
    }
    ok = sha == K30_SHA
    extras = G["extras"]
    thresh = G["thresh"]
    adj = [0] * nL
    for a in range(nL):
        for b in range(a + 1, nL):
            if (local_g[a] != local_g[b]
                    and ip(extras[local[a]], extras[local[b]]) <= thresh):
                adj[a] |= 1 << b
                adj[b] |= 1 << a
    hit, best, nodes, complete, _U = leftover_search(
        adj, nL, local_miss, target=20, node_limit=2000,
    )
    rec["bb_smoke_best"] = best
    rec["bb_smoke_nodes"] = nodes
    rec["bb_smoke_complete"] = complete
    rec["bb_smoke_hit"] = hit is not None
    if hit is not None:
        ok = False
        rec["found_41"] = True
    report = {
        "ok": ok,
        "found_41": hit is not None,
        "rep": rec,
        "comment": (
            "CNF rebuild of the type-(0,5) leftover-tight representative. "
            " Encoder is q8/cnfutil.py. Tiny leftover_bb smoke is not a "
            " certificate."
        ),
    }
    (HERE / "replay_k30.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"ok": ok, "sha_match_q8": rec["sha_match_q8"],
                      "n_extras": nL, "k": rec["k"]}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
