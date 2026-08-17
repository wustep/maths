#!/usr/bin/env python3
"""Re-derive the prime list from n2p1.json without trusting it."""
from __future__ import annotations
import json
import sys
from pathlib import Path

from sieve_n2p1 import miller_rabin

HERE = Path(__file__).resolve().parent


def main() -> None:
    data = json.loads((HERE / "n2p1.json").read_text())
    n_max = int(data["n_max"])
    claimed = set(int(x) for x in data["prime_n"])
    found: list[int] = []
    if n_max >= 1 and miller_rabin(2):
        found.append(1)
    for n in range(2, n_max + 1, 2):
        if miller_rabin(n * n + 1):
            found.append(n)
    extra = [n for n in claimed if n not in set(found)]
    missing = [n for n in found if n not in claimed]
    print(f"n_max={n_max} claimed={len(claimed)} found={len(found)} extra={len(extra)} missing={len(missing)}")
    if extra[:10]:
        print("extra sample", extra[:10])
    if missing[:10]:
        print("missing sample", missing[:10])
    if extra or missing:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
