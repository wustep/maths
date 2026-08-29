#!/usr/bin/env python3
"""Exact finite orders not implied by Hoàng–Reed or a numerical c."""

from __future__ import annotations

import json


# Exact orders already stored in q1 / q2 / q3 / q4 / q5 / q6 / q7 / q8 / q9 / q10 / q11 / q12 / q13 / q14 / q15 / q16 / q17 / q18 / q19 / q20 / q21 / q22 / q23 / q24 / q25 / q26 / q27 / q28 / q29 / q30 / q31 / q32 / q33 / q34 / q35 / q36 / q37 / q38 / q39 / q40. q41 starts at n=151.
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
CLOSED_BEFORE_Q11 = CLOSED_BEFORE_Q10 | {119}
CLOSED_BEFORE_Q12 = CLOSED_BEFORE_Q11 | {120}
CLOSED_BEFORE_Q13 = CLOSED_BEFORE_Q12 | {121}
CLOSED_BEFORE_Q14 = CLOSED_BEFORE_Q13 | {122}
CLOSED_BEFORE_Q15 = CLOSED_BEFORE_Q14 | {123}
CLOSED_BEFORE_Q16 = CLOSED_BEFORE_Q15 | {124}
CLOSED_BEFORE_Q17 = CLOSED_BEFORE_Q16 | {125}
CLOSED_BEFORE_Q18 = CLOSED_BEFORE_Q17 | {126}
CLOSED_BEFORE_Q19 = CLOSED_BEFORE_Q18 | {127}
CLOSED_BEFORE_Q20 = CLOSED_BEFORE_Q19 | {128}
CLOSED_BEFORE_Q21 = CLOSED_BEFORE_Q20 | {129}
CLOSED_BEFORE_Q22 = CLOSED_BEFORE_Q21 | {130}
CLOSED_BEFORE_Q23 = CLOSED_BEFORE_Q22 | {131}
CLOSED_BEFORE_Q24 = CLOSED_BEFORE_Q23 | {132}
CLOSED_BEFORE_Q25 = CLOSED_BEFORE_Q24 | {133}
CLOSED_BEFORE_Q26 = CLOSED_BEFORE_Q25 | {134}
CLOSED_BEFORE_Q27 = CLOSED_BEFORE_Q26 | {135}
CLOSED_BEFORE_Q28 = CLOSED_BEFORE_Q27 | {136}
CLOSED_BEFORE_Q29 = CLOSED_BEFORE_Q28 | {137}
CLOSED_BEFORE_Q30 = CLOSED_BEFORE_Q29 | {138}
CLOSED_BEFORE_Q31 = CLOSED_BEFORE_Q30 | {139}
CLOSED_BEFORE_Q32 = CLOSED_BEFORE_Q31 | {140}
CLOSED_BEFORE_Q33 = CLOSED_BEFORE_Q32 | {141}
CLOSED_BEFORE_Q34 = CLOSED_BEFORE_Q33 | {142}
CLOSED_BEFORE_Q35 = CLOSED_BEFORE_Q34 | {143, 144}
CLOSED_BEFORE_Q36 = CLOSED_BEFORE_Q35 | {145}
CLOSED_BEFORE_Q37 = CLOSED_BEFORE_Q36 | {146}
CLOSED_BEFORE_Q38 = CLOSED_BEFORE_Q37 | {147}
CLOSED_BEFORE_Q39 = CLOSED_BEFORE_Q38 | {148}
CLOSED_BEFORE_Q40 = CLOSED_BEFORE_Q39 | {149}
CLOSED_BEFORE_Q41 = CLOSED_BEFORE_Q40 | {150}


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


def remaining_after_q10(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q11]


def remaining_after_q11(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q12]


def remaining_after_q12(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q13]


def remaining_after_q13(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q14]


def remaining_after_q14(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q15]


def remaining_after_q15(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q16]


def remaining_after_q16(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q17]


def remaining_after_q17(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q18]


def remaining_after_q18(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q19]


def remaining_after_q19(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q20]


def remaining_after_q20(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q21]


def remaining_after_q21(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q22]


def remaining_after_q22(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q23]


def remaining_after_q23(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q24]


def remaining_after_q24(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q25]


def remaining_after_q25(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q26]


def remaining_after_q26(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q27]


def remaining_after_q27(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q28]


def remaining_after_q28(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q29]


def remaining_after_q29(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q30]


def remaining_after_q30(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q31]


def remaining_after_q31(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q32]


def remaining_after_q32(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q33]


def remaining_after_q33(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q34]


def remaining_after_q34(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q35]


def remaining_after_q35(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q36]


def remaining_after_q36(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q37]


def remaining_after_q37(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q38]


def remaining_after_q38(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q39]


def remaining_after_q39(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q40]


def remaining_after_q40(c: float = 0.34640, n_max: int = 160) -> list[dict]:
    return [row for row in open_orders(c, n_max=n_max) if row["n"] not in CLOSED_BEFORE_Q41]


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
    leftover = remaining_after_q40()
    rec = {
        "hkn_0.3465": open_orders(0.3465),
        "repo_f4_0.34645": open_orders(0.34645),
        "repo_f4_0.34640": open_orders(0.34640),
        "personal_0.3388": open_orders(0.3388),
        "remaining_after_q40": leftover,
        "n150": cube_range(150, 50),
        "n151": cube_range(151, 51),
        "n152": cube_range(152, 51),
        "note": (
            "An order is a hole when ceil(n/3) < c*n and ceil(n/3) > 5. "
            "q1 closed 18; q2 closed 21–36 leftover; q3 closed 38–72 leftover; "
            "q4 closed 73–108 leftover; q5 closed 109–114 leftover; "
            "q6 closed 115 leftover; q7 closed 116 leftover; "
            "q8 closed 117 leftover; q9 closed 118 leftover; "
            "q10 closed 119 leftover; q11 closed 120 leftover; "
            "q12 closed 121 leftover; q13 closed 122 leftover; "
            "q14 closed 123 leftover; q15 closed 124 leftover; "
            "q16 closed 125 leftover; q17 closed 126 leftover; "
            "q18 closed 127 leftover; q19 closed 128 leftover; "
            "q20 closed 129 leftover; "
            "q21 closed 130 leftover; "
            "q22 closed 131 leftover; "
            "q23 closed 132 leftover; "
            "q24 closed 133 leftover; "
            "q25 closed 134 leftover; "
            "q26 closed 135 leftover; "
            "q27 closed 136 leftover; "
            "q28 closed 137 leftover; "
            "q29 closed 138 leftover; "
            "q30 closed 139 leftover; "
            "q31 closed 140 leftover; "
            "q32 closed 141 leftover; "
            "q33 closed 142 leftover; "
            "q34 closed 143–144 leftover; "
            "q35 closed 145 leftover; "
            "q36 closed 146 leftover; "
            "q37 closed 147 leftover; "
            "q38 closed 148 leftover; "
            "q39 closed 149 leftover; "
            "q40 closed 150 leftover. "
            "First leftover for this folder is n=151, d=51."
        ),
    }
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
