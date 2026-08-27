#!/usr/bin/env python3
"""Independent leftover-tight CNF rebuild for the three 5-star orbits.

Second algorithm: rebuild the DIMACS (cnfutil) and compare sha256 to
any stored five_star_sat.json.  Optional leftover_bb smoke on the
k=32 representative (tiny node budget; not a certificate).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import leftover_tight_cnf, load_graph, pool_for_stars, cnf_sha256  # noqa: E402
from leftover_bb import leftover_search  # noqa: E402
from orbits import REPS  # noqa: E402
from sphere import ip  # noqa: E402


def main() -> int:
    G = load_graph()
    stored = {}
    sat_path = HERE / "five_star_sat.json"
    if sat_path.exists():
        data = json.loads(sat_path.read_text())
        for p in data.get("pools", []):
            stored[tuple(p["stars"])] = p

    rows = []
    ok = True
    for name, comb in REPS.items():
        U, local, local_g, local_miss = pool_for_stars(G, comb)
        cnf, nL, nY = leftover_tight_cnf(G, local, local_g, local_miss, U)
        sha = cnf_sha256(cnf)
        rec = {
            "name": name,
            "stars": list(comb),
            "k": U.bit_count(),
            "n_extras": nL,
            "n_roots": nY,
            "cnf_vars": cnf.nv,
            "cnf_clauses": len(cnf.clauses),
            "cnf_sha256": sha,
        }
        if tuple(comb) in stored:
            s = stored[tuple(comb)]
            rec["sha_match"] = s.get("cnf_sha256") == sha
            rec["stored_sat"] = s.get("sat")
            if s.get("cnf_sha256") and not rec["sha_match"]:
                ok = False
                rec["ok"] = False
        if name == "k32_n2_1":
            adj = [0] * nL
            extras = G["extras"]
            thresh = G["thresh"]
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
        rows.append(rec)

    report = {
        "n_reps": len(rows),
        "ok": ok,
        "found_41": any(r.get("found_41") for r in rows),
        "reps": rows,
        "comment": (
            "CNF rebuild of the three Aut(D5) 5-star representatives.  "
            "sha256 match against five_star_sat.json when present.  "
            "Tiny leftover_bb smoke on the k=32 rep is not a certificate."
        ),
    }
    (HERE / "replay_five_star.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "ok": ok,
        "n_reps": len(rows),
        "sha": [r.get("sha_match") for r in rows],
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
