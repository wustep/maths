"""Shared comparison constants for the q3 Lieb–Thirring campaign.

Published later record: Carvalho Corso–Ried, arXiv:2403.04347v2,
Corollary 1.7, L/Lcl ≤ 1.44655 from M_3 = 0.371185695.
"""

from __future__ import annotations

import math

CCR_L = 1.44655
CCR_M3 = 0.371185695
FHJN_L = 1.456
Q1_L = 1.45576
SOBOLEV_RATIO = 2.0 / math.sqrt(3.0)

LCL_11 = 2.0 / (3.0 * math.pi)  # L_{1,1}^{cl}
KCL_1 = math.pi**2 / 3.0  # K_1^{cl}

# Duality at d=1: L/Lcl = 1/sqrt(K/Kcl),  K = 4/(27 L^2)
# and L = (9 sqrt(3)/4) C_1,  K/Kcl = 16/(243 C_1^2).


def l_from_c1(c1: float) -> float:
    return (9.0 * math.sqrt(3.0) / 4.0) * c1


def k_over_kcl_from_c1(c1: float) -> float:
    return 16.0 / (243.0 * c1 * c1)


def l_from_k(k: float) -> float:
    """L_{1,1} from the kinetic constant K_1 (not the ratio)."""
    return math.sqrt(4.0 / (27.0 * k))


def ratio_from_k_over_kcl(kk: float) -> float:
    return 1.0 / math.sqrt(kk)
