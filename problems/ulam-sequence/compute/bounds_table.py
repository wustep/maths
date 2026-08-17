#!/usr/bin/env python3
"""Assemble the CS-majorant table and exact N0 comparisons."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Exhaustive max ||W||_F^2, independently recomputed (C + Python for L≤16).
F2 = {
    0: 1,
    1: 5,
    2: 9,
    3: 18,
    4: 37,
    5: 69,
    6: 144,
    7: 280,
    8: 580,
    9: 1150,
    10: 2308,
    11: 4710,
    12: 9252,
    13: 18748,
    14: 37602,
    15: 75172,
    16: 150408,
    17: 301572,
    18: 607022,
    19: 1202020,
    20: 2417294,
    21: 4845788,
    22: 9690750,
}

WORDS = {
    1: "1",
    2: "21",
    3: "231",
    4: "2313",
    5: "23131",
    6: "231313",
    7: "2313131",
    8: "23131313",
    9: "231313113",
    10: "2313131313",
    11: "23131311313",
    12: "231313131313",
    13: "2313131131313",
    14: "23131311311313",
    15: "231313113131313",
    16: "2313131131311313",
    17: "23131311311311313",
    18: "231313113131311313",
    19: "2313131131313131313",
    20: "23131311311311311313",
    21: "231313113113131311313",
    22: "2313131131313131311313",
}

C2 = {
    15: 1.4539022020434931,
    16: 1.4514086807307693,
    17: 1.4493008896499420,
    18: 1.4475866437807043,
    19: 1.4454320349168224,
    20: 1.4440533448508110,
}


def beats(F2L: int, L: int, num: int, den: int = 1000) -> bool:
    return F2L * (den ** (2 * L)) < num ** (2 * L)


def majorant_ok(L: int, q: int, r: int, num: int, den: int = 1000) -> bool:
    """||v_{5+Lq+r}||_2^2 ≤ F2[L]^q * F2[r] * 65  vs  (num/den)^{2n}."""
    n = 5 + L * q + r
    left = (F2[L] ** q) * F2[r] * 65 * (den ** (2 * n))
    right = num ** (2 * n)
    return left <= right


def find_N0(L: int, num: int, den: int = 1000, qmax: int = 800) -> dict:
    """Incremental integer scan.  n = 5 + Lq + r."""
    # bases at r=0: left = F2[L]^q * 1 * 65 * den^{2(5+Lq)}, right = num^{2(5+Lq)}
    left_base = 65 * (den ** 10)
    right_base = num ** 10
    first_full = None
    last_fail_n = None
    for q in range(0, qmax + 1):
        left = left_base
        right = right_base
        all_ok = True
        for r in range(L):
            if r > 0:
                left = left_base * F2[r] * (den ** (2 * r))
                right = right_base * (num ** (2 * r))
            ok = left <= right
            if not ok:
                all_ok = False
                last_fail_n = 5 + L * q + r
        if all_ok:
            first_full = q
            break
        left_base *= F2[L] * (den ** (2 * L))
        right_base *= num ** (2 * L)
    if first_full is None:
        return {"ok": False, "qmax": qmax, "last_fail_n": last_fail_n}
    N0 = 5 if last_fail_n is None else last_fail_n + 1
    return {
        "ok": True,
        "L": L,
        "target": f"{num}/{den}",
        "first_full_q": first_full,
        "N0": N0,
        "last_fail_n": last_fail_n,
        "C_F": F2[L] ** (0.5 / L),
    }


def main() -> None:
    table = []
    for L in range(1, 23):
        table.append(
            {
                "L": L,
                "F2": F2[L],
                "CF": F2[L] ** (0.5 / L),
                "C2": C2.get(L),
                "wordF": WORDS[L],
                "beats_1.454": beats(F2[L], L, 1454),
                "beats_1.452": beats(F2[L], L, 1452),
                "beats_1.445": beats(F2[L], L, 1445),
                "beats_1.443": beats(F2[L], L, 1443),
                "beats_1.442": beats(F2[L], L, 1442),
            }
        )
    n0_16 = find_N0(16, 1452)
    n0_21 = find_N0(21, 1443)
    n0_22 = find_N0(22, 1442)
    rec = {
        "published_CS": 1.454,
        "eggleton": 1.4655712318767682,
        "barrier": 1.4146717609798722,
        "table": table,
        "N0_L16_1452": n0_16,
        "N0_L21_1443": n0_21,
        "N0_L22_1442": n0_22,
        "v5_sq": 65,
        "note": (
            "CF = (max ||W||_F^2)^{1/(2L)} is an exact integer-power quantity. "
            "N0 is the first index from which the CS majorant started at "
            "v_5=(6,4,3,2) is ≤ (p/1000)^n by integer comparison."
        ),
    }
    out = HERE / "bounds_table.json"
    out.write_text(json.dumps(rec, indent=2) + "\n")
    print("L  CF            beats 1.454 / 1.452 / 1.445 / 1.443 / 1.442")
    for row in table:
        print(
            f"{row['L']:2d} {row['CF']:.12f}  "
            f"{row['beats_1.454']} {row['beats_1.452']} "
            f"{row['beats_1.445']} {row['beats_1.443']} {row['beats_1.442']}"
        )
    print("N0 L=16 vs 1.452", n0_16)
    print("N0 L=21 vs 1.443", n0_21)
    print("N0 L=22 vs 1.442", n0_22)


if __name__ == "__main__":
    main()
