#!/usr/bin/env python3
"""q3 leftovers: s>3 two-shell replay, and cheap global Toeplitz trials.

Not a lower bound on β_3. Does not run verify_beta3.c. No n>16 faces.

A) Replays the two-shell dipole quadratic of HPS Lemma 4.3 at s=4:
   Q = α² t^{s-1} + β² + αβ (t^{s+ℓ} + t^ℓ) = -1025/2048
   at (s,ℓ,t,α,β) = (4,1,1/8,16,-1). Confirms I_s<0 for s in {3.1,3.5,4}
   and I_3≥0 on the same family. Does not invent a path from this to
   b(4) in Theorem 2.2.

B) After Newton, Q = I/D is an average of f(t)=(1+t³)/(1+t²). This
   file records three cheap candidates for a global floor above
   fmin = 1/b(3) ≈ 0.894107:

     1. two-atom exact min
        Q2* = (17√17 − 55)/16 ≈ 0.943301
        (only a bound on 2-atomic measures; 3-atomic trials sit lower)
     2. geometric t0-chain, closed double sum; Q_n → 1, min at n=3
        ≈ 0.937926 (a trial, hence an upper bound on β_3^{rad})
     3. 1D convolution of f(e^{-|h|}) on log-radius: the kernel is
        ≥ fmin, so Bochner/Fourier recovers fmin; the signed symbol
        at θ=π dips below fmin; a log-Gaussian trial sits near the
        HPS power-law 0.921, not below it.

None of these is a global γ > fmin valid for every radial probability.
Status: residue. Compact-class 1.1087 is not used here.

Writes toeplitz_probe.json next to this file. Replay:
  python3 toeplitz_probe.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from mpmath import iv, mp, mpf, nstr, power, sqrt

HERE = Path(__file__).resolve().parent
mp.dps = 80
iv.dps = 50
PREC = 36

T0 = (1 + sqrt(2)) ** (mpf(1) / 3) - (1 + sqrt(2)) ** (mpf(-1) / 3)
B3 = (mpf(2) / 3) * (1 + sqrt(2)) ** (mpf(1) / 3) / (
    (1 + sqrt(2)) ** (mpf(2) / 3) - 1
)
FMIN = 1 / B3


def S(x, d: int = PREC) -> str:
    return nstr(x, d, strip_zeros=False)


def f_of(t):
    t = mpf(t)
    if t <= 0:
        return mpf(1)
    return (1 + t**3) / (1 + t**2)


def Q_two_shell(s, ell, t, alpha, beta):
    s, t, alpha, beta = mpf(s), mpf(t), mpf(alpha), mpf(beta)
    return (
        alpha**2 * t ** (s - 1)
        + beta**2
        + alpha * beta * (t ** (s + ell) + t**ell)
    )


def Q_two_shell_iv(s, ell, t, alpha, beta):
    s = iv.mpf(str(s))
    ell = iv.mpf(int(ell))
    t = iv.mpf(str(t))
    a = iv.mpf(str(alpha))
    b = iv.mpf(str(beta))
    return a**2 * iv.exp((s - 1) * iv.log(t)) + b**2 + a * b * (
        iv.exp((s + ell) * iv.log(t)) + iv.exp(ell * iv.log(t))
    )


# ---------------------------------------------------------------------------
# A) s>3 two-shell
# ---------------------------------------------------------------------------


def confirm_s_gt_3() -> dict:
    Q4 = Q_two_shell(4, 1, mpf("1/8"), 16, -1)
    Q4_exact = mpf(-1025) / 2048
    if abs(Q4 - Q4_exact) > mpf("1e-60"):
        raise SystemExit(f"s=4 Q is {Q4}, not -1025/2048")
    # Hand expansion, all dyadic:
    # 16²·(1/8)³ + 1 − 16·((1/8)⁵ + 1/8)
    #   = 256/512 + 1 − 16/32768 − 2
    #   = 1/2 + 1 − 1/2048 − 2
    #   = −1/2 − 1/2048 = −1025/2048
    hand = mpf(256) / 512 + 1 - mpf(16) / 32768 - 2
    if abs(hand - Q4_exact) > mpf("1e-60"):
        raise SystemExit("hand expansion of −1025/2048 failed")

    Q35 = Q_two_shell(mpf("7/2"), 1, mpf("1/32"), 64, -1)
    Q35_closed = 1 / sqrt(2) - 1 - 1 / (65536 * sqrt(2))
    if abs(Q35 - Q35_closed) > mpf("1e-50"):
        raise SystemExit("s=7/2 closed form mismatch")

    examples = [
        ("s3_t_1/2", 3, 1, "1/2", 1, -1),
        ("s3_t_1/8_a16", 3, 1, "1/8", 16, -1),
        ("s31_t_1e-7", "3.1", 1, "1e-7", "3e7", -1),
        ("s35_t_1/32", "7/2", 1, "1/32", 64, -1),
        ("s4_t_1/8", 4, 1, "1/8", 16, -1),
        ("s4_quad", 4, 2, "1/8", 16, -1),
        ("s4_same_sign", 4, 1, "1/8", 1, 1),
        ("s4_one_shell", 4, 1, 1, 1, 0),
    ]
    rows = []
    for name, s, ell, t, a, b in examples:
        Q = Q_two_shell(s, ell, t, a, b)
        Qi = Q_two_shell_iv(s, ell, t, a, b)
        sign = (
            "negative"
            if Qi.b < 0
            else (
                "positive"
                if Qi.a > 0
                else ("zero" if Qi.a == 0 == Qi.b else "undetermined")
            )
        )
        rows.append(
            {
                "name": name,
                "s": str(s),
                "ell": ell,
                "t": str(t),
                "Q": S(Q),
                "sign": sign,
            }
        )
    if rows[0]["sign"] != "positive" or rows[1]["sign"] != "positive":
        raise SystemExit("s=3 dipole went non-positive")
    if rows[2]["sign"] != "negative" or rows[3]["sign"] != "negative":
        raise SystemExit("s=3.1 or 3.5 dipole not negative")
    if rows[4]["sign"] != "negative":
        raise SystemExit("s=4 dipole not negative")
    if rows[5]["sign"] != "positive" or rows[6]["sign"] != "positive":
        raise SystemExit("quad / same-sign should stay positive")

    # s=3 dipole discriminant identity
    # (t^4+t)^2 − 4 t^2 = t^2 (t^3−1)(t^3+3) ≤ 0 on (0,1]
    t = mpf("1/3")
    lhs = (t**4 + t) ** 2 - 4 * t**2
    rhs = t**2 * (t**3 - 1) * (t**3 + 3)
    if abs(lhs - rhs) > mpf("1e-60"):
        raise SystemExit("s=3 discriminant identity failed")

    b4, t04 = _b_of(4)
    # t^4 + 4t − 3 = 0 isolates t0
    if not (mpf("0.692") ** 4 + 4 * mpf("0.692") - 3 < 0 < mpf("0.693") ** 4 + 4 * mpf("0.693") - 3):
        raise SystemExit("t0(4) not isolated in (0.692, 0.693)")
    if not (b4 > mpf("1.08302") and b4 < mpf("1.08303")):
        raise SystemExit(f"b(4) unexpected: {b4}")

    return {
        "Q4_exact": "-1025/2048",
        "Q4_value": S(Q4_exact),
        "Q35_closed": "1/sqrt(2) - 1 - 1/(65536 sqrt(2))",
        "Q35_value": S(Q35),
        "Q35_negative": bool(Q35 < 0),
        "s3_discriminant_identity": "(t^4+t)^2 - 4 t^2 = t^2 (t^3-1)(t^3+3)",
        "examples": rows,
        "b4": S(b4),
        "t0_4": S(t04),
        "b4_lt_1.1185": bool(b4 < mpf("1.1185")),
        "I_s_negative_for_s_gt_3": True,
        "certified_path_to_b4_in_Theorem_2_2": False,
    }


def _b_of(s):
    s = mpf(s)

    def fn(t):
        return t**s + s * t + 1 - s

    lo, hi = mpf("1e-30"), mpf(1)
    for _ in range(220):
        mid = (lo + hi) / 2
        if fn(mid) < 0:
            lo = mid
        else:
            hi = mid
    t0 = (lo + hi) / 2
    return (s - 1) / (s * t0), t0


# ---------------------------------------------------------------------------
# B1) two-atom exact min
# ---------------------------------------------------------------------------


def two_atom_Q(t, w):
    """Q for D-mass w at radius 1 and 1-w at radius 1/t, t∈(0,1].

    Q(w,t) = [w² + (1-w)² t² + w(1-w)(1+t³)] / [w + (1-w)t²].
    """
    t, w = mpf(t), mpf(w)
    num = w**2 + (1 - w) ** 2 * t**2 + w * (1 - w) * (1 + t**3)
    den = w + (1 - w) * t**2
    return num / den


def two_atom_exact() -> dict:
    # Critical D-mass at fixed t: w = t/(1+t)  (see the note).
    # Then Q2(t) = (1 + 2t + t³) / (1 + 2t + t²).
    # Q2'(t)=0 iff t=0 or t³ + 4t² + t − 2 = 0.
    # (t+1)(t² + 3t − 2)=0, positive root t* = (−3+√17)/2.
    # Q2* = (17√17 − 55)/16,  1/Q2* = (55 + 17√17)/118.
    tstar = (mpf(-3) + sqrt(17)) / 2
    Qstar_closed = (17 * sqrt(17) - 55) / 16
    inv_closed = (55 + 17 * sqrt(17)) / 118
    wstar = tstar / (1 + tstar)
    Qstar = two_atom_Q(tstar, wstar)
    Q2_of_t = (1 + 2 * tstar + tstar**3) / (1 + 2 * tstar + tstar**2)
    if abs(Qstar - Qstar_closed) > mpf("1e-50"):
        raise SystemExit("two-atom closed form mismatch")
    if abs(Qstar - Q2_of_t) > mpf("1e-50"):
        raise SystemExit("Q2(t*) formula mismatch")
    if abs(1 / Qstar - inv_closed) > mpf("1e-50"):
        raise SystemExit("two-atom inverse mismatch")
    if Qstar <= FMIN:
        raise SystemExit("two-atom min sat at or below fmin; arithmetic bug")

    Q_at_t0 = (3 - T0) / (1 + T0) ** 2  # uses t0³ = 2 − 3 t0
    Q_at_t0_direct = two_atom_Q(T0, T0 / (1 + T0))
    if abs(Q_at_t0 - Q_at_t0_direct) > mpf("1e-50"):
        raise SystemExit("Q2(t0) identity failed")

    # Endpoint check and a coarse grid: the critical w is the unique
    # interior min for each t, and min_t Q2(t) is at t*.
    grid_min = mpf(2)
    for i in range(1, 2000):
        t = mpf(i) / 2000
        val = (1 + 2 * t + t**3) / (1 + 2 * t + t**2)
        if val < grid_min:
            grid_min = val
    if abs(grid_min - Qstar) > mpf("1e-6"):
        raise SystemExit("grid min of Q2 drifted from closed form")

    return {
        "t_star": S(tstar),
        "t_star_closed": "(-3+sqrt(17))/2",
        "w_star": S(wstar),
        "Q2_star": S(Qstar_closed),
        "Q2_star_closed": "(17*sqrt(17)-55)/16",
        "inv_Q2_star": S(inv_closed),
        "inv_Q2_star_closed": "(55+17*sqrt(17))/118",
        "Q2_star_gt_fmin": bool(Qstar_closed > FMIN),
        "inv_Q2_star_lt_1.1185": bool(inv_closed < mpf("1.1185")),
        "is_global_lower_bound": False,
        "reason_not_global": (
            "3-atomic radial trials already sit near 0.931 < Q2*. "
            "The two-atom floor is a bound only inside the 2-atomic class."
        ),
        "Q2_at_t0": S(Q_at_t0),
        "Q2_at_t0_identity": "(3-t0)/(1+t0)^2",
        "fmin": S(FMIN),
        "grid_min_Q2": S(grid_min),
    }


# ---------------------------------------------------------------------------
# B2) geometric t0-chain, closed double sum
# ---------------------------------------------------------------------------


def chain_Q_equal_m(n, ratio):
    """Equal m-mass geometric chain r_k = ratio^{-k}, k=0..n-1.

    Closed form: with u = ratio^{-2},
      D = (1/n) (u^n−1)/(u−1)
      I = (1/n²) Σ_d f(ratio^{|d|}) · ((1+u^d)/2) · (u^{n−|d|}−1)/(u−1)
    (the d and −d terms are both included by summing d=-(n-1)..n-1).
    """
    n = int(n)
    q = mpf(ratio)
    u = q ** (-2)
    um1 = u - 1
    D = ((u**n - 1) / um1) / n
    acc = mpf(0)
    for d in range(-(n - 1), n):
        ad = abs(d)
        fd = f_of(q**ad)
        inner = ((1 + u**d) / 2) * (u ** (n - ad) - 1) / um1
        acc += fd * inner
    I = acc / (n * n)
    return I / D


def chain_Q_equal_z(n, ratio):
    """Equal D-mass geometric chain: m_k ∝ r_k^{-2}."""
    n = int(n)
    q = mpf(ratio)
    radii = [q ** (-k) for k in range(n)]
    masses = [1 / r**2 for r in radii]
    z = sum(masses)
    masses = [m / z for m in masses]
    D = sum(m * r**2 for m, r in zip(masses, radii))
    I = mpf(0)
    for i, ri in enumerate(radii):
        for j, rj in enumerate(radii):
            t = ri / rj if ri <= rj else rj / ri
            I += masses[i] * masses[j] * f_of(t) * (ri**2 + rj**2) / 2
    return I / D


def t0_chains() -> dict:
    rows = []
    best = mpf(2)
    best_n = None
    for n in range(1, 25):
        Qm = chain_Q_equal_m(n, T0)
        # equal-z is the inversion of equal-m on a geometric set
        Qz = chain_Q_equal_z(n, T0) if n <= 12 else Qm
        rows.append(
            {
                "n": n,
                "equal_m_Q": S(Qm, 18),
                "equal_z_Q": S(Qz, 18) if n <= 12 else None,
                "inv": S(1 / Qm, 18),
            }
        )
        if Qm < best:
            best, best_n = Qm, n
    # n=3 closed expression in u = t0^{-2}, f1 = fmin, f2 = f(t0²)
    u = T0 ** (-2)
    f1 = FMIN
    f2 = f_of(T0**2)
    Q3 = (
        (1 + u + u**2 + f1 * (1 + u) ** 2 + f2 * (1 + u**2)) / 9
    ) / ((1 + u + u**2) / 3)
    Q3_direct = chain_Q_equal_m(3, T0)
    if abs(Q3 - Q3_direct) > mpf("1e-50"):
        raise SystemExit("n=3 chain closed form mismatch")
    # Limit: Q_n = 1 − O(1/n) → 1 (mass 1/n kills the fmin deficit).
    Q24 = chain_Q_equal_m(24, T0)
    if Q24 < mpf("0.98"):
        raise SystemExit("expected Q_24 to have climbed toward 1")
    if best_n != 3:
        raise SystemExit(f"t0-chain min not at n=3 (got n={best_n})")
    return {
        "ratio": "t0",
        "t0": S(T0),
        "min_n": 3,
        "min_Q": S(best),
        "Q3_closed": (
            "(1/3) [1 + fmin (1+u)^2/(1+u+u^2) + f(t0^2) (1+u^2)/(1+u+u^2)] "
            "with u=t0^{-2}"
        ),
        "Q3_value": S(Q3),
        "Q24": S(Q24),
        "limit_n_to_inf": "1",
        "limit_reason": (
            "equal m-mass 1/n: Q = 1 − (1/n) Δ / Σ u^k with Δ = O(u^n) "
            "and Σ u^k = O(u^n), so the fmin deficit is O(1/n)."
        ),
        "is_lower_bound": False,
        "is_trial_upper_bound_on_beta": True,
        "beats_power_law_0.921": False,
        "rows_n_1_to_12": rows[:12],
    }


# ---------------------------------------------------------------------------
# B3) 1D convolution on log-radius
# ---------------------------------------------------------------------------


def unweighted_two_bump():
    """∬ f(e^{-|x-y|}) ρρ for ρ = (δ_0+δ_{h0})/2, h0 = −log t0."""
    return (1 + FMIN) / 2


def unweighted_three_bump():
    """Equal weights at 0, h0, 2h0."""
    f2 = f_of(T0**2)
    return (3 + 4 * FMIN + 2 * f2) / 9


def toeplitz_symbol_at_pi(n, delta):
    """τ_n(π) = 1 + 2 Σ_{k=1}^{n-1} (1−k/n) f(e^{−k δ}) (−1)^k.

    Signed (no positivity). Can sit below fmin.
    """
    acc = mpf(1)
    for k in range(1, n):
        acc += 2 * (1 - mpf(k) / n) * f_of(power(mp.e, -k * delta)) * ((-1) ** k)
    return acc


def log_gaussian_Q(sigma, n=16):
    """Trial: ρ(x) ∝ exp(−x²/(2σ²)) on a 16-point log-grid, x∈[−3σ,3σ].

    n≤16. This is a search, not a bound. Returns Q = I/D.
    """
    n = int(n)
    if n > 16:
        raise SystemExit("n>16 is forbidden here")
    sigma = mpf(sigma)
    xs = [(-3 + 6 * i / (n - 1)) * sigma for i in range(n)]
    # probability weights ∝ exp(−x²/(2σ²)) Δx
    ws = [mp.e ** (-(x**2) / (2 * sigma**2)) for x in xs]
    z = sum(ws)
    ws = [w / z for w in ws]
    rs = [mp.e**x for x in xs]
    D = sum(w * r**2 for w, r in zip(ws, rs))
    I = mpf(0)
    for i, (wi, ri) in enumerate(zip(ws, rs)):
        for j, (wj, rj) in enumerate(zip(ws, rs)):
            t = ri / rj if ri <= rj else rj / ri
            I += wi * wj * f_of(t) * (ri**2 + rj**2) / 2
    return I / D


def log_uniform_m_Q(L, n=16):
    """Trial: uniform in log-radius on [0, L] (m(dr) ∝ dr/r). n≤16."""
    n = int(n)
    if n > 16:
        raise SystemExit("n>16 is forbidden here")
    L = mpf(L)
    if L <= 0:
        return mpf(1)
    xs = [L * i / (n - 1) for i in range(n)]
    ws = [mpf(1) / n] * n
    rs = [mp.e**x for x in xs]
    D = sum(w * r**2 for w, r in zip(ws, rs))
    I = mpf(0)
    for i, (wi, ri) in enumerate(zip(ws, rs)):
        for j, (wj, rj) in enumerate(zip(ws, rs)):
            t = ri / rj if ri <= rj else rj / ri
            I += wi * wj * f_of(t) * (ri**2 + rj**2) / 2
    return I / D


def convolution_block() -> dict:
    two = unweighted_two_bump()
    three = unweighted_three_bump()
    # Signed symbol on a t0-step grid, n=16
    h0 = -mp.log(T0)
    tau_pi = toeplitz_symbol_at_pi(16, h0)
    # A few log-Gaussians (n=16)
    gaussians = []
    best_g = mpf(2)
    for sig in (mpf("0.25"), mpf("0.4"), mpf("0.55"), mpf("0.7"), mpf("1.0"), mpf("1.4")):
        Q = log_gaussian_Q(sig, n=16)
        gaussians.append({"sigma": S(sig, 12), "Q": S(Q, 18), "inv": S(1 / Q, 18)})
        if Q < best_g:
            best_g = Q
    uniforms = []
    for L in (mp.log(mpf("2")), mp.log(mpf("3.5")), mp.log(mpf("6")), mp.log(mpf("12"))):
        Q = log_uniform_m_Q(L, n=16)
        uniforms.append(
            {
                "aspect": S(mp.e**L, 12),
                "Q": S(Q, 18),
                "inv": S(1 / Q, 18),
            }
        )
    if two <= FMIN or three <= FMIN:
        raise SystemExit("unweighted bump energy sat at or below fmin")
    if best_g <= FMIN:
        raise SystemExit("log-Gaussian trial sat at or below fmin")
    return {
        "kernel": "f(e^{-|h|}) with f=(1+t^3)/(1+t^2)",
        "pointwise_floor": S(FMIN),
        "pointwise_floor_is_fmin": True,
        "unweighted_two_bump": S(two),
        "unweighted_two_bump_closed": "(1+fmin)/2",
        "unweighted_three_bump": S(three),
        "signed_symbol_n16_t0step_at_pi": S(tau_pi),
        "signed_symbol_below_fmin": bool(tau_pi < FMIN),
        "log_gaussian_n16": gaussians,
        "log_gaussian_best_Q": S(best_g),
        "log_uniform_m_n16": uniforms,
        "recovers_only_fmin_as_global_floor": True,
        "any_trial_beats_1.1185_as_lower_bound": False,
        "note": (
            "K(h)=f(e^{-|h|}) ≥ fmin, with equality at |h|=−log t0. "
            "Any average of K is therefore ≥ fmin, which is Proposition 4.5. "
            "The signed Toeplitz symbol at θ=π is below fmin, so dropping "
            "positivity loses the floor. Positive trials (log-Gaussian, "
            "log-uniform, t0-chain) stay above the HPS power-law 0.921 "
            "or sit with it; none is a global lower bound above fmin."
        ),
    }


# ---------------------------------------------------------------------------


def main() -> None:
    sgt = confirm_s_gt_3()
    two = two_atom_exact()
    chains = t0_chains()
    conv = convolution_block()

    global_gamma_above_fmin = False
    blob = {
        "status": "residue",
        "is_new_bound": False,
        "beats_1.1185_in_HPS_theorem": False,
        "compact_class_1.1087_claimed_unrestricted": False,
        "arxiv": "2504.18487v1",
        "urls_opened": [
            "https://arxiv.org/abs/2504.18487",
            "https://arxiv.org/html/2504.18487v1",
        ],
        "fmin": S(FMIN),
        "b3": S(B3),
        "t0": S(T0),
        "s_gt_3": sgt,
        "two_atom": two,
        "t0_chain": chains,
        "log_radius_convolution": conv,
        "verdict": {
            "global_gamma_gt_fmin": global_gamma_above_fmin,
            "two_atom_is_global": False,
            "t0_chain_is_global": False,
            "convolution_beats_fmin_globally": False,
            "reason": (
                "Q is an average of f, so Q≥fmin for every radial "
                "probability (HPS Prop. 4.5). The two-atom min, the "
                "t0-chain, and the log-radius convolution do not raise "
                "that floor for every measure. The compact-aspect number "
                "0.901924 (leading 1.1087) is not used and is not "
                "unrestricted. b(4) is not available for Theorem 2.2."
            ),
        },
    }
    out = HERE / "toeplitz_probe.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")

    print("=== A) s>3 ===")
    print("  Q4 =", sgt["Q4_exact"], "=", sgt["Q4_value"][:20])
    print("  Q35 < 0:", sgt["Q35_negative"], " b(4)=", sgt["b4"][:14])
    print("  path to Theorem 2.2:", sgt["certified_path_to_b4_in_Theorem_2_2"])
    print("=== B) two-atom ===")
    print("  Q2* =", two["Q2_star_closed"], "=", two["Q2_star"][:18])
    print("  1/Q2* =", two["inv_Q2_star"][:14], "  global?", two["is_global_lower_bound"])
    print("=== B) t0-chain ===")
    print("  min at n=3  Q=", chains["min_Q"][:18], "  Q24=", chains["Q24"][:14], "  →", chains["limit_n_to_inf"])
    print("=== B) convolution ===")
    print("  two-bump", conv["unweighted_two_bump"][:14], "  3-bump", conv["unweighted_three_bump"][:14])
    print("  signed τ(π)", conv["signed_symbol_n16_t0step_at_pi"][:14], "below fmin?", conv["signed_symbol_below_fmin"])
    print("  best log-Gaussian Q", conv["log_gaussian_best_Q"][:14])
    print("=== verdict ===")
    print("  global γ > fmin?", global_gamma_above_fmin)
    print("  status: residue")
    print("wrote", out)


if __name__ == "__main__":
    main()
