#!/usr/bin/env python3
"""Independent q2 audit: no imports from an encoder or search program."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from time import monotonic


HERE = Path(__file__).resolve().parent


def read_colors(path: Path) -> list[int]:
    colors = [int(token) for token in path.read_text(encoding="ascii").split()]
    if not colors or any(color not in range(7) for color in colors):
        raise ValueError(f"malformed seven-color file: {path}")
    return colors


def violations(colors: list[int]) -> tuple[int, list[list[int]]]:
    result: list[list[int]] = []
    checked = 0
    n = len(colors)
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            checked += 1
            z = x + y
            if colors[x - 1] == colors[y - 1] == colors[z - 1]:
                result.append([x, y, z, colors[x - 1]])
    return checked, result


def final_event(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        data = data[-1]
    if not isinstance(data, dict):
        raise ValueError(f"unexpected log shape: {path}")
    return data


def main() -> None:
    started = monotonic()
    coloring_audits: dict[str, object] = {}
    for name in (
        "near1697.txt",
        "q2-best-cyclic144.txt",
        "q2-best-four-split.txt",
        "q2-best-six-split.txt",
        "q2-best-direct.txt",
    ):
        path = HERE / name
        colors = read_colors(path)
        checked, bad = violations(colors)
        coloring_audits[name] = {
            "length": len(colors),
            "class_sizes": [Counter(colors)[color] for color in range(7)],
            "pairs_checked": checked,
            "valid": not bad,
            "violation_count": len(bad),
            "violations": bad,
        }

    witness_path = HERE / "coloring1697-q2.txt"
    witness: dict[str, object]
    if witness_path.exists():
        colors = read_colors(witness_path)
        checked, bad = violations(colors)
        witness = {
            "exists": True,
            "length": len(colors),
            "pairs_checked": checked,
            "valid": len(colors) >= 1697 and not bad,
            "violations": bad,
        }
    else:
        witness = {"exists": False, "valid": False}

    logs: dict[str, object] = {}
    for name in (
        "q2-exact-cadical195-m144.json",
        "q2-exact-cadical300-split493-712.json",
        "q2-cegar1696-long.json",
        "q2-cegar1697.json",
    ):
        path = HERE / name
        if path.exists():
            logs[name] = final_event(path)

    audit = {
        "quest": "q2-second-pass",
        "result": "verified-witness" if witness["valid"] else "residue-no-witness",
        "witness": witness,
        "near_coloring_audits": coloring_audits,
        "search_log_final_events": logs,
        "elapsed_seconds": round(monotonic() - started, 6),
        "warning": "A timeout/interruption and per-seed UNSAT results are not an unrestricted UNSAT result.",
    }
    destination = HERE / "q2-independent-audit.json"
    destination.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, sort_keys=True))
    if witness["exists"] and not witness["valid"]:
        raise RuntimeError("a purported q2 witness exists but failed independent audit")


if __name__ == "__main__":
    main()
