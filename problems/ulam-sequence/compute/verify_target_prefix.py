#!/usr/bin/env python3
"""Direct integer check: a_n * 1000^n ≤ 1443^n on a generated prefix."""

from __future__ import annotations

import json
from pathlib import Path

from ulam import ulam_first

HERE = Path(__file__).resolve().parent


def first_failure(seq, num: int, den: int = 1000) -> int | None:
    pow_num = 1
    pow_den = 1
    for n, a in enumerate(seq, start=1):
        pow_num *= num
        pow_den *= den
        if a * pow_den > pow_num:
            return n
    return None


def main() -> None:
    seq = ulam_first(3304)
    fail443 = first_failure(seq, 1443)
    fail452 = first_failure(seq, 1452)
    rec = {
        "N": len(seq),
        "a_N": seq[-1],
        "first_fail_1.443": fail443,
        "first_fail_1.452": fail452,
        "all_ok_1.443": fail443 is None,
        "all_ok_1.452": fail452 is None,
    }
    (HERE / "target_prefix.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))
    if fail443 is not None or fail452 is not None:
        raise SystemExit("prefix failed the exponential target")


if __name__ == "__main__":
    main()
