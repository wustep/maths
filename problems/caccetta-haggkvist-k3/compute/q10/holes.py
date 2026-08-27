#!/usr/bin/env python3
"""Exact finite orders not implied by Hoàng–Reed or a numerical c."""

from __future__ import annotations

import json


# Exact orders already stored in q1 / q2 / q3 / q4 / q5 / q6 / q7 / q8 / q9. q10 starts at n=119.
CLOSED_BEFORE_Q4 = {
    12,
    15,
    16,
    17,
    18,
    21,
    24,
    26,
    27,
    29,
    30,
    32,
    33,
    35,
    36,
    38,
    39,
    41,
    42,
    44,
    45,
    47,
    48,
    *range(50, 73),
}

CLOSED_BEFORE_Q5 = CLOSED_BEFORE_Q4 | set(range(73, 109))
CLOSED_BEFORE_Q6 = CLOSED_BEFORE_Q5 | set(range(109, 115))
CLOSED_BEFORE_Q7 = CLOSED_BEFORE_Q6 | {115}
CLOSED_BEFORE_Q8 = CLOSED_BEFORE_Q7 | {116}
CLOSED_BEFORE_Q9 = CLOSED_BEFORE_Q8 | {117}
CLOSED_BEFORE_Q10 = CLOSED_BEFORE_Q9 | {118}


def ceil_div(n: int, k: int) -> int:
    return (n + k - 1) // k


def open_orders(c: float, n_max: int = 160, hoang_reed_r: int = 5) -> list[dict]:
    rows = []
    for n in range(1, n_max + 1):
        d = ceil_div(n, 3)
        if d <= hoang_reed_r:
            continue
        if d >= c * n:
            continue
        rows.append(
            {
                "n": n,
                "d": d,
                "c_n": c * n,
                "gap": c * n - d,
            }
        )
    return rows


def remaining_after_q3(c: float = 0.34645, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q4]


def remaining_after_q4(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q5]


def remaining_after_q5(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q6]


def remaining_after_q6(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q7]


def remaining_after_q7(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q8]


def remaining_after_q8(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q9]


def remaining_after_q9(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q10]


def cube_range(n: int, d: int) -> dict:
    """Pigeonhole plus the N⁺ counting cut.

    n*d arcs ⇒ some in-degree ≥ d.  Each v ∈ N⁺(0) needs d out-neighbours
    from (N⁺(0)\\{v}) ∪ U, size (d-1) + (n-1-d-k) = n-2-k.  Need
    n-2-k ≥ d, so k ≤ n-2-d.  The absolute maximum is n-1-d.
    """
    k_min = d
    k_abs = n - 1 - d
    k_count = n - 2 - d
    return {
        "n": n,
        "d": d,
        "arcs": n * d,
        "mean_indeg": d,
        "k_min_pigeonhole": k_min,
        "k_max_absolute": k_abs,
        "k_max_count": k_count,
        "needed_cubes": list(range(k_min, min(k_abs, k_count) + 1)),
        "empty_by_count": list(range(k_count + 1, k_abs + 1)),
    }


def main():
    leftover = remaining_after_q9()
    rec = {
        "hkn_0.3465": open_orders(0.3465),
        "repo_f4_0.34645": open_orders(0.34645),
        "repo_f4_0.34640": open_orders(0.34640),
        "personal_0.3388": open_orders(0.3388),
        "remaining_after_q9": leftover,
        "n119": cube_range(119, 40),
        "n120": cube_range(120, 40),
        "n121": cube_range(121, 41),
        "note": (
            "An order is a hole when ceil(n/3) < c*n and ceil(n/3) > 5. "
            "q1 closed 18; q2 closed 21–36 leftover; q3 closed 38–72 leftover; "
            "q4 closed 73–108 leftover; q5 closed 109–114 leftover; "
            "q6 closed 115 leftover; q7 closed 116 leftover; "
            "q8 closed 117 leftover; q9 closed 118 leftover. "
            "First leftover for this folder is n=119, d=40."
        ),
    }
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
