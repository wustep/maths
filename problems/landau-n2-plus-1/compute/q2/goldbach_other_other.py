#!/usr/bin/env python3
"""Goldbach's other other conjecture on the certified prime_n list.

Grantham–Graves (arXiv:2502.03513) already checked this through
m^2+1 <= 6.25e28. This is only a consistency check of our prefix:
every a>1 with a^2+1 prime is b+c with both b,c in the same list.
Not a new bound.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_n(path: Path) -> list[int]:
    out: list[int] = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(int(s.split()[0]))
    return out


def main() -> None:
    A = load_n(HERE / "prime_n.txt")
    S = set(A)
    missing: list[int] = []
    max_j = 0
    champ = None
    for i, a in enumerate(A):
        if a == 1:
            continue
        ok = False
        j = 0
        for k in range(i - 1, -1, -1):
            j += 1
            if a - A[k] in S:
                ok = True
                if j > max_j:
                    max_j = j
                    champ = {"a": a, "b": A[k], "c": a - A[k], "j": j}
                break
        if not ok:
            missing.append(a)
    payload = {
        "n_terms": len(A),
        "n_max": A[-1] if A else None,
        "missing": missing,
        "max_j": max_j,
        "champion": champ,
        "note": (
            "Goldbach other-other on this prefix only. "
            "Grantham–Graves already verified it to 6.25e28. Not a new bound."
        ),
    }
    out = HERE / "goldbach_other_other.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} missing={len(missing)} max_j={max_j} champ={champ}")
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
