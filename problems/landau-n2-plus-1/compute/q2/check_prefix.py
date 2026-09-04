#!/usr/bin/env python3
"""q2 lists must extend the committed N=10^6 prefix, not rewrite it."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent


def load_n(path: Path) -> list[int]:
    out: list[int] = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(int(s.split()[0]))
    return out


def main() -> None:
    parent_p = load_n(PARENT / "prime_n.txt")
    parent_p2 = load_n(PARENT / "p2_omega2.txt")
    q2_p = load_n(HERE / "prime_n.txt")
    q2_p2 = load_n(HERE / "p2_omega2.txt")
    if q2_p[: len(parent_p)] != parent_p:
        for i, (a, b) in enumerate(zip(q2_p, parent_p)):
            if a != b:
                sys.exit(f"prime prefix mismatch at {i}: q2={a} parent={b}")
        sys.exit(f"prime prefix length q2={len(q2_p)} parent={len(parent_p)}")
    if q2_p2[: len(parent_p2)] != parent_p2:
        for i, (a, b) in enumerate(zip(q2_p2, parent_p2)):
            if a != b:
                sys.exit(f"p2 prefix mismatch at {i}: q2={a} parent={b}")
        sys.exit(f"p2 prefix length q2={len(q2_p2)} parent={len(parent_p2)}")
    print(
        f"prefix OK: {len(parent_p)} primes and {len(parent_p2)} P2 rows "
        f"match the N=10^6 lists; q2 continues to {len(q2_p)} primes, {len(q2_p2)} P2"
    )


if __name__ == "__main__":
    main()
