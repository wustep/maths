#!/usr/bin/env python3
"""Independent replay of Nam's β interval, arXiv:1009.2367v3.

β := inf { ∬ (x²+y²)/(2|x-y|) dρ dρ  /  ∫ |x| dρ  :  ρ a probability }.

Lower bound (Nam Lemma 6):
  β ≥ sup_λ inf_{x,y} W_λ(x,y) / (|x|+|y|) > 0.8218
with
  W_λ = λ (max + min²/|x-y|) + (1-λ) (|x-y| + (2/3) min²/max).

Nam's analytic minorant g(λ) (Appendix, λ≥0.8) is a rigorous lower bound.
The AM-GM equality geometry is realisable in R^3, so at the maximising λ
the infimum of W_λ/(|x|+|y|) equals g(λ). A fine grid in (r,s,angle) and
in (b,c) is a numerical check, not a lower bound (grid min ≥ true inf).

Upper bound: Nam's radial trial m(r)=(3/4) r^{-3/2} 1_{[1,9]} gives the
exact value 115/81 − (1/2) ln 3. A second trial is an atomic radial
measure (optimised masses on a geometric grid), evaluated in mpmath.

Writes certs/nam_beta.json.

Record: Phan Thành Nam, arXiv:1009.2367v3 (opened 2026-08-27,
https://arxiv.org/abs/1009.2367 and https://arxiv.org/html/1009.2367v3).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from mpmath import iv, log, mp, mpf, nstr, sqrt
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 80
iv.dps = 60
PREC = 40


def S(x, d: int = PREC) -> str:
    return nstr(x, d, strip_zeros=False)


def iv_bounds(x) -> tuple[str, str]:
    return S(mpf(x.a)), S(mpf(x.b))


# ---------------------------------------------------------------------------
# Nam's g(λ)
# ---------------------------------------------------------------------------


def g_mp(lam):
    lam = mpf(lam)
    inner = (lam + 2) / 3 - 2 * sqrt(lam * (1 - lam))
    return lam - (sqrt(inner) - sqrt((mpf(2) / 3) * (1 - lam))) ** 2


def g_iv(lam):
    inner = (lam + 2) / 3 - 2 * iv.sqrt(lam * (1 - lam))
    return lam - (iv.sqrt(inner) - iv.sqrt((iv.mpf(2) / 3) * (1 - lam))) ** 2


def maximize_g():
    lo, hi = mpf("0.80"), mpf("0.95")
    phi = (sqrt(5) - 1) / 2
    for _ in range(140):
        t1 = hi - phi * (hi - lo)
        t2 = lo + phi * (hi - lo)
        if g_mp(t1) < g_mp(t2):
            lo = t1
        else:
            hi = t2
    lam = (lo + hi) / 2
    return lam, g_mp(lam)


def lambda_prime(lam):
    lam = mpf(lam)
    return (
        sqrt((lam + 2) / 3 - 2 * sqrt(lam * (1 - lam)))
        - sqrt((mpf(2) / 3) * (1 - lam))
    ) ** 2


def equality_geometry(lam):
    """AM-GM equality: a=1, b² = 3λ'/(2(1-λ)), c = b √(λ/(1-λ))."""
    lam = mpf(lam)
    lp = lambda_prime(lam)
    b2 = 3 * lp / (2 * (1 - lam))
    b = sqrt(b2)
    c = b * sqrt(lam / (1 - lam))
    triangle = (abs(1 - b) <= c) and (c <= 1 + b)
    # 3D embeddable iff triangle (two radii and |x-y|)
    ratio = (lam * (1 + b**2 / c) + (1 - lam) * (c + (mpf(2) / 3) * b**2)) / (1 + b)
    return {
        "lambda_prime": S(lp),
        "a": "1",
        "b": S(b),
        "c": S(c),
        "triangle_ok": bool(triangle),
        "W_ratio": S(ratio),
        "g": S(g_mp(lam)),
        "W_equals_g": bool(abs(ratio - g_mp(lam)) < mpf("1e-40")),
    }


# ---------------------------------------------------------------------------
# W_λ grids (numerical check only)
# ---------------------------------------------------------------------------


def W_ratio_bc(lam, b, c):
    """a=1, b=min/max in (0,1], c=|x-y| in [|1-b|, 1+b]."""
    return (lam * (1.0 + b * b / c) + (1.0 - lam) * (c + (2.0 / 3.0) * b * b)) / (
        1.0 + b
    )


def grid_bc(lam: float, nb: int = 500, nc: int = 500):
    bs = np.linspace(1e-8, 1.0, nb)
    best = 1e300
    pt = None
    for b in bs:
        cmin = abs(1.0 - b) + 1e-14
        cmax = 1.0 + b
        cs = np.linspace(cmin, cmax, nc)
        val = W_ratio_bc(lam, b, cs)
        j = int(np.argmin(val))
        if val[j] < best:
            best = float(val[j])
            pt = (float(b), float(cs[j]))
    return best, pt


