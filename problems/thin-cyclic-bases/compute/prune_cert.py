#!/usr/bin/env python3
"""Greedy-delete points from a verified certificate. Independent of bel.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import is_sum_cover


def prune(n, A):
    A = set(int(x) % n for x in A)
    assert is_sum_cover(A, n)
    dropped = []
    for x in sorted(A, reverse=True):
        if x == 0:
            continue
        trial = A - {x}
        if is_sum_cover(trial, n):
            A = trial
            dropped.append(x)
    return sorted(A), dropped


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "compute/certs/bel_q13.json")
    rec = json.loads(path.read_text())
    n, A = rec["n"], rec["A"]
    kept, dropped = prune(n, A)
    print(
        f"{path.name} n={n} m0={len(set(A))} m={len(kept)} dropped={len(dropped)}"
    )
    if dropped:
        out = Path("compute/certs") / (path.stem + "_pruned.json")
        out.write_text(
            json.dumps(
                {
                    "family": rec.get("family", "") + "-pruned",
                    "source": path.name,
                    "n": n,
                    "m": len(kept),
                    "dropped": dropped,
                    "A": kept,
                },
                indent=2,
            )
        )
        print("wrote", out)


if __name__ == "__main__":
    main()
