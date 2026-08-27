#!/usr/bin/env python3
"""Write the T^5 36-clique CNF and a Cadical DRAT (if UNSAT).

Replay: python3 t5_36_proof.py && ./bin/drat-trim certs/t5_clique36.cnf
certs/t5_clique36.drat
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from t5_36 import build_pool, is_clique  # noqa: E402


def build_cnf(adj, n, target=36):
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF

    cnf = CNF()
    for i in range(n):
        for j in range(i + 1, n):
            if not ((adj[i] >> j) & 1):
                cnf.append([-(i + 1), -(j + 1)])
    card = CardEnc.equals(lits=list(range(1, n + 1)), bound=target,
                          encoding=EncType.seqcounter)
    cnf.extend(card.clauses)
    return cnf


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    (HERE / "certs").mkdir(exist_ok=True)
    cnf = build_cnf(adj, n, 36)
    cnf_path = HERE / "certs" / "t5_clique36.cnf"
    cnf.to_file(str(cnf_path))
    print(f"cnf n={n} vars={cnf.nv} clauses={len(cnf.clauses)} "
          f"wrote {cnf_path}", flush=True)

    from pysat.solvers import Cadical195
    slv = Cadical195(bootstrap_with=cnf, with_proof=True)
    sat = slv.solve()
    model = slv.get_model() if sat else None
    proof = slv.get_proof() if not sat else None
    slv.delete()
    print(f"cadical sat={sat}", flush=True)

    report = {
        "n": n,
        "target": 36,
        "cnf_vars": cnf.nv,
        "cnf_clauses": len(cnf.clauses),
        "sat": bool(sat),
        "proof_lines": len(proof) if proof else 0,
    }
    if sat and model:
        true = set(x for x in model if 1 <= x <= n)
        clique = sorted(v - 1 for v in true)
        report["found_36"] = is_clique(adj, clique) and len(clique) == 36
        report["clique"] = clique
        if report["found_36"]:
            univ = G["univ"]
            keep = G["keep"]
            pool = G["pool"]
            idx = [keep[i] for i in clique] + list(univ)
            pts = [list(map(str, pool[i])) for i in idx]
            (HERE / "certs" / "code41.json").write_text(json.dumps({
                "n": 41,
                "source": "T5 remainder 36-clique plus 5 universal basis vectors",
                "points": pts,
            }, indent=2) + "\n")
    else:
        report["found_36"] = False
        if proof:
            drat = HERE / "certs" / "t5_clique36.drat"
            drat.write_text("\n".join(proof) + "\n")
            report["drat"] = str(drat.name)
            report["comment"] = (
                "Cadical UNSAT proof for a 36-clique in the 355-point "
                "T^5 remainder.  Replay with drat-trim."
            )
        else:
            report["comment"] = "UNSAT without a proof object."

    (HERE / "t5_36_proof.json").write_text(json.dumps(report, indent=2) + "\n")
    print("wrote t5_36_proof.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
