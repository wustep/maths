#!/usr/bin/env python3
"""HPS Section 7 chain with the q13 compact γ.

Same arithmetic as q1/tighten_hps.py and q11/tighten_leading.py.
β_3 lower bound is the best certified compact γ (mass-opt lift).

Writes certs/leading.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

from select_row import best_row

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 80
iv.dps = 80
PREC = 40


def S(x, d: int = PREC) -> str:
    return nstr(x, d, strip_zeros=False)


def iv_bounds(x) -> tuple[str, str]:
    return S(mpf(x.a)), S(mpf(x.b))


def iv_cbrt(x):
    return iv.exp(iv.log(x) / 3)


def iv_pow(x, p):
    return iv.exp(iv.mpf(p) * iv.log(x))


def C2inv_iv():
    return 4 * iv_pow(iv.pi, iv.mpf(2) / 3) / iv.sqrt(15)


def kappa_iv():
    return iv.sqrt(5) * iv_cbrt(2 / (9 * iv.pi**2) * iv.mpf("1.456"))


def c_iv():
    return kappa_iv() * C2inv_iv()


def a1_iv(x, beta3):
    coeff = 3 * iv_cbrt(iv.mpf(3) / 10)
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


def ceil_dec(x: mpf, places: int) -> mpf:
    """Round up to the given number of decimal places."""
    scale = mpf(10) ** places
    # tiny pad so a value already on a grid still goes up if it is a float hair
    return (mp.floor(x * scale + mpf("1e-12")) + 1) / scale


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    row = best_row()
    gamma = iv.mpf(str(row["compact_gamma"]))
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

    a1_max_hi = mpf(a1_left.b)
    for num, den in ((12, 10), (14, 10), (16, 10), (18, 10), (20, 10), (9, 4)):
        val = a1_iv(iv.mpf(num) / den, gamma_safe)
        a1_max_hi = max(a1_max_hi, mpf(val.b))

    lead = ceil_dec(b_hi, 4)
    lead_str = format(float(lead), ".4f")
    a1_dec = ceil_dec(a1_max_hi, 3)
    rem_dec = ceil_dec(mpf(coeff4.b), 3)
    extras_dec = (
        ceil_dec(mpf(a2.b), 4),
        ceil_dec(mpf(a3.b), 4),
        ceil_dec(mpf(a4.b), 5),
    )

    lead_ok = bool(b_hi < lead)
    a1_ok = bool(a1_max_hi < a1_dec)
    rem_ok = bool(mpf(coeff4.b) < rem_dec)
    extras_ok = bool(
        mpf(a2.b) < extras_dec[0]
        and mpf(a3.b) < extras_dec[1]
        and mpf(a4.b) < extras_dec[2]
    )
    beats_q11 = bool(lead < mpf("1.1010") and lead_ok)
    beats_q10 = bool(lead < mpf("1.1013") and lead_ok)
    beats_q9 = bool(lead < mpf("1.1017") and lead_ok)
    beats_q8 = bool(lead < mpf("1.1020") and lead_ok)
    beats_q7 = bool(lead < mpf("1.1021") and lead_ok)
    beats_q6 = bool(lead < mpf("1.1026") and lead_ok)
    beats_q5 = bool(lead < mpf("1.1035") and lead_ok)
    beats_q4 = bool(lead < mpf("1.1057") and lead_ok)
    beats_q3 = bool(lead < mpf("1.1118") and lead_ok)
    beats_r4 = bool(lead < mpf("1.108741"))
    beats_hps = bool(lead < mpf("1.1185"))

    lam = iv_cbrt(iv.mpf(5) / 12)
    rmax = lam / iv_cbrt(iv.mpf(4))
    r_ok = bool(mpf(rmax.b) < mpf("0.5"))

    blob = {
        "arxiv": "2504.18487v1",
        "beta3_lower": str(row["compact_gamma"]),
        "source": (
            f"q13 compact R={int(row['R'])} n={int(row['n'])} "
            f"target={row['target']}, lifted by mass-opt dichotomy"
        ),
        "row": row["_path"],
        "R_split": int(row["R"]),
        "b_interval": list(iv_bounds(b)),
        "b_hi": S(b_hi),
        "printed_leading": lead_str,
        "a1_at_left": list(iv_bounds(a1_left)),
        "a1_at_9/4": list(iv_bounds(a1_94)),
        "a1_max_hi_on_interval": S(a1_max_hi),
        "a1_printed": nstr(a1_dec, 4, strip_zeros=False),
        "a2": list(iv_bounds(a2)),
        "a3": list(iv_bounds(a3)),
        "a4": list(iv_bounds(a4)),
        "Z4_remainder_coeff": list(iv_bounds(coeff4)),
        "Z4_printed": str(rem_dec),
        "extras_printed": [
            nstr(extras_dec[0], 4, strip_zeros=False),
            nstr(extras_dec[1], 4, strip_zeros=False),
            nstr(extras_dec[2], 5, strip_zeros=False),
        ],
        "r_max": list(iv_bounds(rmax)),
        "checks": {
            "leading_lt_printed": lead_ok,
            "a1_lt_printed": a1_ok,
            "Z4_coeff_lt_printed": rem_ok,
            "extras_ok": extras_ok,
            "r_max_lt_0.5": r_ok,
            "beats_1.1185": beats_hps,
            "beats_1.1118": beats_q3,
            "beats_1.1057": beats_q4,
            "beats_1.1010": beats_q11,
            "beats_1.1013": beats_q10,
            "beats_1.1017": beats_q9,
            "beats_1.1020": beats_q8,
            "beats_1.1021": beats_q7,
            "beats_1.1026": beats_q6,
            "beats_1.1035": beats_q5,
            "beats_1.108741_class_number": beats_r4,
        },
        "inequalities": [
            {
                "beats": (
                    "q11 leading 1.1010, q10 1.1013, q9 1.1017, q8 1.1020, q7 1.1021, q6 1.1026, "
                    "q5 1.1035, q4 1.1057, q3 1.1118, and HPS printed 1.1185"
                ),
                "range": "Z >= 4",
                "inequality": (
                    f"N < {lead_str} Z + {nstr(a1_dec, 4, strip_zeros=False)} Z^{{1/3}} "
                    f"+ {nstr(extras_dec[0], 4, strip_zeros=False)} "
                    f"+ {nstr(extras_dec[1], 4, strip_zeros=False)} Z^{{-1/3}} "
                    f"+ {nstr(extras_dec[2], 5, strip_zeros=False)} Z^{{-2/3}}"
                ),
            },
            {
                "beats": "q11 simplified 1.1010 Z + 3.934 Z^{1/3}",
                "range": "Z >= 4",
                "inequality": f"N_c < {lead_str} Z + {rem_dec} Z^{{1/3}}",
            },
        ],
        "LT_factor": "1.456",
        "note": (
            f"β_3 ≥ compact γ on every radial probability, by the "
            f"aspect-{int(row['R'])} compact certificate plus the "
            f"mass-stationary cut Q>{int(row['R'])}/{int(row['R'])+1}. "
            "Not the withdrawn 1.1168. The aspect-≤4 number 1.1087 is "
            "not used as a class-only quote; the unrestricted leading "
            "is the compact γ at the split R."
        ),
    }
    out = CERTS / "leading.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("b_hi", float(b_hi), "printed", lead_str, "ok", lead_ok)
    print("a1 max", float(a1_max_hi), "printed", float(a1_dec), "ok", a1_ok)
    print("Z4 coeff", float(mpf(coeff4.b)), "printed", float(rem_dec), "ok", rem_ok)
    print("beats 1.1010", beats_q11, "beats 1.1013", beats_q10)
    print("wrote", out)
    if not (
        lead_ok and a1_ok and rem_ok and extras_ok and r_ok and beats_q11 and beats_hps
    ):
        raise SystemExit("tighten_leading.py FAIL")
    print("tighten_leading.py PASS")


if __name__ == "__main__":
    main()
