#!/usr/bin/env python3
"""Independent replay of Hladký–Král'–Norin, Combinatorica 37 (2017).

Reconstructs the linear form F(c, r) on 32 type-densities of triangle-free
oriented graphs on 4 vertices, from the published matrices (Tables 1–2 and
(4.14)–(4.15), (4.7) fork identity) and the published test vectors a1..a4, b,
cT, cV, d.

A vector r in the simplex with F(c, r) having every coordinate negative
certifies that R(c) is empty, hence every triangle-free oriented graph satisfies
δα < c.

This file does not trust the printed expansion (4.22); it rebuilds F from the
pieces.  Run:

    python3 hkn_replay.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "certs"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Published test vectors (HKN Proposition 4.9)
# ---------------------------------------------------------------------------
A_VECS = [
    (-69.83, -27.04, 3.45, -53.59, 1.74, 28.78, -9.28, 59.66),
    (-44.57, -25.93, -24.40, -30.16, 2.40, 5.40, 15.67, 37.27),
    (86.95, 58.70, 35.15, 52.46, -18.52, 3.32, -52.56, -57.83),
    (-1.29, 0.17, 57.48, -26.29, 10.28, 26.90, -27.33, -9.15),
]
B_VEC = (
    0,
    0,
    -17448,
    -16496,
    26501,
    -24163,
    -8929,
    -54193,
    -30136,
    7267,
    -24582,
    -42769,
    22644,
    0,
)
CT = 39648.0
CV = 19877.0
D_FORK = 2078.0
HKN_C = 0.3465

# ---------------------------------------------------------------------------
# AC(Ψ): 8×8 symmetric, entries linear in (Ψ_0 … Ψ_31).
# Stored as a list of 8×8 matrices M_k, so AC(r) = sum_k r_k M_k.
# Transcribed from HKN Table 1.
# ---------------------------------------------------------------------------

# Each entry is a dict {k: coeff} meaning coeff * Ψ_k.
_AC_UPPER = {
    (0, 0): {1: 2, 10: 4},
    (0, 1): {3: 1, 11: 1, 15: 1},
    (0, 2): {2: 2, 11: 1, 12: 1},
    (0, 3): {4: 2, 12: 1, 17: 1},
    (0, 4): {9: 1, 13: 1, 18: 1},
    (0, 5): {9: 1, 14: 1, 19: 1},
    (0, 6): {3: 1, 15: 1, 17: 1},
    (0, 7): {9: 1, 16: 1, 20: 1},
    (1, 1): {7: 2, 16: 2},
    (1, 2): {6: 2, 14: 1},
    (1, 3): {17: 1, 23: 1, 25: 2},
    (1, 4): {19: 1, 24: 1, 27: 1},
    (1, 5): {18: 1, 27: 1},
    (1, 6): {15: 1, 23: 1, 28: 4},
    (1, 7): {18: 1, 29: 1},
    (2, 2): {5: 6, 13: 2},
    (2, 3): {12: 1, 21: 4, 23: 1},
    (2, 4): {14: 1, 22: 2},
    (2, 5): {13: 1, 22: 2, 24: 1},
    (2, 6): {11: 1, 23: 1, 25: 2},
    (2, 7): {13: 1, 24: 1, 26: 2},
    (3, 3): {8: 6, 20: 2},
    (3, 4): {20: 1, 26: 2, 29: 1},
    (3, 5): {20: 1, 29: 1, 30: 2},
    (3, 6): {7: 2, 19: 1},
    (3, 7): {19: 1, 30: 2},
    (4, 4): {30: 2, 31: 2},
    (4, 5): {29: 1, 31: 1},
    (4, 6): {16: 1, 24: 1},
    (4, 7): {27: 1, 31: 1},
    (5, 5): {26: 2, 31: 2},
    (5, 6): {16: 1, 27: 1},
    (5, 7): {24: 1, 31: 1},
    (6, 6): {6: 2, 18: 2},
    (6, 7): {14: 1, 27: 1, 29: 1},
    (7, 7): {22: 2, 31: 2},
}


def ac_slices() -> list[list[list[float]]]:
    """Return [M_0, …, M_31], each M_k an 8×8 symmetric matrix."""
    Ms = [[[0.0] * 8 for _ in range(8)] for _ in range(32)]
    for (i, j), terms in _AC_UPPER.items():
        for k, coeff in terms.items():
            Ms[k][i][j] += coeff
            if i != j:
                Ms[k][j][i] += coeff
    return Ms


# ---------------------------------------------------------------------------
# AR, BR: 14 × 32, transcribed from HKN Table 2.
# ---------------------------------------------------------------------------
AR = [
    [12, 6, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 0, 0, 0, 0, 3, 4, 2, 2, 1, 1, 2, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 2, 2, 2, 0, 0, 0, 0, 3, 4, 2, 2, 1, 1, 2, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 6, 2, 0, 0, 0, 0, 2, 2, 4, 2, 0, 0, 0, 0, 0, 0, 4, 4, 2, 2, 2, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 2, 2, 0, 0, 0, 1, 0, 0, 1, 2, 2, 1, 2, 1, 0, 0, 0, 2, 1, 2, 0, 2, 4, 1, 0, 0],
    [0, 2, 2, 2, 2, 0, 0, 0, 0, 3, 4, 2, 2, 1, 1, 2, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 2, 2, 0, 0, 0, 1, 0, 0, 1, 2, 2, 1, 2, 1, 0, 0, 0, 2, 1, 2, 0, 2, 4, 1, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 2, 6, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 2, 4, 4, 0, 2, 0, 2, 2, 0, 0, 2, 4, 0],
    [0, 0, 0, 0, 1, 0, 0, 1, 3, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 2, 0, 1, 0, 1, 1, 0, 0, 1, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 2, 0, 2, 0, 2, 2, 0, 2, 2, 4],
    [0, 0, 0, 1, 0, 0, 2, 2, 0, 0, 0, 1, 0, 0, 1, 2, 2, 1, 2, 1, 0, 0, 0, 2, 1, 2, 0, 2, 4, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 2, 0, 2, 0, 2, 2, 0, 2, 2, 4],
    [0, 0, 1, 0, 0, 3, 1, 0, 0, 0, 0, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 2, 0, 2, 0, 2, 2, 0, 2, 2, 4],
]

BR = [
    [0, 1, 2, 1, 0, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 4, 4, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 2, 0, 2, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 2, 2, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 2, 2, 3],
    [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 2, 2],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
]


def _check_shapes() -> None:
    assert len(AR) == 14 and all(len(row) == 32 for row in AR)
    assert len(BR) == 14 and all(len(row) == 32 for row in BR)
    assert len(B_VEC) == 14
    assert all(len(a) == 8 for a in A_VECS)


# ---------------------------------------------------------------------------
# IndT, IndV: coefficients of (const + linear-in-c) for each r_k.
# From HKN (4.14) and (4.15).  We store (const_coeff, c_coeff) per index
# so Ind = sum_k (p_k + q_k c) r_k.
#
# 24 Ψ([[f(T)]]) = IndT:
#   (1-c) r9 - c r13 - c r14 - c r16 + (1-c) r18 + (1-c) r19 + (1-c) r20
#   - 2c r22 - 2c r24 - 2c r26 + (1-2c) r27 + (1-2c) r29
#   + (2-2c) r30 - 3c r31
#
# 12 Ψ([[f(V)]]) = IndV:
#   (1-c) r2 - 3c r5 + (1-c) r6 - c r11 + (1-c) r12 - 2c r13 + (1-c) r14
#   + (2-2c) r21 - c r22 - c r23 - c r24 - c r25 - c r26
# ---------------------------------------------------------------------------

def indT_coeffs(c: float) -> list[float]:
    q = [0.0] * 32
    q[9] = 1 - c
    q[13] = -c
    q[14] = -c
    q[16] = -c
    q[18] = 1 - c
    q[19] = 1 - c
    q[20] = 1 - c
    q[22] = -2 * c
    q[24] = -2 * c
    q[26] = -2 * c
    q[27] = 1 - 2 * c
    q[29] = 1 - 2 * c
    q[30] = 2 - 2 * c
    q[31] = -3 * c
    return q


def indV_coeffs(c: float) -> list[float]:
    q = [0.0] * 32
    q[2] = 1 - c
    q[5] = -3 * c
    q[6] = 1 - c
    q[11] = -c
    q[12] = 1 - c
    q[13] = -2 * c
    q[14] = 1 - c
    q[21] = 2 - 2 * c
    q[22] = -c
    q[23] = -c
    q[24] = -c
    q[25] = -c
    q[26] = -c
    return q


# Fork(Ψ) = 4Ψ(κ − 3(3c−1)²)
#   = r4 + r7 + 3 r8 + r12 + r17 + r19 + 2 r20 + 2 r21
#     + r23 + r25 + r26 + r29 + 2 r30 − 12(3c−1)² Σ r_i
def fork_coeffs(c: float) -> list[float]:
    penalty = 12.0 * (3.0 * c - 1.0) ** 2
    q = [-penalty] * 32
    extra = {
        4: 1,
        7: 1,
        8: 3,
        12: 1,
        17: 1,
        19: 1,
        20: 2,
        21: 2,
        23: 1,
        25: 1,
        26: 1,
        29: 1,
        30: 2,
    }
    for k, v in extra.items():
        q[k] += v
    return q


def quad_form(a: tuple[float, ...], M: list[list[float]]) -> float:
    s = 0.0
    n = len(a)
    for i in range(n):
        for j in range(n):
            s += a[i] * M[i][j] * a[j]
    return s


def F_coeffs(
    c: float,
    a_vecs=A_VECS,
    b_vec=B_VEC,
    cT: float = CT,
    cV: float = CV,
    d_fork: float = D_FORK,
) -> list[float]:
    """Coefficient of each r_k in F(c, r)."""
    Ms = ac_slices()
    out = [0.0] * 32
    for k in range(32):
        sos = 0.0
        for a in a_vecs:
            sos += quad_form(a, Ms[k])
        reg = 0.0
        for i, bi in enumerate(b_vec):
            reg += bi * (BR[i][k] - c * AR[i][k])
        out[k] = sos + reg
    it = indT_coeffs(c)
    iv = indV_coeffs(c)
    fk = fork_coeffs(c)
    for k in range(32):
        out[k] += cT * it[k] + cV * iv[k] + d_fork * fk[k]
    return out


# Printed expansion (4.22), for comparison only.
PRINTED_3465 = {
    0: -38.906394,
    1: -25.96859,
    2: -4156.34069,
    3: -16.447994,
    4: -1172.27439,
    5: -577.3814,
    6: -4.57689,
    7: -10.55419,
    8: -4042.1489,
    9: -10.328894,
    10: -13.03079,
    11: -1327.03609,
    12: -2658.54869,
    13: -9.71489,
    14: -14574.68439,
    15: -7.032994,
    16: -6.85949,
    17: -11279.04479,
    18: -7.458494,
    19: -15538.64129,
    20: -19.61149,
    21: -15.87099,
    22: -12.39949,
    23: -9949.057894,
    24: -9.5492,
    25: -12.55709400,
    26: -17.24429,
    27: -9.535194,
    28: -1.24639,
    29: -3070.47399,
    30: -17.36519,
    31: -13.03819,
}


def worst(coeffs: list[float]) -> tuple[int, float]:
    k = max(range(32), key=lambda i: coeffs[i])
    return k, coeffs[k]


def all_negative(coeffs: list[float], eps: float = 0.0) -> bool:
    return all(x < -eps for x in coeffs)


def binary_search_c(lo: float = 1.0 / 3.0, hi: float = 0.4, steps: int = 40) -> float:
    """Smallest c at which the *published* combination is strictly negative.

    HKN prove F is nonincreasing in c on [1/3, 1] for r ≥ 0, so the first
    c with max_k F_k(c) < 0 is the threshold of this particular certificate.
    """
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        _, w = worst(F_coeffs(mid))
        if w < 0:
            hi = mid
        else:
            lo = mid
    return hi


def main() -> None:
    _check_shapes()
    coeffs = F_coeffs(HKN_C)
    k_bad, w = worst(coeffs)
    print("HKN published c =", HKN_C)
    print("recomputed F(0.3465, r) worst coordinate:", k_bad, w)
    print("all strictly negative?", all_negative(coeffs))
    print()
    print("k    recomputed          printed (4.22)      delta")
    diffs = []
    for k in range(32):
        printed = PRINTED_3465[k]
        delta = coeffs[k] - printed
        diffs.append(delta)
        print(f"{k:2d}  {coeffs[k]:18.8f}  {printed:18.8f}  {delta:+.6f}")

    # The printed expansion uses two-decimal a_i; expect O(0.01)–O(1) drift.
    # What matters is the sign pattern of the *recomputed* form.
    c_star = binary_search_c()
    coeffs_star = F_coeffs(c_star)
    _, w_star = worst(coeffs_star)
    print()
    print("threshold of the published combination (binary search):", f"{c_star:.10f}")
    print("worst coordinate there:", worst(coeffs_star))

    # Also evaluate a bit below 0.3465.
    for c in (0.3465, 0.3460, 0.3455, 0.3450, 0.3440, 0.3430, 0.3420, 0.3400, 0.3388):
        cc = F_coeffs(c)
        k, w = worst(cc)
        print(f"  c={c:.4f}  worst=r_{k}  {w:+.6f}  all_neg={all_negative(cc)}")

    payload = {
        "published_c": HKN_C,
        "recomputed_F_at_published": coeffs,
        "printed_422": [PRINTED_3465[k] for k in range(32)],
        "delta_recomputed_minus_printed": diffs,
        "worst_at_published": {"index": k_bad, "value": w},
        "all_negative_at_published": all_negative(coeffs),
        "certificate_threshold": c_star,
        "worst_at_threshold": {"index": worst(coeffs_star)[0], "value": w_star},
        "note": (
            "F is rebuilt from Tables 1–2 and (4.14)(4.15)(fork). "
            "A negative F certifies emptiness of R(c) for this combination. "
            "The two-decimal a_i are used exactly as printed."
        ),
    }
    path = OUT / "hkn_replay.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
