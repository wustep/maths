#!/usr/bin/env python3
"""Tighten HPS remainders without changing the theorem.

Same chain as Hundertmark–Pattakos–Schulz arXiv:2504.18487v1 §7, with
tighter arithmetic:

  (1) exact b(3) in a1, not the printed 1.1185;
  (2) N/Z < 2+1/Z (Lieb) per real Z≥4, so N/Z < 9/4, not 5/2;
  (3) evaluate a1(x) on that interval (the max is at the left endpoint
      once the right end is 9/4, not 5/2);
  (4) scan λ including lower-order terms — HPS λ=(5/12)^{1/3} already
      minimises the left-endpoint a1, so this does not move a1;
  (5) mpmath interval enclosures of every claimed decimal.

A dent is a verified strict improvement of a printed record. Here:
  printed Prop. 2.4 remainder 2.96  →  a < 2.953  (Z≥2);
  printed Prop. 2.5 remainder 3.90  →  a1 < 3.892  (Z≥4, Lieb 9/4);
  printed simplified 4              →  remainder coeff < 3.9781 (Z≥4).

Do not claim a leading coefficient below 1.1185: that would need a new
argument for β3. The LT factor stays 1.456 (FHJN arXiv:1808.09017);
a later variational claim 1.44655 (arXiv:2403.04347) was not replayed
and is not used.

Writes certs/hps_tight.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr, pi, sqrt

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

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


def b2_iv():
    return (iv.sqrt(2) + 1) / 2


def b3_iv():
    u = iv_cbrt(1 + iv.sqrt(2))
    return (iv.mpf(2) / 3) * u / (u**2 - 1)


def beta2_iv():
    return 2 * (iv.sqrt(2) - 1)


def beta3_iv():
    return 1 / b3_iv()


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


def lam2_iv():
    return (iv.mpf(3) / 8) * (1 / C1_iv()) * kappa_iv()


def a_s2_iv(x):
    return (1 / beta2_iv()) * lam2_iv() * iv_pow(x, iv.mpf(-2) / 3) + (
        1 / beta2_iv()
    ) * iv_cbrt((iv.mpf(9) / 2) * beta2_iv()) * iv_cbrt(x)


def a1_hps_iv(x, lam=None):
    """HPS (7.32) after the Z < N β3 replacement, general λ."""
    if lam is None:
        coeff = 3 * iv_cbrt(iv.mpf(3) / 10)
    else:
        coeff = 1 / lam + (iv.mpf(6) / 5) * lam**2
    b3 = b3_iv()
    beta3 = 1 / b3
    return coeff * iv_pow(beta3, iv.mpf(-2) / 3) * iv_cbrt(x) + c_iv() * (
        1 / beta3
    ) * iv_pow(x, iv.mpf(-2) / 3)


def a1_exact_x_iv(x, lam):
    """Keep (λ²/5)(Nβ3)^{-2/3} Z as a function of x = N/Z (equality at x=β3^{-1})."""
    b3 = b3_iv()
    beta3 = 1 / b3
    t1 = (1 / lam + lam**2) * iv_pow(beta3, iv.mpf(-2) / 3) * iv_cbrt(x)
    t2 = (lam**2 / 5) * iv_pow(beta3, iv.mpf(-5) / 3) * iv_pow(x, iv.mpf(-2) / 3)
    t3 = c_iv() * (1 / beta3) * iv_pow(x, iv.mpf(-2) / 3)
    return t1 + t2 + t3


def extras_iv():
    b3 = b3_iv()
    beta3 = 1 / b3
    c = c_iv()
    a2 = b3 / 84
    a3 = (c / 5) * iv_pow(iv.mpf(5) / 12, iv.mpf(2) / 3) * iv_cbrt(b3)
    a4 = c * iv_cbrt(b3) / 84
    return a2, a3, a4


def r_max_iv():
    """Largest r = λ (N β3)^{-1/3} on the contradiction set N ≥ β3^{-1} Z, Z≥4."""
    lam = iv_cbrt(iv.mpf(5) / 12)
    # N β3 ≥ Z ≥ 4
    return lam / iv_cbrt(iv.mpf(4))


def scan_lambda(n: int = 200):
    """High-prec (not interval) scan of λ on the Z≥4 interval [b3, 9/4]."""
    b3 = (mpf(2) / 3) * (1 + sqrt(2)) ** (mpf(1) / 3) / (
        (1 + sqrt(2)) ** (mpf(2) / 3) - 1
    )
    beta3 = 1 / b3
    C1 = (
        (3 ** (mpf(5) / 3))
        * (5 ** (mpf(5) / 6))
        * ((7 / pi) ** (mpf(1) / 3))
        / (22 * sqrt(11))
    )
    kap = sqrt(5) * ((2 / (9 * pi**2) * LT) ** (mpf(1) / 3))
    c = kap * 4 * (pi ** (mpf(2) / 3)) / sqrt(15)
    hi = mpf(9) / 4

    def a1(x, lam):
        coeff = 1 / lam + (mpf(6) / 5) * lam**2
        return coeff * beta3 ** (-mpf(2) / 3) * x ** (mpf(1) / 3) + c * (
            1 / beta3
        ) * x ** (-mpf(2) / 3)

    best = None
    hps_lam = (mpf(5) / 12) ** (mpf(1) / 3)
    for i in range(1, n):
        lam = mpf(i) / n * mpf("0.79")
        if lam < mpf("0.3"):
            continue
        # r ≤ 0.5 on Z≥4, N≥β3^{-1} Z requires λ ≤ 0.5 * 4^{1/3}
        if lam > mpf("0.5") * (mpf(4) ** (mpf(1) / 3)):
            continue
        val = max(a1(b3, lam), a1(hi, lam))
        if best is None or val < best[0]:
            best = (val, lam)
    hps_val = max(a1(b3, hps_lam), a1(hi, hps_lam))
    return {
        "best_lambda": S(best[1]),
        "best_max_a1": S(best[0]),
        "hps_lambda": S(hps_lam),
        "hps_max_a1": S(hps_val),
        "moved_a1": bool(best[0] < hps_val - mpf("1e-12")),
    }


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)

    b3i = b3_iv()
    a52 = a_s2_iv(iv.mpf(5) / 2)
    a1_left = a1_hps_iv(b3i)
    a1_94 = a1_hps_iv(iv.mpf(9) / 4)
    a1_52 = a1_hps_iv(iv.mpf(5) / 2)
    a1_2 = a1_hps_iv(iv.mpf(2))
    a2, a3, a4 = extras_iv()
    Z4 = iv.mpf(4)
    coeff4 = (
        a1_left
        + a2 * iv_pow(Z4, iv.mpf(-1) / 3)
        + a3 * iv_pow(Z4, iv.mpf(-2) / 3)
        + a4 / Z4
    )
    rmax = r_max_iv()
    lam_scan = scan_lambda()

    # Equality at x=β3^{-1}: exact-x a1 coincides with HPS a1
    a1_exact_left = a1_exact_x_iv(b3i, iv_cbrt(iv.mpf(5) / 12))

    dent_a_2953 = bool(a52 < iv.mpf("2.953"))
    dent_a1_3892 = bool(a1_left < iv.mpf("3.892") and a1_94 < a1_left)
    dent_4 = bool(coeff4 < iv.mpf("3.9781"))
    r_ok = bool(rmax < iv.mpf("0.5"))

    if not (dent_a_2953 and dent_a1_3892 and dent_4 and r_ok):
        status = "residue"
        reason = (
            "an enclosure failed: "
            f"a<2.953={dent_a_2953}, a1<3.892={dent_a1_3892}, "
            f"coeff<3.9781={dent_4}, r<0.5={r_ok}"
        )
    else:
        status = "dent"
        reason = (
            "interval-certified improvements of the printed HPS remainders "
            "2.96, 3.90, and 4, using the same Section 7 chain"
        )

    # Published-style inequalities (decimal enclosures)
    inequalities = [
        {
            "beats": "HPS Prop. 2.4 printed remainder 2.96",
            "range": "Z >= 2",
            "inequality": "N_c < b(2) Z + 2.953 Z^{1/3}",
            "b2": "(sqrt(2)+1)/2",
        },
        {
            "beats": "HPS Prop. 2.5 printed remainder 3.90",
            "range": "Z >= 4",
            "inequality": (
                "N < b(3) Z + 3.892 Z^{1/3} + 0.0134 + 0.184 Z^{-1/3} "
                "+ 0.0196 Z^{-2/3}"
            ),
            "b3": "(2/3)(1+sqrt(2))^{1/3}/((1+sqrt(2))^{2/3}-1)",
            "note": (
                "same extras as the printed (2.9); only a1 is tightened. "
                "Uses Lieb N/Z < 2+1/Z <= 9/4 so the a1 max is at x=b(3)."
            ),
        },
        {
            "beats": "HPS simplified printed remainder 4",
            "range": "Z >= 4",
            "inequality": "N_c < b(3) Z + 3.9781 Z^{1/3}",
        },
        {
            "beats": "HPS simplified printed remainder 4 (with 1.1185 kept)",
            "range": "Z >= 4",
            "inequality": "N_c < 1.1185 Z + 3.9781 Z^{1/3}",
            "note": "1.1185 is still only an enclosure of b(3), not a new leading coefficient",
        },
    ]

    blob = {
        "status": status,
        "reason": reason,
        "arxiv": "2504.18487v1",
        "theorem_unchanged": True,
        "did_not_beat_1.1185": True,
        "LT_factor": "1.456",
        "LT_source": "Frank–Hundertmark–Jex–Nam arXiv:1808.09017 Theorem 1",
        "later_LT_lead_not_used": {
            "arxiv": "2403.04347",
            "claimed": "L_{1,1,1}/L^{cl} <= 1.44655",
            "why_not_used": "not independently replayed",
        },
        "tightenings": {
            "1_exact_b3_in_a1": True,
            "2_Lieb_N/Z_lt_2+1/Z_for_Z_ge_4": True,
            "3_actual_a1_function": True,
            "4_optimize_lambda": lam_scan,
            "5_interval_enclosures": True,
        },
        "why_lambda_did_not_move_a1": (
            "For Z>=4 the allowed x-interval is [b(3), 9/4]. a1(x) has a "
            "minimum inside and the larger endpoint is x=b(3). At that "
            "point Z = N β3, so the crude replacement Z < N β3 is equality, "
            "and a1 = (λ^{-1}+6λ²/5) β3^{-1} + c β3^{-1/3}, which HPS already "
            "minimises by λ=(5/12)^{1/3}."
        ),
        "HPS_5/2_interval_replay": {
            "a1_at_left": list(iv_bounds(a1_left)),
            "a1_at_5/2": list(iv_bounds(a1_52)),
            "sup_is_at": "x=5/2",
            "3.893_valid_on_5/2_interval": bool(a1_52 < iv.mpf("3.893")),
            "3.90_valid_on_5/2_interval": bool(a1_52 < iv.mpf("3.90")),
            "note": (
                "HPS claimed the sup on [β3^{-1}, 5/2] is at the left. "
                "Independently the sup is at 5/2 and is < 3.90 but not < 3.893. "
                "Prop. 2.5 is only stated for Z>=4, where Lieb gives 9/4 not 5/2."
            ),
        },
        "intermediates": {
            "b2_interval": list(iv_bounds(b2_iv())),
            "b3_interval": list(iv_bounds(b3i)),
            "kappa_interval": list(iv_bounds(kappa_iv())),
            "C1_inv_interval": list(iv_bounds(1 / C1_iv())),
            "C2_inv_sqrt_interval": list(iv_bounds(C2inv_iv())),
            "c_interval": list(iv_bounds(c_iv())),
            "lambda_s2_interval": list(iv_bounds(lam2_iv())),
            "lambda_s3": S((mpf(5) / 12) ** (mpf(1) / 3)),
            "a_s2_at_5/2": list(iv_bounds(a52)),
            "a1_at_b3": list(iv_bounds(a1_left)),
            "a1_exact_x_at_b3": list(iv_bounds(a1_exact_left)),
            "a1_at_9/4": list(iv_bounds(a1_94)),
            "a1_at_2": list(iv_bounds(a1_2)),
            "a2": list(iv_bounds(a2)),
            "a3": list(iv_bounds(a3)),
            "a4": list(iv_bounds(a4)),
            "Z4_remainder_coeff": list(iv_bounds(coeff4)),
            "r_max_on_contradiction_set": list(iv_bounds(rmax)),
            "r_max_lt_0.5": r_ok,
        },
        "enclosures": {
            "a_s2_lt_2.953": dent_a_2953,
            "a1_lt_3.892": dent_a1_3892,
            "a1_lt_3.893": bool(a1_left < iv.mpf("3.893")),
            "a2_lt_0.01332": bool(a2 < iv.mpf("0.01332")),
            "a2_lt_0.0134": bool(a2 < iv.mpf("0.0134")),
            "a3_lt_0.18362": bool(a3 < iv.mpf("0.18362")),
            "a3_lt_0.184": bool(a3 < iv.mpf("0.184")),
            "a4_lt_0.01960": bool(a4 < iv.mpf("0.01960")),
            "Z4_coeff_lt_3.9781": dent_4,
            "Z4_coeff_lt_3.979": bool(coeff4 < iv.mpf("3.979")),
        },
        "inequalities": inequalities,
    }

    out = CERTS / "hps_tight.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("status:", status)
    print("a(5/2) < 2.953:", dent_a_2953, iv_bounds(a52))
    print("a1(left) < 3.892 and > a1(9/4):", dent_a1_3892, iv_bounds(a1_left))
    print("Z=4 coeff < 3.9781:", dent_4, iv_bounds(coeff4))
    print("r_max < 0.5:", r_ok, iv_bounds(rmax))
    print("λ scan moved a1:", lam_scan["moved_a1"])
    print("wrote", out)
    if status != "dent":
        raise SystemExit("tighten_hps.py residue (no certified dent)")
    print("tighten_hps.py PASS")


if __name__ == "__main__":
    main()
