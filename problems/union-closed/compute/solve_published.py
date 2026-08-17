"""Independently recompute the published frequency constants.

Uses mpmath dps=80.  Writes compute/published_constants.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from mpmath import mp, mpf, log, sqrt, findroot, nstr

mp.dps = 80
LN2 = log(2)


def h(p):
    p = mpf(p)
    if p <= 0 or p >= 1:
        return mpf(0)
    return -(p * log(p) + (1 - p) * log(1 - p)) / LN2


def gilmer_phi():
    """(3-√5)/2, the unique root in (0,1/2) of h(2p-p²)=h(p)."""
    return (3 - sqrt(5)) / 2


def check_gilmer_equality(phi):
    return h(2 * phi - phi**2) - h(phi)


def cambie_b_equation(b):
    """h(b)(2 - h(b)) - h((1-b)²) = 0."""
    return h(b) * (2 - h(b)) - h((1 - b) ** 2)


def solve_cambie():
    b1 = findroot(cambie_b_equation, mpf("0.14"))
    b2 = findroot(cambie_b_equation, mpf("0.33"))
    # a from (1-a) h(b̄²) = h(b)
    def a_of(b):
        hb = h(b)
        hbb = h((1 - b) ** 2)
        return 1 - hb / hbb

    a1, a2 = a_of(b1), a_of(b2)
    # also check the h(1/2) form: (1-2a) = (1-a) h(b)
    def a_alt(b):
        hb = h(b)
        return (1 - hb) / (2 - hb)

    c1 = a1 + (1 - a1) * b1
    c2 = a2 + (1 - a2) * b2
    return {
        "b_small": b1,
        "a_small": a1,
        "a_small_alt": a_alt(b1),
        "c_small": c1,
        "b_star": b2,
        "a_star": a2,
        "a_star_alt": a_alt(b2),
        "c_star": c2,
        "eq_residual_b1": cambie_b_equation(b1),
        "eq_residual_b2": cambie_b_equation(b2),
        "a_forms_agree_b2": a2 - a_alt(b2),
    }


def alpha_star(a, b):
    """Liu (15) / Cambie derivative formula for the Sawin mix weight."""
    # Use finite-difference of the mix along mean-preserving direction.
    # Liu closed form (PDF garbled); recompute from the two-point mix.
    abar = 1 - a
    bbar = 1 - b
    # g1 = E[h(S̄T̄)] - E[h(S)] at the two-point {b,1} with P(1)=a
    # E[h(S)] = (1-a) h(b)
    # E[h(S̄T̄)] = (1-a)² h(b̄²)
    # g2 maxent: P(b,b)=1-2a, P(b,1)=P(1,b)=a, P(1,1)=0
    #   E[h(maxent)] = (1-2a) h(min(2b, 1/2)) + 2a h(max(b,1,min(b+1,1/2)))
    #                = (1-2a) * 1  +  2a * h(1) = 1-2a
    # since min(2b,1/2)=1/2 when b≥1/4 (b*≈0.329).
    #
    # α is chosen so the directional derivative of
    #   (1-α) E h_iid + α E h_maxent - E h
    # vanishes along {da, db : dE[S]=0}.
    #
    # Recompute by 2-variable implicit differentiation as Liu does,
    # using high-precision finite differences as a check, and also
    # the exact 2-point derivatives.

    def pack(aa, bb):
        eh = (1 - aa) * h(bb)
        eiid = (1 - aa) ** 2 * h((1 - bb) ** 2)
        emax = (1 - 2 * aa) * h(min(2 * bb, mpf("0.5")))
        # the 2a cross terms: max(b,1,min(b+1,1/2)) = 1, h=0
        mean = aa + (1 - aa) * bb
        return eh, eiid, emax, mean

    eh, eiid, emax, mean = pack(a, b)
    # partials via 1e-24 steps
    eps = mpf("1e-24")
    _, eiid_a, emax_a, mean_a = pack(a + eps, b)
    eh_a = ((1 - (a + eps)) * h(b) - eh) / eps
    diid_a = (eiid_a - eiid) / eps
    dmax_a = (emax_a - emax) / eps
    dmean_a = (mean_a - mean) / eps

    _, eiid_b, emax_b, mean_b = pack(a, b + eps)
    eh_b = ((1 - a) * h(b + eps) - eh) / eps
    diid_b = (eiid_b - eiid) / eps
    dmax_b = (emax_b - emax) / eps
    dmean_b = (mean_b - mean) / eps

    # direction (da, db) with dmean = 0: da * dmean_a + db * dmean_b = 0
    # take da = dmean_b, db = -dmean_a
    da, db = dmean_b, -dmean_a
    # d((1-α) eiid + α emax - eh) = 0
    # (1-α) (diid_a da + diid_b db) + α (dmax_a da + dmax_b db) - (eh_a da + eh_b db) = 0
    A = diid_a * da + diid_b * db  # d eiid
    B = dmax_a * da + dmax_b * db  # d emax
    C = eh_a * da + eh_b * db  # d eh
    # (1-α) A + α B - C = 0  =>  A + α (B-A) = C  => α = (C-A)/(B-A)
    alpha = (C - A) / (B - A)
    return alpha


def solve_liu_two_point():
    """Liu §V-B analytic 2-point (q=0, mass at 0 and x)."""

    def eq(x):
        x = mpf(x)
        xb = 1 - x
        # x² + x² (1 + x̄²) = 1
        return x**2 + x**2 * (1 + xb**2) - 1

    x = findroot(eq, mpf("0.69"))
    # p² h(x²) = p h(x)  =>  p = h(x)/h(x²)
    p = h(x) / h(x**2)
    c = 1 - p * x

    # β from vanishing derivative along d(p x)=0
    def pack(pp, xx):
        eh = pp * h(xx)
        eiid = pp**2 * h(xx**2)
        # CIID Example 5, f(u)=u(1-u), complements: I = xy(1+x̄ȳ)
        I = (xx**2) * (1 + (1 - xx) ** 2)
        eciid = pp**2 * h(I)
        mean_comp = pp * xx  # E[X] = p x,  E[S] = 1 - p x
        return eh, eiid, eciid, mean_comp

    eh, eiid, eciid, mc = pack(p, x)
    eps = mpf("1e-24")
    eh_p, eiid_p, eciid_p, mc_p = pack(p + eps, x)
    eh_x, eiid_x, eciid_x, mc_x = pack(p, x + eps)
    deh_p = (eh_p - eh) / eps
    diid_p = (eiid_p - eiid) / eps
    dci_p = (eciid_p - eciid) / eps
    dmc_p = (mc_p - mc) / eps
    deh_x = (eh_x - eh) / eps
    diid_x = (eiid_x - eiid) / eps
    dci_x = (eciid_x - eciid) / eps
    dmc_x = (mc_x - mc) / eps
    da, db = dmc_x, -dmc_p  # d(px)=0
    A = diid_p * da + diid_x * db
    B = dci_p * da + dci_x * db
    C = deh_p * da + deh_x * db
    # d( (1-β) eiid + β eciid - eh ) = 0
    beta = (C - A) / (B - A)
    return {
        "x_star": x,
        "p_star": p,
        "c_liu": c,
        "beta_star": beta,
        "eq_residual": eq(x),
        "iid_ratio": (p**2 * h(x**2)) / (p * h(x)),
        "I": (x**2) * (1 + (1 - x) ** 2),
        "hI_eq_hx2": h((x**2) * (1 + (1 - x) ** 2)) - h(x**2),
    }


def to_float(d):
    out = {}
    for k, v in d.items():
        out[k] = float(v)
        out[k + "_str"] = nstr(v, 40)
    return out


def main():
    phi = gilmer_phi()
    cambie = solve_cambie()
    alpha = alpha_star(cambie["a_star"], cambie["b_star"])
    liu = solve_liu_two_point()

    report = {
        "gilmer_phi": float(phi),
        "gilmer_phi_str": nstr(phi, 40),
        "gilmer_equality_residual": float(check_gilmer_equality(phi)),
        "yu_cambie": to_float(cambie),
        "alpha_star": float(alpha),
        "alpha_star_str": nstr(alpha, 40),
        "liu_two_point": to_float(liu),
        "published_quotes": {
            "cambie_b": 0.329454738503037,
            "cambie_a": 0.0788772927059232,
            "cambie_c": 0.382345533366703,
            "cambie_alpha": 0.03560698136437784,
            "liu_p": 0.893604513905457,
            "liu_x": 0.690787593924988,
            "liu_c": 0.382709087918741,
            "liu_beta": 0.100052559862974,
        },
    }

    # deltas vs published
    report["deltas"] = {
        "c_star_minus_cambie_quote": float(cambie["c_star"]) - 0.382345533366703,
        "alpha_minus_cambie_quote": float(alpha) - 0.03560698136437784,
        "liu_c_minus_quote": float(liu["c_liu"]) - 0.382709087918741,
        "b_star_minus_quote": float(cambie["b_star"]) - 0.329454738503037,
    }

    out = Path(__file__).resolve().parent / "published_constants.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["deltas"], indent=2))
    print("c*     ", nstr(cambie["c_star"], 20))
    print("alpha* ", nstr(alpha, 20))
    print("liu c  ", nstr(liu["c_liu"], 20))
    print("phi    ", nstr(phi, 20))
    print("wrote", out)


if __name__ == "__main__":
    main()
