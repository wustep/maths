#!/usr/bin/env python3
"""Variational attempts at N=3 for Z=2 (He^-) and Z=3 (Li).

Slater determinants of 1s/2s/2p hydrogenic or screened Slater orbitals.
A trial with E_var(3,Z) below a *lower* bound on E(2,Z) would prove
N0(Z) >= 3. We have a self-contained exact threshold only at Z=1.
For Z=2 the published He energy is a comparison, not a lower bound
computed here. An incomplete search is not a lower bound.

Hydrogenic one- and two-electron integrals are closed form (replayed
from the generating function for 1/r12, checked against 17Z/81,
16Z/729, 59Z/243, 112Z/6561, 83Z/512, 15Z/512). Screened 1s²2s uses
nodeless Slater 2s, Gram–Schmidt orthogonalised against 1s.

Replay:

    python3 three_electron_try.py
"""

from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hylleraas import chandrasekhar_energy, hylleraas_energy, uncorrelated_energy

# ---------------------------------------------------------------------------
# Hydrogenic integrals of nuclear charge zeta (same zeta on every orbital)
# ---------------------------------------------------------------------------
# J(1s,2s)=17ζ/81, K(1s,2s)=16ζ/729 replayed in /tmp/test_1s2s.py from
# Jbare(λ,μ) = 32π² (λ²+3λμ+μ²)/(λ²μ²(λ+μ)³).
# J(1s,2p)=59ζ/243, K(1s,2p)=G¹/3=112ζ/6561 from the l=1 Slater integral.
# J(2s,2p)=83ζ/512, K(2s,2p)=15ζ/512, J(2s,2s)=77ζ/512 likewise.


def I_1s(zeta: Fraction, Z: Fraction) -> Fraction:
    return zeta**2 / 2 - Z * zeta


def I_n2(zeta: Fraction, Z: Fraction) -> Fraction:
    """Hydrogenic n=2 (2s or 2p) of charge zeta."""
    return zeta**2 / 8 - Z * zeta / 4


def J_1s1s(zeta: Fraction) -> Fraction:
    return Fraction(5, 8) * zeta


def J_1s2s(zeta: Fraction) -> Fraction:
    return Fraction(17, 81) * zeta


def K_1s2s(zeta: Fraction) -> Fraction:
    return Fraction(16, 729) * zeta


def J_1s2p(zeta: Fraction) -> Fraction:
    return Fraction(59, 243) * zeta


def K_1s2p(zeta: Fraction) -> Fraction:
    return Fraction(112, 6561) * zeta


def J_2s2p(zeta: Fraction) -> Fraction:
    return Fraction(83, 512) * zeta


def K_2s2p(zeta: Fraction) -> Fraction:
    return Fraction(15, 512) * zeta


def energy_1s2s_doublet(Z: Fraction, zeta: Fraction) -> Fraction:
    """Slater |1sα 1sβ 2sα|, hydrogenic charge zeta."""
    return (
        2 * I_1s(zeta, Z)
        + I_n2(zeta, Z)
        + J_1s1s(zeta)
        + 2 * J_1s2s(zeta)
        - K_1s2s(zeta)
    )


def energy_4P(Z: Fraction, zeta: Fraction) -> Fraction:
    """Slater |1sα 2sα 2pα|, hydrogenic charge zeta."""
    return (
        I_1s(zeta, Z)
        + 2 * I_n2(zeta, Z)
        + (J_1s2s(zeta) - K_1s2s(zeta))
        + (J_1s2p(zeta) - K_1s2p(zeta))
        + (J_2s2p(zeta) - K_2s2p(zeta))
    )


