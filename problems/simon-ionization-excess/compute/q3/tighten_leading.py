#!/usr/bin/env python3
"""HPS Section 7 chain with β_3 ≥ compact γ (aspect-12 lift).

Same arithmetic as q1/tighten_hps.py, but the β_3 lower bound is the
q2 compact γ at R=12, not min f = 1/b(3). Leading coefficient is
1/γ instead of b(3). Remainders are recomputed on x ∈ [1/γ, 9/4].

Writes certs/leading.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr, pi, sqrt

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q2_COMPACT = HERE.parent / "q2" / "certs" / "beta3_compact.json"

mp.dps = 80
iv.dps = 80
PREC = 40
LT = mpf("1.456")


def S(x, d: int = PREC) -> str:
    return nstr(x, d, strip_zeros=False)


def iv_bounds(x) -> tuple[str, str]:
    return S(mpf(x.a)), S(mpf(x.b))


def iv_cbrt(x):
    return iv.exp(iv.log(x) / 3)


def iv_pow(x, p):
    return iv.exp(iv.mpf(p) * iv.log(x))


def C1_iv():
    return (
        iv_pow(3, iv.mpf(5) / 3)
        * iv_pow(5, iv.mpf(5) / 6)
        * iv_pow(7 / iv.pi, iv.mpf(1) / 3)
        / (22 * iv.sqrt(11))
    )


def C2inv_iv():
    return 4 * iv_pow(iv.pi, iv.mpf(2) / 3) / iv.sqrt(15)


def kappa_iv():
    return iv.sqrt(5) * iv_cbrt(2 / (9 * iv.pi**2) * iv.mpf("1.456"))


def c_iv():
    return kappa_iv() * C2inv_iv()


def a1_iv(x, beta3, lam=None):
    if lam is None:
        coeff = 3 * iv_cbrt(iv.mpf(3) / 10)
    else:
        coeff = 1 / lam + (iv.mpf(6) / 5) * lam**2
    return coeff * iv_pow(beta3, iv.mpf(-2) / 3) * iv_cbrt(x) + c_iv() * (
        1 / beta3
    ) * iv_pow(x, iv.mpf(-2) / 3)


def extras_iv(b):
    beta3 = 1 / b
    c = c_iv()
    a2 = b / 84
    a3 = (c / 5) * iv_pow(iv.mpf(5) / 12, iv.mpf(2) / 3) * iv_cbrt(b)
    a4 = c * iv_cbrt(b) / 84
    return a2, a3, a4


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    compact = json.loads(Q2_COMPACT.read_text())
    row = next(r for r in compact["configs"] if r["R"] == 12)
    # Use a slightly smaller γ so 1/γ is an upper enclosure.
    # The stored compact_gamma is already phi_target − err_hi (a lower bound).
    gamma = iv.mpf(row["compact_gamma"])
    gamma_safe = gamma * (1 - iv.mpf("1e-18"))
    b = 1 / gamma_safe
    b_hi = mpf(b.b)

    a1_left = a1_iv(b, gamma_safe)
    a1_94 = a1_iv(iv.mpf(9) / 4, gamma_safe)
    a2, a3, a4 = extras_iv(b)
    Z4 = iv.mpf(4)
    coeff4 = (
        a1_left
        + a2 * iv_pow(Z4, iv.mpf(-1) / 3)
        + a3 * iv_pow(Z4, iv.mpf(-2) / 3)
        + a4 / Z4
    )

    # Conservative printed decimals: round b UP, remainders UP.
    # 1/γ ≤ 1.11169654… so 1.1117 works; keep a bit of room.
    lead = mpf("1.1118")
    a1_dec = mpf("3.880")
    rem_dec = mpf("3.966")
    extras_dec = (mpf("0.0133"), mpf("0.1833"), mpf("0.01956"))

    lead_ok = bool(b_hi < lead)
    a1_ok = bool(mpf(a1_left.b) < a1_dec and mpf(a1_94.b) < mpf(a1_left.a) + mpf("1"))
    # max of a1 on [b, 9/4]: check a handful of points
    a1_max_hi = mpf(a1_left.b)
    for num, den in ((12, 10), (14, 10), (16, 10), (18, 10), (20, 10), (9, 4)):
        val = a1_iv(iv.mpf(num) / den, gamma_safe)
        a1_max_hi = max(a1_max_hi, mpf(val.b))
    a1_max_ok = bool(a1_max_hi < a1_dec)
    rem_ok = bool(mpf(coeff4.b) < rem_dec)
    extras_ok = bool(
        mpf(a2.b) < extras_dec[0]
        and mpf(a3.b) < extras_dec[1]
        and mpf(a4.b) < extras_dec[2]
    )
    beats = bool(lead < mpf("1.1185") and lead_ok)

    # r_max: λ / Z^{1/3} on N γ ≥ Z, Z≥4
    lam = iv_cbrt(iv.mpf(5) / 12)
    rmax = lam / iv_cbrt(iv.mpf(4))
    r_ok = bool(mpf(rmax.b) < mpf("0.5"))

    blob = {
        "arxiv": "2504.18487v1",
        "beta3_lower": row["compact_gamma"],
        "source": "q2 compact R=12 n=22, lifted by mass-opt dichotomy",
        "b_interval": list(iv_bounds(b)),
        "b_hi": S(b_hi),
        "printed_leading": str(lead),
        "a1_at_left": list(iv_bounds(a1_left)),
        "a1_at_9/4": list(iv_bounds(a1_94)),
        "a1_max_hi_on_interval": S(a1_max_hi),
        "a2": list(iv_bounds(a2)),
        "a3": list(iv_bounds(a3)),
        "a4": list(iv_bounds(a4)),
        "Z4_remainder_coeff": list(iv_bounds(coeff4)),
        "r_max": list(iv_bounds(rmax)),
        "checks": {
            "leading_lt_1.1118": lead_ok,
            "a1_lt_3.880": a1_ok and a1_max_ok,
            "Z4_coeff_lt_3.966": rem_ok,
            "extras_ok": extras_ok,
            "r_max_lt_0.5": r_ok,
            "beats_1.1185": beats,
        },
        "inequalities": [
            {
                "beats": "HPS Theorem 2.2 / Prop. 2.5 leading 1.1185",
                "range": "Z >= 4",
                "inequality": (
                    "N < 1.1118 Z + 3.880 Z^{1/3} + 0.0133 "
                    "+ 0.1833 Z^{-1/3} + 0.01956 Z^{-2/3}"
                ),
            },
            {
                "beats": "HPS simplified 1.1185 Z + 4 Z^{1/3}",
                "range": "Z >= 4",
                "inequality": "N_c < 1.1118 Z + 3.966 Z^{1/3}",
            },
        ],
        "LT_factor": "1.456",
        "note": (
            "β_3 ≥ compact γ on every radial probability, by the "
            "aspect-12 compact certificate plus the mass-stationary "
            "cut Q>12/13 off that class. Not the R=4 number 1.1087."
        ),
    }
    out = CERTS / "leading.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("b_hi", float(b_hi), "printed", float(lead), "ok", lead_ok)
    print("a1 max", float(a1_max_hi), "ok", a1_max_ok)
    print("Z4 coeff", float(mpf(coeff4.b)), "ok", rem_ok)
    print("beats 1.1185", beats)
    print("wrote", out)
    if not (lead_ok and a1_max_ok and rem_ok and extras_ok and r_ok and beats):
        raise SystemExit("tighten_leading.py FAIL")
    print("tighten_leading.py PASS")


if __name__ == "__main__":
    main()