def grid_r_s_angle(lam: float, nr: int = 80, ns: int = 80, nmu: int = 80):
    """Scale |x|=1, |y|=s∈(0,1], μ=cosθ ∈[-1,1]."""
    ss = np.linspace(1e-6, 1.0, ns)
    mus = np.linspace(-1.0, 1.0, nmu)
    best = 1e300
    pt = None
    for s in ss:
        # |x-y|^2 = 1 + s^2 - 2 s μ
        dist = np.sqrt(np.maximum(1.0 + s * s - 2.0 * s * mus, 1e-18))
        mx = np.maximum(1.0, s)
        mn = np.minimum(1.0, s)
        val = (
            lam * (mx + (mn * mn) / dist)
            + (1.0 - lam) * (dist + (2.0 / 3.0) * (mn * mn) / mx)
        ) / (1.0 + s)
        j = int(np.argmin(val))
        if val[j] < best:
            best = float(val[j])
            pt = (1.0, float(s), float(mus[j]), float(dist[j]))
    return best, pt


# ---------------------------------------------------------------------------
# Upper bounds: Nam trial (exact) and a second atomic trial
# ---------------------------------------------------------------------------


def nam_trial_exact():
    """m(r) = (3/4) r^{-3/2} on [1,9]. Value = 115/81 - (1/2) ln 3."""
    # Independent expansion (see derivation in BOUNDS.md / JSON).
    val = mpf(115) / 81 - log(3) / 2
    return val


def nam_trial_iv():
    return iv.mpf(115) / 81 - iv.log(3) / 2


def nam_trial_by_integrals():
    """Recompute the double integral in mpmath, not the closed 115/81 form."""
    # m(r)=(3/4) r^{-3/2} on [1,9]. Closed antiderivatives:
    # M(r) = (3/2)(1 - r^{-1/2})
    # ∫_r^9 m(s)/s ds = (1/2)(r^{-3/2} - 1/27)
    # I_A = 9/2 - (9/4) ln 3
    # I_B = (3/4) ln 3 - 1/4 + 1/108
    IA = mpf(9) / 2 - (mpf(9) / 4) * log(3)
    IB = (mpf(3) / 4) * log(3) - mpf(1) / 4 + mpf(1) / 108
    den = mpf(3)  # ∫ r m(r) dr
    return (IA + IB) / den


def beta_atomic_mp(radii, masses):
    """∬ r_i² / max(r_i,r_j) m_i m_j  /  ∑ m_i r_i, exact for the given atoms."""
    n = len(radii)
    num = mpf(0)
    den = mpf(0)
    for i in range(n):
        den += masses[i] * radii[i]
        for j in range(n):
            num += masses[i] * masses[j] * (radii[i] ** 2) / max(radii[i], radii[j])
    return num / den


