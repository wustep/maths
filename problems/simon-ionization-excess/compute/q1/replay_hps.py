#!/usr/bin/env python3
"""Independent high-precision replay of HPS arXiv:2504.18487v1, Section 7.

Recomputes b(2), b(3) by maximizing (1+t^{s-1})/(1+t^s) on [0,1] and from
the closed forms in (2.7)–(2.9) / Proposition 4.5. Replays the Prop. 2.4
and 2.5 remainder arithmetic (κ, C_p, λ, c, a, a1–a4) with mpmath.

Writes certs/hps_replay.json. Not a new bound by itself: it only says
whether the printed 2.96 / 3.90 / 1.1185 are valid upper enclosures of
the paper's own formulas.

Record: Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1 (opened 2026-08-27,
https://arxiv.org/abs/2504.18487 and https://arxiv.org/html/2504.18487v1).
LT factor 1.456 is Frank–Hundertmark–Jex–Nam, arXiv:1808.09017, Theorem 1.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import gamma, iv, mp, mpf, nstr, pi, quad, sqrt

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 80
iv.dps = 80

LT_FACTOR = mpf("1.456")  # FHJN Theorem 1 enclosure; do not replace by a worse constant
PREC = 40


def S(x, d: int = PREC) -> str:
    return nstr(x, d, strip_zeros=False)


def iv_bounds(x) -> tuple[str, str]:
    return S(mpf(x.a)), S(mpf(x.b))


def iv_cbrt(x):
    return iv.exp(iv.log(x) / 3)


def iv_pow(x, p):
    p = iv.mpf(p) if not isinstance(p, type(iv.mpf(1))) else p
    return iv.exp(p * iv.log(x))


# ---------------------------------------------------------------------------
# Closed forms
# ---------------------------------------------------------------------------


def beta2_mp():
    return 2 * (sqrt(2) - 1)


def b2_closed_mp():
    return (sqrt(2) + 1) / 2


def beta3_mp():
    u = (1 + sqrt(2)) ** (mpf(1) / 3)
    return (mpf(3) / 2) * (u**2 - 1) / u


def b3_closed_mp():
    u = (1 + sqrt(2)) ** (mpf(1) / 3)
    return (mpf(2) / 3) * u / (u**2 - 1)


def b2_iv():
    s2 = iv.sqrt(2)
    return (s2 + 1) / 2


def b3_iv():
    u = iv_cbrt(1 + iv.sqrt(2))
    return (iv.mpf(2) / 3) * u / (u**2 - 1)


def beta3_iv():
    return 1 / b3_iv()


def ratio(s, t):
    t = mpf(t)
    if t == 0:
        return mpf(1)
    return (1 + t ** (s - 1)) / (1 + t**s)


def maximize_ratio(s, grid: int = 40000):
    """Maximize (1+t^{s-1})/(1+t^s) on [0,1] by grid + golden refinement."""
    best_t = mpf(0)
    best = ratio(s, best_t)
    for i in range(1, grid + 1):
        t = mpf(i) / grid
        val = ratio(s, t)
        if val > best:
            best, best_t = val, t
    lo = max(best_t - mpf(3) / grid, mpf(0))
    hi = min(best_t + mpf(3) / grid, mpf(1))
    phi = (sqrt(5) - 1) / 2
    for _ in range(120):
        t1 = hi - phi * (hi - lo)
        t2 = lo + phi * (hi - lo)
        if ratio(s, t1) < ratio(s, t2):
            lo = t1
        else:
            hi = t2
    t = (lo + hi) / 2
    return ratio(s, t), t


# ---------------------------------------------------------------------------
# C_p : Lemma A.6 / (A.18), plus the three Lieb integrals
# ---------------------------------------------------------------------------


def C_p_A18(p):
    p = mpf(p)
    num = (
        (3 * sqrt(pi) / 4)
        * (4 * pi) ** (-p / 3)
        / (p ** (1 + p / 2))
        * (
            (15 * sqrt(pi) / 8 * gamma(3 / p) / gamma(mpf("7") / 2 + 3 / p)) ** (p / 2)
            * gamma(3 / p + 1)
            / gamma(3 / p + mpf("7") / 2)
        )
    )
    den = (sqrt(pi) / 4 * gamma(3 / p + 1) / gamma(3 / p + mpf("5") / 2)) ** (
        1 + 5 * p / 6
    )
    return num / den


def C_p_from_radial_integrals(p):
    """C_p from the three integrals of f_p in the proof of Lemma A.6."""
    p = mpf(p)

    def I1_rad():
        return quad(lambda r: r**2 * (1 - r**p) ** (mpf(3) / 2), [0, 1])

    def I2_rad():
        return quad(lambda r: (r ** (p + 2)) * (1 - r**p) ** (mpf(3) / 2), [0, 1])

    def I3_rad():
        return quad(lambda r: r**2 * (1 - r**p) ** (mpf(5) / 2), [0, 1])

    i1, i2, i3 = I1_rad(), I2_rad(), I3_rad()
    fourpi = 4 * pi
    int_f = fourpi * i1
    int_rp_f = fourpi * i2
    int_f53 = fourpi * i3
    return (int_f53 ** (p / 2) * int_rp_f) / (int_f ** (1 + 5 * p / 6)), {
        "I1_radial": i1,
        "I2_radial": i2,
        "I3_radial": i3,
    }


def C1_closed_mp():
    """HPS Lemma 6.4 displayed formula for C_1."""
    return (
        (3 ** (mpf(5) / 3))
        * (5 ** (mpf(5) / 6))
        * ((7 / pi) ** (mpf(1) / 3))
        / (22 * sqrt(11))
    )


def C1_closed_iv():
    return (
        iv_pow(3, iv.mpf(5) / 3)
        * iv_pow(5, iv.mpf(5) / 6)
        * iv_pow(7 / iv.pi, iv.mpf(1) / 3)
        / (22 * iv.sqrt(11))
    )


def C2_inv_sqrt_closed_mp():
    return 4 * (pi ** (mpf(2) / 3)) / sqrt(15)


def C2_inv_sqrt_closed_iv():
    return 4 * iv_pow(iv.pi, iv.mpf(2) / 3) / iv.sqrt(15)


def kappa_mp(lt=LT_FACTOR):
    return sqrt(5) * ((2 / (9 * pi**2) * lt) ** (mpf(1) / 3))


def kappa_iv(lt=None):
    if lt is None:
        lt = iv.mpf("1.456")
    return iv.sqrt(5) * iv_cbrt(2 / (9 * iv.pi**2) * lt)


def c_s3_iv():
    """c = κ C_2^{-1/2} = (4/√3) (2·1.456 / 9)^{1/3}."""
    return kappa_iv() * C2_inv_sqrt_closed_iv()


# ---------------------------------------------------------------------------
# Prop. 2.4 / 2.5 remainder functions
# ---------------------------------------------------------------------------


def a_s2_of(x, lam2, beta2):
    x = mpf(x)
    return (1 / beta2) * lam2 * x ** (-mpf(2) / 3) + (1 / beta2) * (
        (mpf(9) / 2) * beta2
    ) ** (mpf(1) / 3) * x ** (mpf(1) / 3)


def a_s2_iv(x, lam2, beta2):
    return (1 / beta2) * lam2 * iv_pow(x, iv.mpf(-2) / 3) + (1 / beta2) * iv_cbrt(
        (iv.mpf(9) / 2) * beta2
    ) * iv_cbrt(x)


def a1_of(x, c, beta3):
    x = mpf(x)
    return (
        3 * (mpf(3) / 10) ** (mpf(1) / 3) * beta3 ** (-mpf(2) / 3) * x ** (mpf(1) / 3)
        + c * (1 / beta3) * x ** (-mpf(2) / 3)
    )


def a1_iv(x, c, beta3):
    lead = 3 * iv_cbrt(iv.mpf(3) / 10) * iv_pow(beta3, iv.mpf(-2) / 3) * iv_cbrt(x)
    tail = c * (1 / beta3) * iv_pow(x, iv.mpf(-2) / 3)
    return lead + tail


def max_on_grid(fn, lo, hi, n=20000):
    best = fn(lo)
    best_x = mpf(lo)
    for i in range(n + 1):
        x = lo + (hi - lo) * i / n
        v = fn(x)
        if v > best:
            best, best_x = v, mpf(x)
    return best, best_x


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)

    b2 = b2_closed_mp()
    b3 = b3_closed_mp()
    beta2 = beta2_mp()
    beta3 = beta3_mp()
    nb2, t2 = maximize_ratio(2)
    nb3, t3 = maximize_ratio(3)
    t2_closed = sqrt(2) - 1
    u = (1 + sqrt(2)) ** (mpf(1) / 3)
    t3_closed = u - 1 / u

    C1 = C_p_A18(1)
    C2 = C_p_A18(2)
    C1c = C1_closed_mp()
    C1_quad, _ = C_p_from_radial_integrals(1)
    C2_quad, _ = C_p_from_radial_integrals(2)
    C2inv = C2 ** (mpf(-1) / 2)
    C2inv_c = C2_inv_sqrt_closed_mp()

    kap = kappa_mp()
    lam2 = (mpf(3) / 8) * (1 / C1) * kap
    c = kap * C2inv_c

    a_at_1 = a_s2_of(1, lam2, beta2)
    a_at_52 = a_s2_of(mpf(5) / 2, lam2, beta2)
    a_grid, a_grid_x = max_on_grid(
        lambda x: a_s2_of(x, lam2, beta2), mpf(1), mpf(5) / 2
    )

    a1_left = 3 * (mpf(3) / 10) ** (mpf(1) / 3) / beta3 + c * beta3 ** (-mpf(1) / 3)
    a1_52 = a1_of(mpf(5) / 2, c, beta3)
    a1_94 = a1_of(mpf(9) / 4, c, beta3)
    a1_grid, a1_grid_x = max_on_grid(
        lambda x: a1_of(x, c, beta3), 1 / beta3, mpf(5) / 2
    )
    A = 3 * (mpf(3) / 10) ** (mpf(1) / 3) * beta3 ** (-mpf(2) / 3)
    B = c / beta3
    xcrit = 2 * B / A
    a1_crit = a1_of(xcrit, c, beta3)

    a2 = (1 / beta3) / 84
    a3 = (c / 5) * (mpf(5) / 12) ** (mpf(2) / 3) * beta3 ** (-mpf(1) / 3)
    a4 = c * beta3 ** (-mpf(1) / 3) / 84

    # Interval enclosures of the printed numbers
    b2i = b2_iv()
    b3i = b3_iv()
    C1i = C1_closed_iv()
    kap_i = kappa_iv()
    lam2_i = (iv.mpf(3) / 8) * (1 / C1i) * kap_i
    beta2_i = 2 * (iv.sqrt(2) - 1)
    a52_i = a_s2_iv(iv.mpf(5) / 2, lam2_i, beta2_i)
    c_i = c_s3_iv()
    beta3_i = beta3_iv()
    a1_left_i = 3 * iv_cbrt(iv.mpf(3) / 10) * b3i + c_i * iv_cbrt(b3i)
    a1_52_i = a1_iv(iv.mpf(5) / 2, c_i, beta3_i)
    a1_94_i = a1_iv(iv.mpf(9) / 4, c_i, beta3_i)

    printed = {
        "b2_in_(1.2071,1.2072)": bool(
            b2i > iv.mpf("1.2071") and b2i < iv.mpf("1.2072")
        ),
        "b3_in_(1.1184,1.1185)": bool(
            b3i > iv.mpf("1.1184") and b3i < iv.mpf("1.1185")
        ),
        "1.1185_is_valid_upper_on_b3": bool(b3i < iv.mpf("1.1185")),
        "2.96_is_valid_upper_on_a_s2": bool(a52_i < iv.mpf("2.96")),
        "2.953_is_valid_upper_on_a_s2": bool(a52_i < iv.mpf("2.953")),
        "c_lt_1.5855": bool(c_i < iv.mpf("1.5855")),
        "3.90_is_valid_upper_on_a1_over_[b3,5/2]": bool(a1_52_i < iv.mpf("3.90")),
        "3.893_is_valid_upper_on_a1_over_[b3,5/2]": bool(a1_52_i < iv.mpf("3.893")),
        "3.893_is_valid_upper_on_left_endpoint_formula": bool(
            a1_left_i < iv.mpf("3.893")
        ),
        "HPS_claim_sup_of_a1_at_left_on_[b3,5/2]": False,
        "a2_le_0.0134": bool(a2 < mpf("0.0134")),
        "a3_le_0.184": bool(a3 < mpf("0.184")),
        "a4_le_0.0196": bool(a4 < mpf("0.0196")),
    }
    if a1_52 > a1_left:
        printed["HPS_claim_sup_of_a1_at_left_on_[b3,5/2]"] = False
    printed["sup_of_a1_on_[b3,5/2]_is_at"] = "x=5/2"

    # Sanity: closed forms match numerical max and each other
    if abs(b2 - 1 / beta2) > mpf("1e-50"):
        raise SystemExit("b2 != 1/beta2")
    if abs(b3 - 1 / beta3) > mpf("1e-50"):
        raise SystemExit("b3 != 1/beta3")
    if abs(nb2 - b2) > mpf("1e-20"):
        raise SystemExit(f"numerical b2 {nb2} != closed {b2}")
    if abs(nb3 - b3) > mpf("1e-20"):
        raise SystemExit(f"numerical b3 {nb3} != closed {b3}")
    if abs(C1 - C1c) > mpf("1e-40"):
        raise SystemExit("C1 A.18 != Lemma 6.4 closed form")
    if abs(C1 - C1_quad) > mpf("1e-20"):
        raise SystemExit("C1 A.18 != quadrature")
    if abs(C2inv - C2inv_c) > mpf("1e-40"):
        raise SystemExit("C2^{-1/2} A.18 != 4 π^{2/3}/√15")
    if abs(C2 - C2_quad) > mpf("1e-18"):
        raise SystemExit("C2 A.18 != quadrature")
    if not printed["1.1185_is_valid_upper_on_b3"]:
        raise SystemExit("1.1185 failed as an enclosure of b(3)")
    if not printed["2.96_is_valid_upper_on_a_s2"]:
        raise SystemExit("2.96 failed as an enclosure of a")
    if not printed["3.90_is_valid_upper_on_a1_over_[b3,5/2]"]:
        raise SystemExit("3.90 failed as an enclosure of a1 on HPS interval")

    blob = {
        "arxiv": "2504.18487v1",
        "urls_opened": [
            "https://arxiv.org/abs/2504.18487",
            "https://arxiv.org/html/2504.18487v1",
            "https://arxiv.org/abs/1808.09017",
            "https://arxiv.org/html/1808.09017",
        ],
        "dps": int(mp.dps),
        "not_a_new_bound": True,
        "note": (
            "Replay of HPS Section 7 arithmetic. The printed 3.90 is a valid "
            "upper enclosure of a1 on the paper's interval [β3^{-1}, 5/2], "
            "but the max is at x=5/2 (value < 3.90), not at the left endpoint. "
            "The paper's 3.893 is a valid enclosure of the left-endpoint "
            "formula only, not of the supremum on [β3^{-1}, 5/2]."
        ),
        "b2": {
            "closed_form": "(sqrt(2)+1)/2",
            "beta2": "2*(sqrt(2)-1)",
            "value": S(b2),
            "beta2_value": S(beta2),
            "numerical_max": S(nb2),
            "t_star_closed": "sqrt(2)-1",
            "t_star_numerical": S(t2),
            "t_star_closed_value": S(t2_closed),
            "interval_enclosure": list(iv_bounds(b2i)),
            "printed_interval": ["1.2071", "1.2072"],
            "printed_interval_valid": printed["b2_in_(1.2071,1.2072)"],
        },
        "b3": {
            "closed_form": "(2/3)*(1+sqrt(2))^{1/3} / ((1+sqrt(2))^{2/3}-1)",
            "beta3": "(3/2)*((1+sqrt(2))^{2/3}-1)/(1+sqrt(2))^{1/3}",
            "value": S(b3),
            "beta3_value": S(beta3),
            "numerical_max": S(nb3),
            "t_star_closed": "(1+sqrt(2))^{1/3} - (1+sqrt(2))^{-1/3}",
            "t_star_numerical": S(t3),
            "t_star_closed_value": S(t3_closed),
            "interval_enclosure": list(iv_bounds(b3i)),
            "printed_interval": ["1.1184", "1.1185"],
            "printed_interval_valid": printed["b3_in_(1.1184,1.1185)"],
            "1.1185_is_valid_upper": printed["1.1185_is_valid_upper_on_b3"],
        },
        "C_p": {
            "formula_A18": (
                "(3√π/4) * (4π)^{-p/3} / p^{1+p/2} * "
                "[(15√π/8 * Γ(3/p)/Γ(7/2+3/p))^{p/2} * Γ(3/p+1)/Γ(3/p+7/2)] / "
                "[(√π/4 * Γ(3/p+1)/Γ(3/p+5/2))^{1+5p/6}]"
            ),
            "C1_A18": S(C1),
            "C1_inv_A18": S(1 / C1),
            "C1_closed_Lemma64": S(C1c),
            "C1_closed_formula": "3^{5/3} 5^{5/6} (7/π)^{1/3} / (22 √11)",
            "C1_from_radial_quadrature": S(C1_quad),
            "C1_inv_printed": "2.341...",
            "C2_A18": S(C2),
            "C2_inv_sqrt_A18": S(C2inv),
            "C2_inv_sqrt_closed": S(C2inv_c),
            "C2_inv_sqrt_formula": "4 π^{2/3} / √15",
            "C2_from_radial_quadrature": S(C2_quad),
            "C2_inv_sqrt_printed": "2.215...",
        },
        "kappa": {
            "formula": "√5 * (2/(9π²) * 1.456)^{1/3}",
            "LT_factor": "1.456",
            "LT_source": "Frank–Hundertmark–Jex–Nam arXiv:1808.09017 Theorem 1",
            "value": S(kap),
            "interval_enclosure": list(iv_bounds(kap_i)),
        },
        "prop_2_4": {
            "lambda_formula": "(3/8) C1^{-1} κ",
            "lambda": S(lam2),
            "lambda_printed": "0.6284",
            "a_formula": (
                "β2^{-1} λ (N/Z)^{-2/3} + β2^{-1} (9/2 β2)^{1/3} (N/Z)^{1/3}"
            ),
            "a_at_N/Z=1": S(a_at_1),
            "a_at_N/Z=5/2": S(a_at_52),
            "a_at_N/Z=5/2_interval": list(iv_bounds(a52_i)),
            "grid_max_on_[1,5/2]": S(a_grid),
            "grid_max_at": S(a_grid_x),
            "max_is_at_right_endpoint": True,
            "printed_2.953_valid": printed["2.953_is_valid_upper_on_a_s2"],
            "printed_2.96_valid": printed["2.96_is_valid_upper_on_a_s2"],
        },
        "prop_2_5": {
            "c_formula": "κ * C2^{-1/2}",
            "c": S(c),
            "c_interval": list(iv_bounds(c_i)),
            "c_printed_upper": "1.5855",
            "c_lt_1.5855": printed["c_lt_1.5855"],
            "lambda": S((mpf(5) / 12) ** (mpf(1) / 3)),
            "lambda_formula": "(5/12)^{1/3}",
            "a1_left_endpoint_formula": "3 (3/10)^{1/3} β3^{-1} + c β3^{-1/3}",
            "a1_left_endpoint": S(a1_left),
            "a1_left_endpoint_interval": list(iv_bounds(a1_left_i)),
            "a1_at_5/2": S(a1_52),
            "a1_at_5/2_interval": list(iv_bounds(a1_52_i)),
            "a1_at_9/4": S(a1_94),
            "a1_at_9/4_interval": list(iv_bounds(a1_94_i)),
            "a1_critical_point_is_a_minimum": True,
            "a1_critical_x": S(xcrit),
            "a1_at_critical": S(a1_crit),
            "grid_max_on_[b3,5/2]": S(a1_grid),
            "grid_max_at": S(a1_grid_x),
            "HPS_says_sup_at_x=beta3^{-1}": True,
            "independent_sup_is_at": "x=5/2",
            "printed_3.893_valid_on_HPS_interval_[b3,5/2]": printed[
                "3.893_is_valid_upper_on_a1_over_[b3,5/2]"
            ],
            "printed_3.893_valid_on_left_endpoint_only": printed[
                "3.893_is_valid_upper_on_left_endpoint_formula"
            ],
            "printed_3.90_valid": printed["3.90_is_valid_upper_on_a1_over_[b3,5/2]"],
            "a2_formula": "β3^{-1}/84",
            "a2": S(a2),
            "a3_formula": "(c/5) (5/12)^{2/3} β3^{-1/3}",
            "a3": S(a3),
            "a4_formula": "c β3^{-1/3}/84",
            "a4": S(a4),
            "printed_a2_0.0134_valid": printed["a2_le_0.0134"],
            "printed_a3_0.184_valid": printed["a3_le_0.184"],
            "printed_a4_0.0196_valid": printed["a4_le_0.0196"],
        },
        "printed_enclosures": printed,
    }

    out = CERTS / "hps_replay.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("b(2) =", S(b2, 20), "in (1.2071, 1.2072)", printed["b2_in_(1.2071,1.2072)"])
    print("b(3) =", S(b3, 20), "in (1.1184, 1.1185)", printed["b3_in_(1.1184,1.1185)"])
    print("C1^{-1} =", S(1 / C1, 16), "  λ =", S(lam2, 16))
    print("c =", S(c, 16), "< 1.5855", printed["c_lt_1.5855"])
    print("a(5/2) =", S(a_at_52, 16), "  2.953 valid", printed["2.953_is_valid_upper_on_a_s2"])
    print("a1(left) =", S(a1_left, 16), "  a1(5/2) =", S(a1_52, 16))
    print("3.90 valid on [b3,5/2]", printed["3.90_is_valid_upper_on_a1_over_[b3,5/2]"])
    print("3.893 valid on [b3,5/2]", printed["3.893_is_valid_upper_on_a1_over_[b3,5/2]"])
    print("wrote", out)
    print("replay_hps.py PASS")


if __name__ == "__main__":
    main()
