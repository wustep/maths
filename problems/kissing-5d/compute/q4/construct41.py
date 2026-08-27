#!/usr/bin/env python3
"""Algebraic 41-point hunts outside the leftover (1/4)Z^5 and T^5 graphs.

Pools, all exact:

- (1/3)Z^5, (1/5)Z^5, (1/6)Z^5: same-missed groups, then mixed U-slices,
  and a 40-colouring attempt (D5 is a 40-clique).
- Q(√2) / Q(√5) orbits that are not the q3 golden (φ,1,1/φ,0,0) pool.
- A5 in the sum-zero hyperplane of R^6, plus integer extras (d=1,2,3).
- Projections of D6's 60 roots onto exact 5-spaces.
- Layer-swaps of Q5 and R5 (q2 already did D5 and L5).
- Regular 5-simplex (size 6) as the cyclic/simplex box.

A hit is written to certs/code41.json.  An incomplete clique search is
residue, not a lower bound.
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run_mod(name: str) -> dict:
    path = HERE / f"{name}.py"
    print(f"---- {name} ----", flush=True)
    runpy.run_path(str(path), run_name="__main__")
    jpath = HERE / f"{name}.json"
    if jpath.exists():
        return json.loads(jpath.read_text())
    return {"present": False}


def best_of(report: dict) -> int:
    if not report:
        return 0
    if "best" in report and isinstance(report["best"], int):
        return report["best"]
    if "best_kissing_size" in report:
        return int(report["best_kissing_size"] or 0)
    if "best_total" in report:
        return int(report["best_total"] or 0)
    best = 0
    for v in report.values():
        if isinstance(v, dict):
            best = max(best, best_of(v))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    best = max(best, best_of(item))
    return best


def main() -> int:
    parts = {}
    for name in (
        "same_missed",
        "color_sphere",
        "mixed_slices",
        "quadratic_orbits",
        "a5_hyper",
        "proj_d6",
        "qr_reflect",
    ):
        parts[name] = run_mod(name)

    found = False
    code = HERE / "certs" / "code41.json"
    if code.exists():
        found = True
    for rec in parts.values():
        if isinstance(rec, dict) and rec.get("found_41"):
            found = True

    best = 40
    for rec in parts.values():
        best = max(best, best_of(rec))

    complete_flags = []
    for rec in parts.values():
        if isinstance(rec, dict) and "complete" in rec:
            complete_flags.append(bool(rec["complete"]))

    report = {
        "found_41": found,
        "best": best,
        "complete": bool(complete_flags) and all(complete_flags) and not found,
        "parts": {k: _strip(v) for k, v in parts.items()},
        "comment": (
            "No 41-point code in the pools that finished.  A skipped or "
            "incomplete search is residue, not a lower bound.  Did not "
            "touch the leftover (1/4)Z^5 1480-graph or the T^5 355-remainder."
        ),
    }
    if found:
        report["comment"] = (
            "A 41-point spherical code was written to certs/code41.json. "
            "Replay: python3 verify.py and the independent C verifier."
        )
    (HERE / "construct41.json").write_text(json.dumps(report, indent=2) + "\n")
    print("found_41", report["found_41"], "best", report["best"])
    return 0


def _strip(obj, depth=0):
    if depth > 4:
        return None
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("clique", "clique41", "hit", "hit_int", "colouring",
                     "colouring_extras", "points", "roots"):
                continue
            out[k] = _strip(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [_strip(x, depth + 1) for x in obj[:20]]
    return obj


if __name__ == "__main__":
    raise SystemExit(main())
