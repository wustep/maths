#!/usr/bin/env python3
"""Collect q3's checked order-7 exclusions and remaining timeouts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASES = [
    {"cycles": 1, "fixed_cycle_count": 1, "covers_k": [0, 1], "solver": "kissat --unsat --seed=17"},
    {"cycles": 2, "fixed_cycle_count": 1, "covers_k": [1], "solver": "kissat --plain"},
    {"cycles": 2, "fixed_cycle_count": 2, "covers_k": [0, 2], "solver": "kissat --plain"},
    {"cycles": 3, "fixed_cycle_count": 1, "covers_k": [1, 2], "solver": "kissat --plain"},
    {"cycles": 3, "fixed_cycle_count": 3, "covers_k": [0, 3], "solver": "kissat --plain"},
    {"cycles": 4, "fixed_cycle_count": 1, "covers_k": [1, 3], "solver": "kissat --plain"},
    {"cycles": 4, "fixed_cycle_count": 2, "covers_k": [2], "solver": "kissat --plain"},
    {"cycles": 5, "fixed_cycle_count": 2, "covers_k": [2, 3], "solver": "kissat --plain"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    direct = []
    for template in CASES:
        row = dict(template)
        name = f"p7_c{row['cycles']}_k{row['fixed_cycle_count']}"
        build = json.loads((Path("certs") / f"{name}_build.json").read_text())
        proof = Path("certs/proofs") / f"{name}.drat.gz"
        check_log = Path("logs") / f"{name}_drat.txt"
        if "s VERIFIED" not in check_log.read_text():
            raise RuntimeError(f"unchecked direct proof: {name}")
        row.update(
            {
                "cnf_sha256": build["cnf_sha256"],
                "fixed": build["fixed"],
                "nclauses": build["nclauses"],
                "nvars": build["nvars"],
                "proof": {
                    "bytes": proof.stat().st_size,
                    "path": str(proof),
                    "sha256": sha256(proof),
                },
                "proof_verified": True,
                "status": "UNSAT",
            }
        )
        direct.append(row)

    composite = json.loads(Path("certs/p7_proofs.json").read_text())
    maximum = json.loads(Path("certs/p7_neighborhoods.json").read_text())
    timeouts = []
    for name in (
        "p5_c8_k4_plain",
        "p3_c14_k6_plain",
        "p3_c14_k7_plain",
        "p2_c21_k9_plain",
        "p2_c21_k10_plain",
    ):
        log = Path("logs") / f"{name}.txt"
        status = "UNKNOWN" if "s UNKNOWN" in log.read_text() else "UNEXPECTED"
        timeouts.append({"log": str(log), "status": status})

    summary = {
        "found_43_graph": False,
        "automorphism_order_7": {
            "all_cycle_types_excluded": True,
            "complement_rule": "k is paired with cycles-k; fixed vertices are relabelled before the fixed-cycle prefix is imposed",
            "direct_cycle_type_representatives": direct,
            "maximum_cycle_type": {
                "build": json.loads(Path("certs/p7_c6_k3_build.json").read_text()),
                "completion_cnf_sha256": maximum["completion_cnf_sha256"],
                "conquer_proofs": composite,
                "cycles": 6,
                "fixed": 1,
                "fixed_cycle_count": 3,
                "neighborhood_assignments": maximum["total"],
                "neighborhood_rows_sha256": maximum["rows_sha256"],
                "status": "UNSAT",
            },
        },
        "hypothetical_automorphism_prime_divisors_after_q2_q3": [2, 3, 5],
        "interval_moved": False,
        "note": "Order 7 is excluded only as an automorphism order of a hypothetical (5,5,43)-graph. This is not a bound on R(5,5). Orders 2, 3, and 5 remain open.",
        "published_interval": [43, 46],
        "timeouts": timeouts,
    }
    Path("certs/q3_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"order7_excluded": True, "interval_moved": False, "timeouts": len(timeouts)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
