#!/usr/bin/env python3
"""Assemble five_star_sat.json / leftover_sat.json from native sat.json files."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def load_cnf_meta(name: str):
    p = CERTS / f"{name}.cnf.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}


def load_sat(name: str):
    p = CERTS / f"{name}.sat.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def five_row(name: str, stars, typ, k, n_extras):
    meta = load_cnf_meta(f"five_{name}")
    sat = load_sat(f"five_{name}")
    rec = {
        "name": name,
        "stars": list(stars),
        "type": list(typ),
        "k": k,
        "n_extras": n_extras,
        "n_roots": k,
        "cnf_vars": meta.get("vars"),
        "cnf_clauses": meta.get("clauses"),
        "cnf_sha256": meta.get("sha256"),
        "sat": None if sat is None else sat.get("sat"),
        "found_41": False,
    }
    if sat:
        rec["cadical"] = sat.get("cadical")
        rec["drat"] = sat.get("drat")
        rec["drat_bytes"] = sat.get("drat_bytes")
        rec["drat_trim"] = sat.get("drat_trim")
    return rec


def main() -> int:
    pools = [
        five_row("k32_n2_1", (0, 1, 2, 3, 4), (2, 1), 32, 528),
        five_row("k31_n1_3", (0, 1, 2, 4, 6), (1, 3), 31, 596),
        five_row("k30_n0_5", (0, 2, 4, 6, 8), (0, 5), 30, 625),
        five_row("q6_01235", (0, 1, 2, 3, 5), (2, 1), 32, 528),
        five_row("q6_01236", (0, 1, 2, 3, 6), (2, 1), 32, 528),
        five_row("q6_01237", (0, 1, 2, 3, 7), (2, 1), 32, 528),
    ]
    present = [p for p in pools if p.get("sat") is not None]
    n_unsat = sum(1 for p in present if p.get("sat") is False)
    n_verified = sum(
        1 for p in present
        if (p.get("drat_trim") or {}).get("status") == "VERIFIED"
    )
    report = {
        "n_pools": len(present),
        "n_expected": 6,
        "found_41": False,
        "n_sat_unsat": n_unsat,
        "n_drat_verified": n_verified,
        "complete": n_verified == 6 and n_unsat == 6,
        "pools": present,
        "comment": (
            "Leftover-tight SAT on 5-star hosts.  Native CaDiCaL 3.0.1 "
            "binary DRAT; Heule drat-trim.  Three Aut(D5) orbit "
            "representatives plus the four q6 k=32 cutoff pools "
            "(the orbit rep is one of those four).  UNSAT without a "
            "stored verified DRAT is residue.  Did not claim tau5=40."
        ),
    }
    (HERE / "five_star_sat.json").write_text(json.dumps(report, indent=2) + "\n")
    print("five_star_sat", "verified", n_verified, "/", len(present))

    glob = load_sat("n1_k19_star5")
    gmeta = load_cnf_meta("n1_k19_star5")
    if glob is not None:
        grec = {
            "k": 19,
            "n1": 21,
            "need_extras": 20,
            "min_star_cover": 5,
            "cnf_vars": gmeta.get("vars"),
            "cnf_clauses": gmeta.get("clauses"),
            "cnf_sha256": gmeta.get("sha256"),
            "sat": glob.get("sat"),
            "found_41": False,
            "complete": (glob.get("drat_trim") or {}).get("status") == "VERIFIED",
            "cadical": glob.get("cadical"),
            "drat": glob.get("drat"),
            "drat_bytes": glob.get("drat_bytes"),
            "drat_trim": glob.get("drat_trim"),
            "comment": (
                "Global leftover SAT k=19 star-cover>=5.  A model is a "
                "41-set.  UNSAT without a stored verified DRAT is residue. "
                " Did not claim tau5=40."
            ),
        }
        (HERE / "leftover_sat.json").write_text(json.dumps(grec, indent=2) + "\n")
        (HERE / "leftover_sat_k19.json").write_text(json.dumps(grec, indent=2) + "\n")
        (HERE / "leftover_sat_status.json").write_text(json.dumps({
            "k": 19,
            "n1": 21,
            "min_star_cover": 5,
            "cnf_vars": grec["cnf_vars"],
            "cnf_clauses": grec["cnf_clauses"],
            "found_41": False,
            "sat": grec["sat"],
            "complete": grec["complete"],
            "drat_trim": (grec.get("drat_trim") or {}).get("status"),
            "comment": grec["comment"],
        }, indent=2) + "\n")
        print("leftover_sat sat=", grec["sat"], "complete=", grec["complete"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
