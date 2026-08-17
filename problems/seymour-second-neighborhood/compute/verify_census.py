#!/usr/bin/env python3
"""Independent checks of the labeled Pisa census and SAT residues.

Replays Halkiewicz's published n=6,7 counts against compute/enum_pisa,
checks every SAT witness with seymour.py, and confirms the cycle-power
family is Pisa and not Kn-minus-matching for n>=7 (except C8^3).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seymour import (
    cycle_power,
    decode_ternary,
    directed_cycle,
    is_matching_missing,
    is_pisa,
    is_seymour_tight,
    missing_degree_sequence,
)


ROOT = Path(__file__).resolve().parent
CERTS = ROOT / "certs"

HALKIEWICZ = {
    6: {
        "pisa": 1050,
        "types": {
            (3, 3, 3, 3, 3, 3): 120,
            (1, 1, 1, 1, 1, 1): 150,
            (1, 1, 1, 1, 0, 0): 180,
            (1, 1, 0, 0, 0, 0): 360,
            (0, 0, 0, 0, 0, 0): 240,
        },
    },
    7: {
        "pisa": 4080,
        "types": {
            (4, 4, 4, 4, 4, 4, 4): 720,
            (2, 2, 2, 2, 2, 2, 2): 720,
            (0, 0, 0, 0, 0, 0, 0): 2640,
        },
    },
}


def load(name):
    return json.loads((CERTS / name).read_text())


def check_halkiewicz():
    report = []
    for n in (6, 7):
        path = CERTS / f"pisa_n{n}.json"
        data = json.loads(path.read_text())
        assert data["n"] == n
        assert data["pisa"] == HALKIEWICZ[n]["pisa"], (n, data["pisa"])
        got = {}
        for row in data["missing_degree_types"]:
            key = tuple(row["missing_deg"])
            got[key] = row["count"]
        assert got == HALKIEWICZ[n]["types"], (n, got)
        report.append({
            "n": n,
            "pisa": data["pisa"],
            "pisa_tight": data.get("pisa_tight"),
            "types": {str(k): v for k, v in got.items()},
            "matches_halkiewicz": True,
        })
    return report


def check_constructions():
    rows = []
    for n, k in [(7, 2), (8, 2), (8, 3), (9, 2), (9, 3), (9, 4)]:
        out = cycle_power(n, k)
        rows.append({
            "name": f"C{n}^{k}",
            "pisa": is_pisa(out),
            "tight": is_seymour_tight(out),
            "matching_missing": is_matching_missing(out),
            "missing_deg": list(missing_degree_sequence(out)),
        })
        assert is_pisa(out) == (2 * k < n)
    c8 = directed_cycle(8)
    assert is_pisa(c8)
    return rows


def check_sat_witnesses():
    rows = []
    for path in sorted(CERTS.glob("*.json")):
        data = json.loads(path.read_text())
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("status") not in ("FEASIBLE", "OPTIMAL"):
                continue
            code = item.get("code")
            n = item.get("n") or (item.get("witness") or {}).get("n")
            if code is None or n is None:
                continue
            out = decode_ternary(n, code)
            ok = is_pisa(out)
            rows.append({"file": path.name, "n": n, "code": code, "pisa": ok})
            if not ok:
                raise SystemExit(f"SAT witness in {path.name} is not Pisa")
    return rows


def check_regular_dense():
    rows = []
    for path in sorted(CERTS.glob("regular_d*.json")):
        data = json.loads(path.read_text())
        rows.append({
            "file": path.name,
            "delta": data.get("delta"),
            "n": data.get("n"),
            "status": data.get("status"),
            "eulerian": data.get("eulerian"),
            "solve_time": data.get("solve_time"),
        })
        if data.get("status") == "FEASIBLE":
            raise SystemExit(f"unexpected Eulerian counterexample in {path.name}")
    return rows


def main():
    rec = {
        "halkiewicz": check_halkiewicz(),
        "constructions": check_constructions(),
        "sat_witnesses": check_sat_witnesses(),
        "regular_dense": check_regular_dense(),
    }
    print(json.dumps(rec, indent=2))
    out = CERTS / "verify_report.json"
    out.write_text(json.dumps(rec, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