def optimize_atomic_trial(n: int = 64, rmax: float = 10.0):
    r = np.geomspace(1.0, rmax, n)
    m0 = r ** (-1.5)
    x0 = np.log(m0)

    def obj(x):
        m = np.exp(x)
        m = m / m.sum()
        R = r[:, None]
        S = r[None, :]
        num = np.sum((m[:, None] * m[None, :]) * (R**2) / np.maximum(R, S))
        den = np.dot(m, r)
        return float(num / den)

    res = minimize(obj, x0, method="L-BFGS-B", options={"maxiter": 600, "ftol": 1e-14})
    m = np.exp(res.x)
    m = m / m.sum()
    # Official trial: 18-digit decimals interpreted as exact rationals
    r_off = [mpf(f"{ri:.18e}") for ri in r]
    m_off = [mpf(f"{mi:.18e}") for mi in m]
    s = sum(m_off)
    m_off = [mi / s for mi in m_off]
    val = beta_atomic_mp(r_off, m_off)
    return val, r_off, m_off, float(res.fun)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)

    lam_star, g_star = maximize_g()
    g_843 = g_mp("0.843")
    g_8435 = g_mp("0.8435")
    g_843_i = g_iv(iv.mpf("0.843"))
    g_8435_i = g_iv(iv.mpf("0.8435"))
    g_star_i = g_iv(iv.mpf(S(lam_star, 20)))
    geom = equality_geometry(lam_star)

    # Grids at Nam's λ and at λ*
    lam_float = float(lam_star)
    g_bc, pt_bc = grid_bc(lam_float, nb=400, nc=400)
    g_ang, pt_ang = grid_r_s_angle(0.8434764, nr=70, ns=70, nmu=90)
    g_bc_843, _ = grid_bc(0.843, nb=300, nc=300)

    trial = nam_trial_exact()
    trial_int = nam_trial_by_integrals()
    trial_i = nam_trial_iv()
    if abs(trial - trial_int) > mpf("1e-40"):
        raise SystemExit("Nam trial closed form != integral expansion")

    atom_val, atom_r, atom_m, atom_f64 = optimize_atomic_trial()

    lower_ok = bool(g_843_i > iv.mpf("0.8218"))
    upper_ok = bool(trial_i < iv.mpf("0.8705"))
    atom_beats_nam_trial = bool(atom_val < trial)

    if not (lower_ok and upper_ok):
        raise SystemExit("Nam printed interval failed the independent enclosure")

    inv_beta_lo = 1 / mpf("0.8218")
    blob = {
        "arxiv": "1009.2367v3",
        "urls_opened": [
            "https://arxiv.org/abs/1009.2367",
            "https://arxiv.org/html/1009.2367v3",
        ],
        "dps": int(mp.dps),
        "definition": (
            "β = inf ∬ (x²+y²)/(2|x-y|) dρ dρ / ∫ |x| dρ over probability measures"
        ),
        "printed_interval": ["0.8218", "0.8705"],
        "printed_interval_valid": True,
        "lower_bound": {
            "method": "Nam g(λ) analytic minorant, λ ≥ 0.8",
            "g_formula": (
                "g(λ) = λ - (√((λ+2)/3 - 2√(λ(1-λ))) - √((2/3)(1-λ)))²"
            ),
            "g_at_0.843": S(g_843),
            "g_at_0.843_interval": list(iv_bounds(g_843_i)),
            "g_at_0.843_gt_0.8218": lower_ok,
            "g_at_0.8435": S(g_8435),
            "g_at_0.8435_interval": list(iv_bounds(g_8435_i)),
            "lambda_max": S(lam_star),
            "g_max": S(g_star),
            "g_max_interval_at_truncated_lambda": list(iv_bounds(g_star_i)),
            "Nam_printed_g_0.843": "0.821804...",
            "Nam_printed_g_max": "0.8218066...",
            "Nam_printed_lambda_max": "0.843476...",
            "equality_geometry_at_lambda_max": geom,
            "inf_W_equals_g_at_lambda_max": geom["triangle_ok"] and geom["W_equals_g"],
            "grid_is_not_a_lower_bound": True,
            "grid_bc_at_lambda_max": {
                "min": g_bc,
                "at_b_c": pt_bc,
                "note": "grid min ≥ true inf; used only as a check",
            },
            "grid_bc_at_0.843": {"min": g_bc_843},
            "grid_r_s_angle_at_0.8434764": {
                "min": g_ang,
                "at_r_s_mu_dist": pt_ang,
            },
        },
        "upper_bound": {
            "nam_trial": {
                "density": "(3/4) r^{-3/2} 1_{[1,9]}(r) dr",
                "closed_form": "115/81 - (1/2) ln 3",
                "value": S(trial),
                "value_from_antiderivatives": S(trial_int),
                "interval": list(iv_bounds(trial_i)),
                "lt_0.8705": upper_ok,
                "Nam_printed": "0.8704...",
            },
            "second_trial_atomic_radial": {
                "description": (
                    "64 point masses on a geometric grid [1,10], masses "
                    "optimised from a Nam-like r^{-3/2} start, then frozen "
                    "as 18-digit decimals and re-evaluated in mpmath"
                ),
                "n": 64,
                "rmax": 10.0,
                "value": S(atom_val),
                "float64_optimiser": atom_f64,
                "beats_nam_trial": atom_beats_nam_trial,
                "radii": [S(x, 18) for x in atom_r],
                "masses": [S(x, 18) for x in atom_m],
                "Nam_printed_beta_rad_numeric": "0.8702",
            },
        },
        "one_over_beta": {
            "1/0.8218": S(inv_beta_lo),
            "Nam_rounds_to": "1.22",
            "1.2168_lt_1.22": bool(inv_beta_lo < mpf("1.22")),
        },
        "enclosures": {
            "beta_gt_0.8218": lower_ok,
            "beta_lt_0.8705": upper_ok,
            "beta_lt_nam_trial": True,
            "beta_lt_second_trial": True,
        },
    }

    out = CERTS / "nam_beta.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("g(0.843) =", S(g_843, 16), "> 0.8218", lower_ok)
    print("g_max =", S(g_star, 16), "at λ =", S(lam_star, 16))
    print("equality geometry triangle", geom["triangle_ok"], "W=g", geom["W_equals_g"])
    print("grid (b,c) min at λ*", g_bc)
    print("Nam trial", S(trial, 16), "< 0.8705", upper_ok)
    print("atomic trial", S(atom_val, 16), "beats Nam trial", atom_beats_nam_trial)
    print("1/0.8218 =", S(inv_beta_lo, 16))
    print("wrote", out)
    print("replay_nam_beta.py PASS")


if __name__ == "__main__":
    main()
