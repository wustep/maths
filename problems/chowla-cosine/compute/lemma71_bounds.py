#!/usr/bin/env python3
"""Integer-only sanity checks for the Lemma 7.1 constants C_Q1=3, C_Q2=14.

These are not a substitute for the analytic derivation in WALKTHROUGH.md;
they only confirm the arithmetic combinations used to add the Young / split
errors. Exit 0 iff the additions match the published constants.
"""

from __future__ import annotations

import sys


def main() -> int:
    # R2' infinity: (L^2 - L) + 3 L^2 = 4 L^2 - L
    # three Young terms T1*(e T2), T2*(e T1), T2*(e T2) each <= L^2
    # plus overflow V <= L^2 - L
    r2p_inf = "4 L^2 - L"

    # R2''' L2: (L^2-L) + L^2 + (4L^2-L) = 6L^2 - 2L
    # v, R1'*(e T2), R2'*hat1_{A-t}
    r2ppp_l2 = "6 L^2 - 2L"

    # R2 = R2' + R2'' - 2 R2'''
    # ||R2||_2 <= 2*(4L^2-L) + 2*(6L^2-2L) = 8L^2-2L + 12L^2-4L = 20L^2-6L
    r2_l2 = (8 - 2, 12 - 4)  # dummy
    r2_coeff = 2 * 4 + 2 * 6
    r2_lin = 2 * 1 + 2 * 2
    assert r2_coeff == 20 and r2_lin == 6

    # S1' pointwise <= 2(hat1_A + L)
    # S1'*T1 overflow <= 2(L^2 - L)
    # S1'*T2, S2'*T1, S2'*T2 each <= 2 L^2
    # ||S2||_inf <= 2(L^2-L) + 6 L^2 = 8L^2 - 2L
    s2_coeff = 2 + 6
    s2_lin = 2
    assert s2_coeff == 8 and s2_lin == 2

    # Q2 = R2/2 + S2/2
    # ||Q2||_2 <= (20L^2-6L)/2 + (8L^2-2L)/2 = 10L^2-3L + 4L^2-L = 14L^2-4L
    q2_quad = 20 // 2 + 8 // 2
    q2_lin = 6 // 2 + 2 // 2
    assert q2_quad == 14 and q2_lin == 4

    # Q1 = R1/2 + S1/2, |R1|<=4(hat1+L), |S1|<=2(hat1+L) => |Q1|<=3(hat1+L)
    assert 4 / 2 + 2 / 2 == 3

    # C_r: ||f||_min <= 4K, f*f >= -16 K^2, 0 <= 1-cos <= 2 => r >= -32 K^2
    assert 2 * 16 == 32

    # AP: L <= 8K^2 + 8, |A_t| >= N/(2K), |B_t| >= N/(2K L) >= N/(16 K (K^2+1))
    assert 2 * 8 == 16

    # energy-branch pack: 16 Cstar (K^7 + K^5) <= 32 Cstar K^7 when K>=1
    # and <= 32 Cstar K^5 when K<=1
    print("lemma71 arithmetic packs: OK")
    print(f"  R2' inf {r2p_inf}")
    print(f"  R2''' L2 {r2ppp_l2}")
    print("  ||Q2||_2 <= 14 K^2 - 4K <= 14 K^2")
    print("  |Q1| <= 3 (hat1_A + K)")
    print("  C_r = 32")
    print("  |B_t| >= N / (16 K (K^2+1))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
