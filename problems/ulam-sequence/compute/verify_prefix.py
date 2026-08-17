#!/usr/bin/env python3
"""Independently generate U(1,2) and match the OEIS A002858 b-file."""

from __future__ import annotations

import json
from pathlib import Path

from ulam import ulam_first, ulam_upto_value

HERE = Path(__file__).resolve().parent
BFILE = HERE / "b002858.txt"


def load_bfile(path: Path) -> list[int]:
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, a = line.split()
        out.append(int(a))
        if int(n) != len(out):
            raise ValueError(f"b-file index gap at n={n}")
    return out


def main() -> None:
    published = load_bfile(BFILE)
    k = len(published)
    got = ulam_first(k)
    mismatches = [(i + 1, published[i], got[i]) for i in range(k) if published[i] != got[i]]
    # Cross-check the two generators against each other on a value cutoff.
    cutoff = published[-1]
    by_value = ulam_upto_value(cutoff)
    report = {
        "oeis_terms": k,
        "oeis_last": published[-1],
        "generated_last": got[-1],
        "match_bfile": mismatches == [],
        "n_mismatch": len(mismatches),
        "first_mismatches": mismatches[:5],
        "value_cutoff_len": len(by_value),
        "two_generators_agree": by_value == got,
        "a_10": got[9] if k >= 10 else None,
        "a_100": got[99] if k >= 100 else None,
        "a_1000": got[999] if k >= 1000 else None,
        "a_10000": got[9999] if k >= 10000 else None,
    }
    out = HERE / "prefix_verify.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if mismatches or not report["two_generators_agree"]:
        raise SystemExit("prefix verification FAILED")
    print("OK: independent prefix matches OEIS A002858 b-file (10 000 terms).")


if __name__ == "__main__":
    main()