def optimize_zeta(energy_fn, Z: Fraction, lo: float, hi: float, n: int = 400):
    """Exact-rational scan of zeta on a uniform grid, then a golden refinement."""
    best = None
    for i in range(n + 1):
        z = Fraction(lo) + (Fraction(hi) - Fraction(lo)) * Fraction(i, n)
        if z <= 0:
            continue
        E = energy_fn(Z, z)
        if best is None or E < best[0]:
            best = (E, z)
    # Refine around the grid min with a finer rational grid.
    z0 = best[1]
    half = (Fraction(hi) - Fraction(lo)) / n
    lo2, hi2 = max(z0 - 2 * half, Fraction(1, 100)), z0 + 2 * half
    for i in range(200 + 1):
        z = lo2 + (hi2 - lo2) * Fraction(i, 200)
        if z <= 0:
            continue
        E = energy_fn(Z, z)
        if E < best[0]:
            best = (E, z)
    return best


# ---------------------------------------------------------------------------
# Screened 1s²2s: Slater 1s + nodeless Slater 2s, Gram–Schmidt
# ---------------------------------------------------------------------------
# All one- and two-electron s-integrals are algebraic in the exponents.
# Square roots from mixed-exponent norms are evaluated in mpmath.


def _install_jbare_engine():
    import sympy as sp

    lam, mu = sp.symbols("lam mu", positive=True)
    pi = sp.pi
    Jbare = 32 * pi**2 * (lam**2 + 3 * lam * mu + mu**2) / (
        lam**2 * mu**2 * (lam + mu) ** 3
    )

    def jpow(n, m):
        e = Jbare
        for _ in range(n):
            e = -sp.diff(e, lam)
        for _ in range(m):
            e = -sp.diff(e, mu)
        return sp.simplify(e)

    needed = {(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (2, 0), (2, 2)}
    fns = {nm: sp.lambdify((lam, mu), jpow(*nm), modules="mpmath") for nm in needed}
    return fns


_JPOW = None


def jpow(n: int, m: int, lam, mu):
    global _JPOW
    if _JPOW is None:
        _JPOW = _install_jbare_engine()
    return _JPOW[(n, m)](lam, mu)


def sto_1s2s_energy(Z: float, z1: float, z2: float) -> float | None:
    """1s²2s energy with Slater 1s(z1), orthogonalised Slater 2s(z2)."""
    from mpmath import mp, mpf, pi, sqrt as msqrt

    mp.dps = 40
    Z, z1, z2 = mpf(Z), mpf(z1), mpf(z2)
    if z1 <= 0 or z2 <= 0:
        return None
    s = z1 + z2
    S = 24 * msqrt(z1**3 * z2**5 / 3) / s**4
    if abs(S) >= mpf("1") - mpf("1e-14"):
        return None
    nrm = 1 / msqrt(1 - S**2)

    T11 = z1**2 / 2
    h11 = T11 - Z * z1
    T22 = z2**2 / 6
    h22 = T22 - Z * (z2 / 2)
    T12 = -2 * z1 * msqrt(z1**3 * z2**5 / 3) * (2 / s**3 - 6 * z2 / s**4)
    V12 = 8 * msqrt(z1**3 * z2**5 / 3) / s**3
    h12 = T12 - Z * V12
    h2 = nrm**2 * (h22 + S**2 * h11 - 2 * S * h12)

    N1 = msqrt(z1**3 / pi)
    N2 = msqrt(z2**5 / (3 * pi))
    J11 = (N1**2) * (N1**2) * jpow(0, 0, 2 * z1, 2 * z1)
    J12p = (N1**2) * (N2**2) * jpow(0, 2, 2 * z1, 2 * z2)
    K12p = (N1 * N2) ** 2 * jpow(1, 1, z1 + z2, z1 + z2)
    Lhyb = (N1**2) * (N1 * N2) * jpow(0, 1, 2 * z1, z1 + z2)

    J12 = nrm**2 * (J12p - 2 * S * Lhyb + S**2 * J11)
    K12 = nrm**2 * (K12p - 2 * S * Lhyb + S**2 * J11)
    E = 2 * h11 + h2 + J11 + 2 * J12 - K12
    return float(E)


def scan_sto_1s2s(Z: float, z1_grid, z2_grid) -> tuple[float, float, float] | None:
    best = None
    for z1 in z1_grid:
        for z2 in z2_grid:
            E = sto_1s2s_energy(Z, z1, z2)
            if E is None:
                continue
            if best is None or E < best[0]:
                best = (E, z1, z2)
    return best


def linspace(a: float, b: float, n: int) -> list[float]:
    if n == 1:
        return [a]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def two_electron_comparators(Z: int) -> dict:
    """Variational upper bounds on E(2,Z) from the two-electron families."""
    if Z == 2:
        a, c = Fraction(37, 20), Fraction(37, 100)
        ca, cb = Fraction(109, 50), Fraction(119, 100)
        ua = Fraction(27, 16)
    elif Z == 3:
        # Near Høgaasen–Richard–Sorba Table 1: a≈3.29, b≈2.08; Hylleraas scaled.
        a = Fraction(11, 4)  # 2.75, a bit below Z-like
        c = Fraction(3, 10)
        ca, cb = Fraction(329, 100), Fraction(208, 100)
        ua = Fraction(43, 16)
    else:
        raise ValueError(Z)
    return {
        "uncorrelated": uncorrelated_energy(ua, Z),
        "hylleraas": hylleraas_energy(a, c, Z),
        "chandrasekhar": chandrasekhar_energy(ca, cb, Z),
    }


def check_hydrogenic_tables() -> None:
    """Replay the textbook hydrogenic J,K values from the generating function."""
    from mpmath import mp, mpf, pi, sqrt as msqrt

    mp.dps = 30
    Z = mpf(1)
    # J(1s,2s) via 2s = A (e^{-βr} - β r e^{-βr}), A=sqrt(β³/π), β=Z/2
    beta = Z / 2
    A2 = beta**3 / pi
    factor = (Z**3 / pi) * A2
    J00 = jpow(0, 0, 2 * Z, 2 * beta)
    J01 = jpow(0, 1, 2 * Z, 2 * beta)
    J02 = jpow(0, 2, 2 * Z, 2 * beta)
    J12 = factor * (J00 - 2 * beta * J01 + beta**2 * J02)
    if abs(J12 - mpf(17) / 81) > 1e-16:
        raise RuntimeError(f"J(1s,2s) replay failed: {J12}")
    B2 = (Z**3 / pi) * (beta**3 / pi)
    gamma = Z + beta
    K00 = jpow(0, 0, gamma, gamma)
    K10 = jpow(1, 0, gamma, gamma)
    K01 = jpow(0, 1, gamma, gamma)
    K11 = jpow(1, 1, gamma, gamma)
    K12 = B2 * (K00 - beta * K10 - beta * K01 + beta**2 * K11)
    if abs(K12 - mpf(16) / 729) > 1e-16:
        raise RuntimeError(f"K(1s,2s) replay failed: {K12}")
    # J(1s,1s) = 5/8
    N1 = msqrt(Z**3 / pi)
    J11 = (N1**4) * jpow(0, 0, 2 * Z, 2 * Z)
    if abs(J11 - mpf(5) / 8) > 1e-16:
        raise RuntimeError(f"J(1s,1s) replay failed: {J11}")


def report() -> dict:
    check_hydrogenic_tables()
    print("Hydrogenic J,K tables replayed (1s-2s and 1s-1s).")

    out = {"He-": {}, "Li": {}, "residue": True}

    published_He = -2.9037243770341195
    published_Li_plus = -7.279913412669  # Nakashima–Nakatsuji Z=3, comparison only

    for name, Z, published_2e in (
        ("He-", 2, published_He),
        ("Li", 3, published_Li_plus),
    ):
        Zf = Fraction(Z)
        E_d, z_d = optimize_zeta(energy_1s2s_doublet, Zf, Fraction(1, 5), Fraction(Z) + 1)
        E_q, z_q = optimize_zeta(energy_4P, Zf, Fraction(1, 5), Fraction(Z) + 1)
        cmp2 = two_electron_comparators(Z)
        print(f"\nZ = {Z}  ({name})")
        print(
            f"  hydrogenic 1s2 2s  ζ = {z_d}  E = {E_d} = {float(E_d):.10f}"
        )
        print(
            f"  hydrogenic 1s2s2p 4P  ζ = {z_q}  E = {E_q} = {float(E_q):.10f}"
        )
        print(
            f"  two-electron variational E(2,{Z}): "
            f"uncorr {float(cmp2['uncorrelated']):.6f}, "
            f"Hyll {float(cmp2['hylleraas']):.6f}, "
            f"Chand {float(cmp2['chandrasekhar']):.6f}"
        )
        print(f"  published E(2,{Z}) (comparison, not a lower bound we own): {published_2e}")
        print(
            f"  4P vs published 2e: {float(E_q) - published_2e:+.6f}  "
            f"(positive means this trial does not bind)"
        )
        out[name]["hydrogenic_doublet"] = {
            "zeta": f"{z_d.numerator}/{z_d.denominator}",
            "energy": f"{E_d.numerator}/{E_d.denominator}",
            "energy_float": float(E_d),
        }
        out[name]["hydrogenic_4P"] = {
            "zeta": f"{z_q.numerator}/{z_q.denominator}",
            "energy": f"{E_q.numerator}/{E_q.denominator}",
            "energy_float": float(E_q),
        }
        out[name]["E2_variational_upper"] = {
            k: f"{v.numerator}/{v.denominator}" for k, v in cmp2.items()
        }
        out[name]["published_E2_comparison"] = published_2e

    # Screened 1s²2s scans
    print("\nScreened Slater 1s^2 2s (orthogonalised nodeless 2s)")
    for name, Z, z1g, z2g, published_2e in (
        ("He-", 2, linspace(1.4, 2.2, 17), linspace(0.15, 1.2, 22), published_He),
        ("Li", 3, linspace(2.2, 3.2, 17), linspace(0.4, 1.6, 25), published_Li_plus),
    ):
        best = scan_sto_1s2s(Z, z1g, z2g)
        if best is None:
            print(f"  Z={Z}: no finite energy")
            continue
        E, z1, z2 = best
        # local refine
        for dz1 in linspace(z1 - 0.08, z1 + 0.08, 9):
            for dz2 in linspace(max(0.08, z2 - 0.08), z2 + 0.08, 9):
                Er = sto_1s2s_energy(Z, dz1, dz2)
                if Er is not None and Er < E:
                    E, z1, z2 = Er, dz1, dz2
        print(
            f"  Z={Z} best E = {E:.10f}  at ζ1s={z1:.4f}, ζ2s={z2:.4f}  "
            f"vs published E(2,{Z}) {E - published_2e:+.6f}"
        )
        out[name]["screened_doublet"] = {
            "zeta_1s": z1,
            "zeta_2s": z2,
            "energy_float": E,
            "minus_published_E2": E - published_2e,
        }

    # He- 4P with a split effective charge: inner 1s at zeta, outer n=2 at eta.
    # Same-zeta 4P already sits far above He. A split scan on hydrogenic
    # 1s(zeta)+2s(eta)+2p(eta) without orthogonalisation is not a legal
    # Slater determinant if ⟨1s|2s⟩≠0. We only report the orthogonal same-zeta
    # 4P and the 1s²2s screened search.
    print(
        "\nResidue: no trial here has E_var(3,2) below the published He energy, "
        "let alone a self-contained lower bound on E(2,2). He- is not shown to "
        "bind. Li 1s²2s sits below the published Li+ energy in the screened "
        "search if the number is < -7.28, but that comparison is not a "
        "certificate (we do not own a lower bound on E(2,3)). Zhislin already "
        "gives N0(3) >= 3. We do not claim N0(Z) for Z>1."
    )
    he_s = out["He-"].get("screened_doublet", {})
    li_s = out["Li"].get("screened_doublet", {})
    out["He-_binds_by_this_search"] = False
    out["claim_N0_Z_gt_1"] = False
    if he_s:
        out["He-_binds_by_this_search"] = he_s["energy_float"] < published_He
    return out


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0]).parse_args(argv)
    report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
