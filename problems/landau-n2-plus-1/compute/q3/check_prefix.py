#!/usr/bin/env python3
"""q3 lists must extend the certified N=10^7 q2 prefix, not rewrite it."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q2 = HERE.parent / "q2"


def load_n(path: Path) -> list[int]:
    out: list[int] = []
    with path.open() as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            out.append(int(s.split()[0]))
    return out


def prefix_ok(parent: list[int], child_path: Path, label: str) -> int:
    """Stream child; require the first len(parent) values to match. Return child length."""
    nchild = 0
    with child_path.open() as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            n = int(s.split()[0])
            if nchild < len(parent):
                if n != parent[nchild]:
                    sys.exit(f"{label} prefix mismatch at {nchild}: q3={n} q2={parent[nchild]}")
            nchild += 1
    if nchild < len(parent):
        sys.exit(f"{label} prefix length q3={nchild} q2={len(parent)}")
    return nchild


def main() -> None:
    parent_p = load_n(Q2 / "prime_n.txt")
    parent_p2 = load_n(Q2 / "p2_omega2.txt")
    n_p = prefix_ok(parent_p, HERE / "prime_n.txt", "prime")
    n_p2 = prefix_ok(parent_p2, HERE / "p2_omega2.txt", "p2")
    print(
        f"prefix OK: {len(parent_p)} primes and {len(parent_p2)} P2 rows "
        f"match the N=10^7 lists; q3 continues to {n_p} primes, {n_p2} P2"
    )


if __name__ == "__main__":
    main()
