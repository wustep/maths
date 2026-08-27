#!/usr/bin/env python3
"""Collect DONE lines and JSON stubs into certs/q1_summary.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = HERE / "logs"
CERTS = HERE / "certs"


def load_json(name):
    p = CERTS / name
    if not p.exists():
        return None
    return json.loads(p.read_text())


def parse_done(text: str) -> dict:
    rec = {}
    for line in text.splitlines():
        if line.startswith("HIT"):
            rec.setdefault("hits_lines", []).append(line)
        if line.startswith("DONE"):
            for m in re.finditer(r"([A-Za-z_]+)=([0-9.]+)", line):
                k, v = m.group(1), m.group(2)
                rec[k] = float(v) if "." in v else int(v)
            rec["done"] = line
    return rec


def main() -> int:
    summary = {
        "group_laws": load_json("group_laws.json"),
        "srg43": load_json("srg43_params.json"),
        "c7_selftest": load_json("c7_selftest.json"),
        "aut_mckay": None,
        "two_flip": load_json("two_flip.json"),
        "py_c11c4": load_json("py_c11c4.json"),
        "py_c3c15": load_json("py_c3c15.json"),
        "c7_n14": load_json("c7_n14.json"),
        "c7_n42": load_json("c7_n42.json"),
        "c7_n43": load_json("c7_n43.json"),
        "circulant44": parse_done((LOGS / "circ44.txt").read_text())
        if (LOGS / "circ44.txt").exists()
        else None,
        "circulant45": parse_done((LOGS / "circ45.txt").read_text())
        if (LOGS / "circ45.txt").exists()
        else None,
        "extend_flips": parse_done((LOGS / "extend_flips.txt").read_text())
        if (LOGS / "extend_flips.txt").exists()
        else None,
        "cayley": {},
    }
    aut = load_json("aut_mckay.json")
    if aut:
        summary["aut_mckay"] = {
            k: aut[k]
            for k in aut
            if k != "records"
        }
    for g in ("c2c22", "d22", "c11c4", "c3c15"):
        p = LOGS / f"cayley_{g}.txt"
        if p.exists():
            summary["cayley"][g] = parse_done(p.read_text())
    hits = 0
    for g, rec in summary["cayley"].items():
        hits += rec.get("hits", 0)
    ext = (summary["extend_flips"] or {}).get("extensions", 0)
    summary["any_43_graph"] = ext > 0
    summary["any_cayley_hit"] = hits > 0
    summary["interval_moved"] = False
    summary["note"] = (
        "A HIT Cayley graph of order 44 or 45, or an extend_flips extension, "
        "would be a certified new (5,5)-graph and a dent. Isolated SAT "
        "timeouts are UNKNOWN, not a bound."
    )
    dest = CERTS / "q1_summary.json"
    dest.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "aut_mckay"}, indent=2))
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
