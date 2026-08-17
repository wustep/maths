#!/usr/bin/env python3
"""Independent verifier for cyclic sum-cover certificates.

Does not import constructions.py / bel.py / singer.py. Recomputes
A+A from the listed set and checks |A+A|=n.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def counting_lower(n: int) -> int:
    return math.ceil((-1 + math.sqrt(1 + 8 * n)) / 2)


def is_sum_cover(A, n: int) -> bool:
    seen = bytearray(n)
    Al = [int(a) % n for a in A]
    # unique
    Al = list(dict.fromkeys(Al))
    for i, a in enumerate(Al):
        seen[(a + a) % n] = 1
        for b in Al[i + 1 :]:
            seen[(a + b) % n] = 1
    return sum(seen) == n


def verify_file(path: Path) -> dict:
    rec = json.loads(path.read_text())
    n = int(rec["n"])
    A = rec["A"]
    m = len(set(int(a) % n for a in A))
    ok = is_sum_cover(A, n)
    ratio = m / math.sqrt(n)
    return {
        "path": str(path),
        "n": n,
        "m": m,
        "claimed_m": rec.get("m"),
        "ok": ok,
        "ratio": ratio,
        "counting": counting_lower(n),
        "sqrt2": math.sqrt(2),
        "sqrt8_3": math.sqrt(8 / 3),
        "sqrt3": math.sqrt(3),
        "beat_bel": ok and ratio < math.sqrt(8 / 3),
        "beat_sqrt2": ok and ratio <= math.sqrt(2) + 1e-12,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--dir", default="compute/certs")
    args = ap.parse_args()
    paths = [Path(p) for p in args.paths]
    if not paths:
        paths = sorted(Path(args.dir).glob("*.json"))
    if not paths:
        print("no certificates", file=sys.stderr)
        sys.exit(2)
    bad = 0
    rows = []
    for p in paths:
        r = verify_file(p)
        rows.append(r)
        flag = "OK" if r["ok"] else "FAIL"
        print(
            f"{flag} {p.name} n={r['n']} m={r['m']} ratio={r['ratio']:.5f} "
            f"count={r['counting']} beat_bel={r['beat_bel']}"
        )
        if not r["ok"]:
            bad += 1
    Path("compute/verify_report.json").write_text(json.dumps(rows, indent=2))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
