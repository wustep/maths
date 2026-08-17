"""Fourier coefficients of Bedert's §7 auxiliary r_t, and variants.

Window of five bits (a_{m-2t}, a_{m-t}, a_m, a_{m+t}, a_{m+2t}).
rho_m is the Fourier coefficient of

    r_t = (1 - beta * cos(2 pi t x + phi)) * (f * f)

where f = 2 (1 + alpha sin(2 pi t x)) hat{1}_A.

Bedert's choice: alpha=1, beta=1, phi=pi/4.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

from qsqrt2 import CSqrt2, I, ONE, QSqrt2, SQRT2, ZERO


Bits = Tuple[int, int, int, int, int]  # (a_{m-2t}, a_{m-t}, a_m, a_{m+t}, a_{m+2t})


def all_windows() -> List[Bits]:
    out = []
    for mask in range(32):
        bits = tuple((mask >> k) & 1 for k in range(5))
        out.append(bits)  # type: ignore[arg-type]
    return out


def fhat_at(am_tm1: int, am: int, am_tp1: int, alpha: QSqrt2) -> CSqrt2:
    """hat f_t (m) = 2 a_m - i alpha a_{m-t} + i alpha a_{m+t}."""
    return CSqrt2(QSqrt2(2 * am), ZERO) + I * alpha * QSqrt2(am_tp1 - am_tm1)


def rho_bedert_pi4(bits: Bits, alpha: QSqrt2 = ONE, beta: QSqrt2 = ONE) -> CSqrt2:
    """rho with phi = pi/4, so e^{i phi} = (1+i)/sqrt(2).

    rho = f(m)^2 - (beta e^{i phi}/2) f(m-t)^2 - (beta e^{-i phi}/2) f(m+t)^2
    beta e^{i pi/4}/2 = beta (1+i) / (2 sqrt(2))
    """
    u, a, b, c, v = bits  # a_{m-2t}, a_{m-t}, a_m, a_{m+t}, a_{m+2t}
    fm = fhat_at(a, b, c, alpha)
    fmt = fhat_at(u, a, b, alpha)  # at m-t: neighbors a_{m-2t}, a_{m-t}, a_m
    ftp = fhat_at(b, c, v, alpha)  # at m+t: neighbors a_m, a_{m+t}, a_{m+2t}
    # coeff = beta * (1+i) / (2 sqrt(2))
    one_plus_i = CSqrt2(ONE, ONE)
    two_sqrt2 = CSqrt2(SQRT2 * 2, ZERO)
    cplus = CSqrt2(beta, ZERO) * one_plus_i / two_sqrt2
    cminus = cplus.conj()
    return fm * fm - cplus * (fmt * fmt) - cminus * (ftp * ftp)


def is_Bt(bits: Bits) -> bool:
    """B_t = (A ∩ (A+t)) \\ (A-t), so (a_{m-t}, a_m, a_{m+t}) = (1, 1, 0)."""
    return bits[1] == 1 and bits[2] == 1 and bits[3] == 0


def classify_triple(bits: Bits) -> Tuple[int, int, int]:
    return (bits[1], bits[2], bits[3])


# Bedert Lemma 7.2 claimed table (max Re rho, max |Im rho|) over the four
# outer bits, keyed by the middle triple (a_{m-t}, a_m, a_{m+t}).
# Values stored as QSqrt2.
BEDERT_TABLE = {
    (0, 0, 0): (QSqrt2(0, Fraction(1, 2)), QSqrt2(0, Fraction(1, 4))),  # 1/√2 = √2/2, √2/4
    (0, 0, 1): (QSqrt2(-1, Fraction(-3, 4)), QSqrt2(0, Fraction(5, 4))),
    (0, 1, 0): (QSqrt2(4, Fraction(1, 2)), QSqrt2(0, Fraction(1, 4))),  # 4+1/√2 = 4+√2/2
    (0, 1, 1): (QSqrt2(3, Fraction(1, 2)), QSqrt2(4, 2)),  # 3+1/√2, 4+2√2
    (1, 0, 0): (QSqrt2(-1, Fraction(-3, 4)), QSqrt2(0, Fraction(5, 4))),
    (1, 0, 1): (QSqrt2(0, -2), QSqrt2(0, Fraction(5, 4))),  # -2√2, 5√2/4
    (1, 1, 0): (QSqrt2(3, Fraction(1, 2)), QSqrt2(4, 2)),
    (1, 1, 1): (QSqrt2(4, Fraction(1, 2)), QSqrt2(0, Fraction(3, 4))),
}

# Claimed B_t lower bound on -Im rho: 4 + √2
BEDERT_BT_IM_LOWER = QSqrt2(4, 1)

# Claimed uniform: Re rho <= 4 + 1/√2 = 4 + √2/2, |Im rho| <= 4 + 2√2
BEDERT_RE_UPPER = QSqrt2(4, Fraction(1, 2))
BEDERT_IM_ABS_UPPER = QSqrt2(4, 2)


def summarise(alpha: QSqrt2 = ONE, beta: QSqrt2 = ONE) -> dict:
    rows = []
    by_triple: Dict[Tuple[int, int, int], List[CSqrt2]] = {}
    for bits in all_windows():
        rho = rho_bedert_pi4(bits, alpha=alpha, beta=beta)
        trip = classify_triple(bits)
        by_triple.setdefault(trip, []).append(rho)
        rows.append((bits, rho, is_Bt(bits)))

    max_re = None
    max_im_abs = None
    min_neg_im_Bt = None
    for bits, rho, bt in rows:
        if max_re is None or rho.re > max_re:
            max_re = rho.re
        im_abs = rho.im if rho.im >= ZERO else -rho.im
        if max_im_abs is None or im_abs > max_im_abs:
            max_im_abs = im_abs
        if bt:
            neg_im = -rho.im
            if min_neg_im_Bt is None or neg_im < min_neg_im_Bt:
                min_neg_im_Bt = neg_im

    gap = min_neg_im_Bt - max_re  # type: ignore[operator]
    return {
        "rows": rows,
        "by_triple": by_triple,
        "max_re": max_re,
        "max_im_abs": max_im_abs,
        "min_neg_im_Bt": min_neg_im_Bt,
        "gap": gap,
    }
