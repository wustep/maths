#!/usr/bin/env python3
"""Independent replay of compute/a3_cert.json.

Does not import certify_a3.py. Recomputes the danger zone from m,k
and checks every stored witness by integer arithmetic only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def check(path: str) -> None:
    data = json.loads(Path(path).read_text())
    m_max = data["m_max"]
    witnesses = {w[0]: (w[1], w[2], w[3]) for w in data["witnesses"]}
    unsaved = data["unsaved"]
    if unsaved:
        raise SystemExit(f"FAIL: certificate lists unsaved {unsaved}")

    n_checked = 0
    missing = []
    bad = []

    for m in range(1, m_max + 1):
        k_lo = max(1, 2 * m - 2)
        k_hi = 3 * m + 2
        for k in range(k_lo, k_hi + 1):
            if (m * m + k) % 2:
                continue
            u = (m * m + k) // 2
            if u < 1:
                continue
            n = u * u + m * m + 1
            if n < 92:
                continue
            mn = min(2 * m, k)
            if (mn + 3) ** 4 < 64 * n:
                continue
            n_checked += 1
            if n not in witnesses:
                missing.append(n)
                continue
            a, b, s = witnesses[n]
            if a * a + b * b != s:
                bad.append((n, "not_sum_of_squares", a, b, s))
                continue
            if s < n:
                bad.append((n, "s_below_n", s))
                continue
            leftover = s - n
            if (leftover + 3) ** 4 >= 64 * n:
                bad.append((n, "leftover_too_big", leftover, s))

    # Named exceptions: confirm they really fail a=3 and succeed a=2.
    exceptions = {
        3: 1,  # next two-square 4
        6: 2,  # 8
        21: 4,  # 25
        91: 6,  # 97
    }
    exc_ok = True
    for n, g in exceptions.items():
        if (g + 3) ** 4 < 64 * n:
            print(f"WARN: exception n={n} actually satisfies a=3")
            exc_ok = False
        if (g + 2) ** 4 < 64 * n:
            pass  # a=2 holds (leftover < Phi-2)
        else:
            print(f"WARN: exception n={n} also fails a=2")

    print(
        json.dumps(
            {
                "path": path,
                "m_max": m_max,
                "n_checked": n_checked,
                "n_witnesses": len(witnesses),
                "n_missing": len(missing),
                "n_bad": len(bad),
                "missing_head": missing[:10],
                "bad_head": bad[:10],
                "exceptions_fail_a3": exc_ok,
                "ok": (not missing) and (not bad) and (n_checked == len(witnesses)),
            },
            indent=2,
        )
    )
    if missing or bad or n_checked != len(witnesses):
        raise SystemExit(1)


if __name__ == "__main__":
    check(sys.argv[1] if len(sys.argv) > 1 else "compute/a3_cert.json")
