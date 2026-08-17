#!/usr/bin/env python3
"""Recheck every SAT witness with the bitmask kernel (not the solver)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seymour import (
    all_margins,
    decode_ternary,
    from_arcs,
    graph_signature,
    is_matching_missing,
    is_pisa,
    is_seymour_tight,
    is_strongly_connected,
    missing_degree_sequence,
)


def check_item(item, origin):
    if not isinstance(item, dict):
        return None
    if item.get("status") not in ("FEASIBLE", "OPTIMAL"):
        return None
    w = item.get("witness") or {}
    n = item.get("n") or w.get("n")
    out = None
    if item.get("code") is not None and n:
        out = decode_ternary(n, item["code"])
    elif w.get("arcs") and n:
        out = from_arcs(n, [tuple(a) for a in w["arcs"]])
    if out is None:
        return None
    sig = graph_signature(out)
    assert is_pisa(out), (origin, sig)
    return {
        "origin": origin,
        "n": sig["n"],
        "pisa": True,
        "tight": sig["tight"],
        "matching_missing": sig["matching_missing"],
        "missing_deg": sig["missing_deg"],
        "underlying_deg": sig["underlying_deg"],
        "outdegrees": sig["outdegrees"],
        "margins": sig["margins"],
        "n_missing": len(sig["missing"]),
        "code": sig["code"],
    }


def main():
    certs = Path(__file__).resolve().parent / "certs"
    rows = []
    for path in sorted(certs.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            rec = check_item(item, path.name)
            if rec:
                rows.append(rec)
                print(
                    f"OK {path.name} miss={rec['missing_deg']} "
                    f"tight={rec['tight']} match={rec['matching_missing']}"
                )
    outp = certs / "verified_witnesses.json"
    outp.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"verified {len(rows)} witnesses -> {outp}")


if __name__ == "__main__":
    main()
