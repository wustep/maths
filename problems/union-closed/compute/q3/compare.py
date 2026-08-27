"""Compare the q3 analytic, Python, and C certificates."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def load(name: str):
    return json.loads((CERTS / name).read_text())


def main():
    analytic = load("analytic_margin.json")
    probe = load("joint_star.json")
    python = load("python_mesh.json")
    cmesh = load("c_mesh.json")

    pa = python["at"]
    ca = cmesh["at"]
    checks = {
        "analytic_replay_ok": analytic.get("all_ok") is True,
        "failed_joint_handle_replays": probe.get("all_ok") is True,
        "python_replay_ok": python.get("all_ok") is True,
        "c_replay_ok": cmesh.get("all_ok") is True,
        "claimed_constant_matches": python["claimed_c"] == cmesh["claimed_c"] == 0.38305,
        "grid_dimensions_match": (
            python["grid"]["n_b"] == cmesh["grid"]["n_b"] == 9000
            and python["grid"]["n_a"] == cmesh["grid"]["n_a"] == 7000
        ),
        "retained_cell_counts_match": (
            python["grid"]["retained_cells"] == cmesh["grid"]["retained_cells"]
        ),
        "minimum_ratios_match": abs(python["min_ratio"] - cmesh["min_ratio"]) < 5e-15,
        "minimum_indices_match": pa["i_b"] == ca["i_b"] and pa["i_a"] == ca["i_a"],
        "minimum_coordinates_match": (
            abs(pa["b"] - ca["b"]) < 5e-15
            and abs(pa["a"] - ca["a"]) < 5e-15
            and abs(pa["mean"] - ca["mean"]) < 5e-15
        ),
        "both_minima_strictly_above_1": (
            python["min_ratio"] > 1.0 and cmesh["min_ratio"] > 1.0
        ),
        "both_have_zero_bad_cells": (
            python["n_bad_cells"] == 0 and cmesh["n_bad_cells"] == 0
        ),
        "claim_below_analytic_crossing": analytic["crossing_float"] > 0.38305,
        "claim_strictly_beats_q1": 0.38305 > 0.38304,
        "claim_strictly_beats_liu": 0.38305 > analytic["liu_quote"],
    }
    report = {
        "status": "dent",
        "record_inequality": analytic["record_inequality"],
        "claimed_c": 0.38305,
        "analytic_crossing": analytic["crossing"],
        "crossing_minus_claimed": analytic["crossing_minus_claimed"],
        "grid": python["grid"],
        "python": {
            "algorithm": python["implementation"],
            "min_ratio": python["min_ratio"],
            "n_bad_cells": python["n_bad_cells"],
            "at": pa,
        },
        "c": {
            "algorithm": cmesh["implementation"],
            "min_ratio": cmesh["min_ratio"],
            "n_bad_cells": cmesh["n_bad_cells"],
            "at": ca,
        },
        "joint_star_probe": {
            "interior_equality_b": probe["interior_equality_b"],
            "note": probe["note"],
        },
        "checks": checks,
        "all_ok": all(checks.values()),
        "scope": (
            "pure Liu Example 4 on the two-point family {b,1}; "
            "the every-measure and 1/2 statements remain open"
        ),
    }
    path = CERTS / "certificate.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
