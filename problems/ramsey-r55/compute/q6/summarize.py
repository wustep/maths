#!/usr/bin/env python3
"""Collect leftover order-2/3/5 certificates and remaining timeouts."""

from __future__ import annotations

import json
from pathlib import Path

from cases import leftover_q6


def main() -> int:
    cases = leftover_q6()
    verified = []
    models = []
    timeouts = []
    pending = []
    for case in cases:
        cert_path = Path("certs") / f"{case['name']}.json"
        if not cert_path.exists():
            pending.append(case["name"])
            continue
        rec = json.loads(cert_path.read_text())
        status = rec.get("status")
        if status == "UNSAT" and rec.get("proof_verified"):
            verified.append({
                "covers_k": case["covers_k"],
                "cycles": case["cycles"],
                "cycle_type": case["cycle_type"],
                "fixed": case["fixed"],
                "fixed_cycle_count": case["fixed_cycle_count"],
                "nclauses": rec.get("build", {}).get("nclauses"),
                "nvars": rec.get("build", {}).get("nvars"),
                "p": case["p"],
                "proof": rec.get("proof"),
                "solve_sec": rec.get("solve_sec"),
                "status": "UNSAT",
            })
        elif status == "SAT" and rec.get("model", {}).get("verified_55"):
            models.append(rec)
        elif status == "UNKNOWN":
            timeouts.append({
                "log": f"logs/{case['name']}_kissat.txt",
                "name": case["name"],
                "solve_sec": rec.get("solve_sec"),
                "status": "UNKNOWN",
            })
        else:
            pending.append(case["name"])

    summary = {
        "found_43_graph": bool(models),
        "interval_moved": bool(models),
        "models": models,
        "note": (
            "A stored DRAT is a restriction on a hypothetical (5,5,43)-graph "
            "automorphism. Isolated SAT timeouts are residue, not a bound. "
            "The published interval remains 43 <= R(5,5) <= 46 unless a "
            "decoded (5,5,43)-graph is stored."
        ),
        "pending": pending,
        "published_interval": [43, 46],
        "timeouts": timeouts,
        "unsat_representatives": verified,
        "unsat_by_prime": {
            str(p): [row["cycle_type"] + f" k={row['fixed_cycle_count']}"
                     for row in verified if row["p"] == p]
            for p in (2, 3, 5)
        },
    }
    Path("certs/q6_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({
        "found_43_graph": summary["found_43_graph"],
        "interval_moved": summary["interval_moved"],
        "pending": len(pending),
        "timeouts": len(timeouts),
        "unsat": len(verified),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
