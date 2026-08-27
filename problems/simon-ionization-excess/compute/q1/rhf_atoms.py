#!/usr/bin/env python3
"""Heuristic Hartree–Fock energies E(N, Z) for small atoms.

Every number this program prints or writes is HEURISTIC. It is not a
bound on N0(Z). Solovej already proved the ionization conjecture in
Hartree–Fock (arXiv:math-ph/0012026). An incomplete variational search
is not a lower bound. Experimental ionization energies are leads, not
certificates.

A variational N-electron energy is a binding certificate only if it
lies strictly below a certified value of E(N-1, Z). The only exact
thresholds used here are E(0, Z) = 0 and the hydrogenic
E(1, Z) = -Z^2 / 2. Comparing two HF energies to each other does not
prove binding.

Methods
-------
1. One-parameter Slater 1s Hartree–Fock for helium-like ions (N = 1, 2).
   Closed form: E(1) = -Z^2/2, E(2) = -(Z - 5/16)^2.
2. Unrestricted HF (UHF) in a small same-center even-tempered Gaussian
   basis with 1s / 2s / 2p scales. Closed shells stay spin-restricted
   if the guess is. Analytic one- and two-electron integrals (s and
   Cartesian p).
3. The same UHF loop on s-Gaussians only, for N = 0, 1, 2, as a
   spherical check that never uses p integrals.

Units are Hartree. Replay:

    python3 rhf_atoms.py
    python3 rhf_atoms.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
import os
from functools import lru_cache
from typing import Iterable

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_DIR = os.path.join(HERE, "certs")

LABEL = "HEURISTIC"
HARTREE = "Hartree"

# STO-3G primitive exponents and contraction coefficients at zeta = 1.
# Hehre, Stewart, Pople, J. Chem. Phys. 51, 2657 (1969); standard
# tabulation (normalized primitives). Exponents scale as zeta^2.
_STO3G_1S_Z1 = (
    (3.42525091, 0.15432897),
    (0.62391373, 0.53532814),
    (0.16885540, 0.44463454),
)
_STO3G_2SP_Z1 = (
    # (exponent, s-coeff, p-coeff)
    (2.94124940, -0.09996723, 0.15591627),
    (0.68348310, 0.39951283, 0.60768372),
    (0.22228992, 0.70011547, 0.39195739),
)

# Standard STO-3G Slater exponents (Pople).
STO3G_ZETA = {
    1: (1.24, None),
    2: (2.0925, None),
    3: (2.69, 0.80),
    4: (3.68, 1.15),
    5: (4.68, 1.50),
    6: (5.67, 1.72),
    7: (6.67, 1.95),
    8: (7.66, 2.25),
    9: (8.65, 2.55),
    10: (9.64, 2.88),
}

# Literature HF limits (Clementi / standard tables). Leads only.
HF_LIMIT_NEUTRAL = {
    1: -0.5,
    2: -2.861679995,
    3: -7.432726931,
    4: -14.57302317,
    5: -24.52906073,
    6: -37.68861896,
    7: -54.40093421,
    8: -74.80939847,
    9: -99.40934939,
    10: -128.5470981,
}


# ---------------------------------------------------------------------------
# Cartesian Gaussian primitives, all on the origin
# ---------------------------------------------------------------------------


def prim_norm(alpha: float, lx: int, ly: int, lz: int) -> float:
    """Normalization of x^lx y^ly z^lz exp(-alpha r^2)."""
    l = lx + ly + lz
    df = _odd_dfac(lx) * _odd_dfac(ly) * _odd_dfac(lz)
    return (2.0 * alpha / math.pi) ** 0.75 * ((4.0 * alpha) ** (0.5 * l)) / math.sqrt(df)


def _odd_dfac(n: int) -> int:
    """(2k-1)!! for n = 2k or 2k+1; empty product is 1.

    For Cartesian normalization one wants (2*lx-1)!! with lx the power.
    _odd_dfac(lx) = (2*lx-1)!! if we interpret ( -1)!! = 1.
    """
    if n <= 0:
        return 1
    # (2*n - 1)!! = 1*3*...*(2n-1)
    out = 1
    k = 1
    while k <= 2 * n - 1:
        out *= k
        k += 2
    return out


def _gauss1d(n: int, gamma: float) -> float:
    """int_{-inf}^{inf} x^n exp(-gamma x^2) dx."""
    if n < 0 or n % 2 == 1:
        return 0.0
    a = n // 2
    return _odd_dfac(a) / (2.0**a) * math.sqrt(math.pi) * gamma ** (-(a + 0.5))


def overlap_prim(
    a: float, la: tuple[int, int, int], b: float, lb: tuple[int, int, int]
) -> float:
    gamma = a + b
    return (
        _gauss1d(la[0] + lb[0], gamma)
        * _gauss1d(la[1] + lb[1], gamma)
        * _gauss1d(la[2] + lb[2], gamma)
    )


def _deriv(alpha: float, l: tuple[int, int, int], axis: int) -> list[tuple[float, tuple[int, int, int]]]:
    """Cartesian derivative of x^l exp(-alpha r^2) along axis."""
    out: list[tuple[float, tuple[int, int, int]]] = []
    li = l[axis]
    if li > 0:
        lp = list(l)
        lp[axis] = li - 1
        out.append((float(li), tuple(lp)))
    lp = list(l)
    lp[axis] = li + 1
    out.append((-2.0 * alpha, tuple(lp)))
    return out


def kinetic_prim(
    a: float, la: tuple[int, int, int], b: float, lb: tuple[int, int, int]
) -> float:
    """<a| -1/2 ∇^2 |b> = 1/2 sum_i <∂i a | ∂i b>."""
    tot = 0.0
    for axis in range(3):
        for ca, la2 in _deriv(a, la, axis):
            for cb, lb2 in _deriv(b, lb, axis):
                tot += ca * cb * overlap_prim(a, la2, b, lb2)
    return 0.5 * tot


def _nuclear_cart(lx: int, ly: int, lz: int, gamma: float) -> float:
    """int x^lx y^ly z^lz exp(-gamma r^2) / r d^3r, origin nucleus."""
    if lx % 2 or ly % 2 or lz % 2:
        return 0.0
    a, b, c = lx // 2, ly // 2, lz // 2
    n = a + b + c
    # angular = 4π (2a-1)!! (2b-1)!! (2c-1)!! / (2n+1)!!
    ang = 4.0 * math.pi * _odd_dfac(a) * _odd_dfac(b) * _odd_dfac(c)
    odd_end = 2 * n + 1
    den = 1
    k = 1
    while k <= odd_end:
        den *= k
        k += 2
    ang /= den
    # radial int_0^∞ r^{2n+1} exp(-γ r^2) dr = n! / (2 γ^{n+1})
    rad = math.factorial(n) / (2.0 * gamma ** (n + 1))
    return ang * rad


def nuclear_prim(
    z: float, a: float, la: tuple[int, int, int], b: float, lb: tuple[int, int, int]
) -> float:
    """<a| -Z/r |b>."""
    return -z * _nuclear_cart(
        la[0] + lb[0], la[1] + lb[1], la[2] + lb[2], a + b
    )


def eri_ssss(a: float, b: float, c: float, d: float, m: int = 0) -> float:
    """(ss|ss)^{(m)} for unnormalized s Gaussians at the origin."""
    g1 = a + b
    g2 = c + d
    pref = 2.0 * math.pi**2.5 / (g1 * g2 * math.sqrt(g1 + g2))
    return pref / (2 * m + 1)


@lru_cache(maxsize=None)
def eri_prim_m(
    ax: int,
    ay: int,
    az: int,
    alpha: float,
    bx: int,
    by: int,
    bz: int,
    beta: float,
    cx: int,
    cy: int,
    cz: int,
    gamma: float,
    dx: int,
    dy: int,
    dz: int,
    delta: float,
    m: int,
) -> float:
    """Obara–Saika (ab|cd)^{(m)} at a common centre."""
    if min(ax, ay, az, bx, by, bz, cx, cy, cz, dx, dy, dz, m) < 0:
        return 0.0
    if (
        ax
        == ay
        == az
        == bx
        == by
        == bz
        == cx
        == cy
        == cz
        == dx
        == dy
        == dz
        == 0
    ):
        return eri_ssss(alpha, beta, gamma, delta, m)

    g1 = alpha + beta
    g2 = gamma + delta
    rho = g1 * g2 / (g1 + g2)
    gsum = g1 + g2

    def rec(a2, b2, c2, d2, mm):
        return eri_prim_m(
            a2[0],
            a2[1],
            a2[2],
            alpha,
            b2[0],
            b2[1],
            b2[2],
            beta,
            c2[0],
            c2[1],
            c2[2],
            gamma,
            d2[0],
            d2[1],
            d2[2],
            delta,
            mm,
        )

    a = (ax, ay, az)
    b = (bx, by, bz)
    c = (cx, cy, cz)
    d = (dx, dy, dz)

    # Reduce the first nonzero Cartesian power (a, then b, then c, then d).
    for vec_idx, vec in enumerate((a, b, c, d)):
        for i in range(3):
            if vec[i] == 0:
                continue
            e = [0, 0, 0]
            e[i] = 1
            e = tuple(e)

            def sub(v, k=1):
                return (v[0] - k * e[0], v[1] - k * e[1], v[2] - k * e[2])

            if vec_idx == 0:
                # (a| = increment of (a - e_i|)
                ai = a[i] - 1
                val = 0.0
                if ai > 0:
                    val += (ai / (2.0 * g1)) * (
                        rec(sub(a, 2), b, c, d, m)
                        - (rho / g1) * rec(sub(a, 2), b, c, d, m + 1)
                    )
                if b[i] > 0:
                    val += (b[i] / (2.0 * g1)) * (
                        rec(sub(a), sub(b), c, d, m)
                        - (rho / g1) * rec(sub(a), sub(b), c, d, m + 1)
                    )
                if c[i] > 0:
                    val += (c[i] / (2.0 * gsum)) * rec(sub(a), b, sub(c), d, m + 1)
                if d[i] > 0:
                    val += (d[i] / (2.0 * gsum)) * rec(sub(a), b, c, sub(d), m + 1)
                return val
            if vec_idx == 1:
                bi = b[i] - 1
                val = 0.0
                if bi > 0:
                    val += (bi / (2.0 * g1)) * (
                        rec(a, sub(b, 2), c, d, m)
                        - (rho / g1) * rec(a, sub(b, 2), c, d, m + 1)
                    )
                if a[i] > 0:
                    val += (a[i] / (2.0 * g1)) * (
                        rec(sub(a), sub(b), c, d, m)
                        - (rho / g1) * rec(sub(a), sub(b), c, d, m + 1)
                    )
                if c[i] > 0:
                    val += (c[i] / (2.0 * gsum)) * rec(a, sub(b), sub(c), d, m + 1)
                if d[i] > 0:
                    val += (d[i] / (2.0 * gsum)) * rec(a, sub(b), c, sub(d), m + 1)
                return val
            if vec_idx == 2:
                # Increment on ket, same-centre OS (swap bra/ket).
                return eri_prim_m(
                    cx,
                    cy,
                    cz,
                    gamma,
                    dx,
                    dy,
                    dz,
                    delta,
                    ax,
                    ay,
                    az,
                    alpha,
                    bx,
                    by,
                    bz,
                    beta,
                    m,
                )
            # vec_idx == 3: swap as well
            return eri_prim_m(
                cx,
                cy,
                cz,
                gamma,
                dx,
                dy,
                dz,
                delta,
                ax,
                ay,
                az,
                alpha,
                bx,
                by,
                bz,
                beta,
                m,
            )
    raise RuntimeError("eri_prim_m: no angular momentum to reduce")


def eri_prim(
    a: float,
    la: tuple[int, int, int],
    b: float,
    lb: tuple[int, int, int],
    c: float,
    lc: tuple[int, int, int],
    d: float,
    ld: tuple[int, int, int],
) -> float:
    return eri_prim_m(
        la[0],
        la[1],
        la[2],
        a,
        lb[0],
        lb[1],
        lb[2],
        b,
        lc[0],
        lc[1],
        lc[2],
        c,
        ld[0],
        ld[1],
        ld[2],
        d,
        0,
    )


# ---------------------------------------------------------------------------
# Basis
# ---------------------------------------------------------------------------


class Prim:
    __slots__ = ("alpha", "l", "coeff")

    def __init__(self, alpha: float, l: tuple[int, int, int], coeff: float):
        self.alpha = float(alpha)
        self.l = l
        self.coeff = float(coeff)


class AO:
    """Contracted Cartesian GTO (possibly a single primitive)."""

    def __init__(self, prims: list[Prim], tag: str):
        self.prims = prims
        self.tag = tag


def _shell_1s(zeta: float, contracted: bool) -> list[AO]:
    prims = []
    for a1, d in _STO3G_1S_Z1:
        alpha = a1 * zeta * zeta
        n = prim_norm(alpha, 0, 0, 0)
        prims.append(Prim(alpha, (0, 0, 0), d * n))
    if contracted:
        return [AO(prims, "1s")]
    return [AO([p], f"1s:{p.alpha:.6g}") for p in prims]


def _shell_2sp(zeta: float, contracted: bool, with_p: bool) -> list[AO]:
    s_prims = []
    p_shells: dict[tuple[int, int, int], list[Prim]] = {
        (1, 0, 0): [],
        (0, 1, 0): [],
        (0, 0, 1): [],
    }
    for a1, ds, dp in _STO3G_2SP_Z1:
        alpha = a1 * zeta * zeta
        ns = prim_norm(alpha, 0, 0, 0)
        s_prims.append(Prim(alpha, (0, 0, 0), ds * ns))
        if with_p:
            for l in p_shells:
                np_ = prim_norm(alpha, *l)
                p_shells[l].append(Prim(alpha, l, dp * np_))
    aos: list[AO] = []
    if contracted:
        aos.append(AO(s_prims, "2s"))
        if with_p:
            aos.append(AO(p_shells[(1, 0, 0)], "2px"))
            aos.append(AO(p_shells[(0, 1, 0)], "2py"))
            aos.append(AO(p_shells[(0, 0, 1)], "2pz"))
        return aos
    for p in s_prims:
        aos.append(AO([p], f"2s:{p.alpha:.6g}"))
    if with_p:
        for l, tag in (((1, 0, 0), "2px"), ((0, 1, 0), "2py"), ((0, 0, 1), "2pz")):
            for p in p_shells[l]:
                aos.append(AO([p], f"{tag}:{p.alpha:.6g}"))
    return aos


def sto3g_basis(z: int, contracted: bool = False, with_p: bool = True) -> list[AO]:
    z1s, z2sp = STO3G_ZETA[z]
    aos = _shell_1s(z1s, contracted)
    if z2sp is not None:
        aos.extend(_shell_2sp(z2sp, contracted, with_p=with_p))
    return aos


def even_tempered_s(z: int, n_s: int = 8) -> list[AO]:
    """Z-scaled even-tempered s Gaussians. Spherical check, no p."""
    # Cover 1s (~Z^2) down toward a loose valence / anion tail.
    alphas = [(z**2) * 0.05 * (2.2**k) for k in range(n_s)]
    alphas += [0.04, 0.015]
    aos = []
    seen = set()
    for alpha in alphas:
        key = round(alpha, 10)
        if key in seen or alpha <= 0:
            continue
        seen.add(key)
        n = prim_norm(alpha, 0, 0, 0)
        aos.append(AO([Prim(alpha, (0, 0, 0), n)], f"s:{alpha:.6g}"))
    return aos


def even_tempered_sp(z: int, with_p: bool | None = None) -> list[AO]:
    """Hydrogenic-scaled even-tempered 1s / 2s / 2p Gaussians.

    Tight s exponents track Z^2, valence s/p track (Z/2)^2, plus a
    short diffuse tail so N = Z+1, Z+2 is representable. This is not a
    library STO-nG contraction; the angular content is 1s, 2s, 2p.
    """
    if with_p is None:
        with_p = z >= 3
    s_alphas = [z * z * x for x in (20.0, 6.0, 2.0, 0.7, 0.25)]
    s_alphas += [(max(z, 2) * 0.5) ** 2 * x for x in (1.8, 0.6, 0.2, 0.07)]
    s_alphas += [0.035, 0.012]
    aos: list[AO] = []
    seen: set[float] = set()
    for alpha in s_alphas:
        key = round(alpha, 10)
        if key in seen or alpha <= 1e-8:
            continue
        seen.add(key)
        n = prim_norm(alpha, 0, 0, 0)
        aos.append(AO([Prim(alpha, (0, 0, 0), n)], f"s:{alpha:.6g}"))
    if with_p:
        p_alphas = [(max(z, 3) * 0.5) ** 2 * x for x in (3.0, 1.0, 0.35, 0.12, 0.04)]
        p_alphas += [0.02]
        seen_p: set[float] = set()
        for alpha in p_alphas:
            key = round(alpha, 10)
            if key in seen_p or alpha <= 1e-8:
                continue
            seen_p.add(key)
            for ell, tag in (((1, 0, 0), "px"), ((0, 1, 0), "py"), ((0, 0, 1), "pz")):
                n = prim_norm(alpha, *ell)
                aos.append(AO([Prim(alpha, ell, n)], f"{tag}:{alpha:.6g}"))
    return aos


# ---------------------------------------------------------------------------
# Integrals over contracted AOs
# ---------------------------------------------------------------------------


def ao_overlap(mu: AO, nu: AO) -> float:
    s = 0.0
    for p in mu.prims:
        for q in nu.prims:
            s += p.coeff * q.coeff * overlap_prim(p.alpha, p.l, q.alpha, q.l)
    return s


def ao_kinetic(mu: AO, nu: AO) -> float:
    t = 0.0
    for p in mu.prims:
        for q in nu.prims:
            t += p.coeff * q.coeff * kinetic_prim(p.alpha, p.l, q.alpha, q.l)
    return t


def ao_nuclear(z: float, mu: AO, nu: AO) -> float:
    v = 0.0
    for p in mu.prims:
        for q in nu.prims:
            v += p.coeff * q.coeff * nuclear_prim(z, p.alpha, p.l, q.alpha, q.l)
    return v


def ao_eri(mu: AO, nu: AO, lam: AO, sig: AO) -> float:
    val = 0.0
    for p in mu.prims:
        for q in nu.prims:
            pq = p.coeff * q.coeff
            for r in lam.prims:
                for s in sig.prims:
                    val += (
                        pq
                        * r.coeff
                        * s.coeff
                        * eri_prim(
                            p.alpha, p.l, q.alpha, q.l, r.alpha, r.l, s.alpha, s.l
                        )
                    )
    return val


def one_electron(z: float, basis: list[AO]) -> tuple[np.ndarray, np.ndarray]:
    n = len(basis)
    s = np.zeros((n, n))
    h = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            sij = ao_overlap(basis[i], basis[j])
            hij = ao_kinetic(basis[i], basis[j]) + ao_nuclear(z, basis[i], basis[j])
            s[i, j] = s[j, i] = sij
            h[i, j] = h[j, i] = hij
    return s, h


def two_electron(basis: list[AO]) -> np.ndarray:
    n = len(basis)
    eri = np.zeros((n, n, n, n))
    for i in range(n):
        for j in range(i, n):
            for k in range(n):
                for ell in range(k, n):
                    # (ij|kl) with i<=j, k<=l; fill 8-fold if the pairs
                    # are unordered. Also swap the two pairs.
                    ij = i * n + j
                    kl = k * n + ell
                    if ij > kl and i != k:
                        # still compute; cheaper to just compute all
                        # unique pair-of-pairs with i<=j, k<=l.
                        pass
                    v = ao_eri(basis[i], basis[j], basis[k], basis[ell])
                    for ii, jj in ((i, j), (j, i)):
                        for kk, ll in ((k, ell), (ell, k)):
                            eri[ii, jj, kk, ll] = v
                            eri[kk, ll, ii, jj] = v
    return eri


# ---------------------------------------------------------------------------
# Occupations and SCF
# ---------------------------------------------------------------------------


def hund_ab(n_elec: int) -> tuple[int, int]:
    """High-spin Aufbau for N <= 12 (1s 2s 2p then next s)."""
    if n_elec < 0:
        raise ValueError("N < 0")
    # Fill 1s (2), 2s (2), 2p (6) with Hund's rule on the p shell,
    # then pair into the next spatial orbitals.
    n_a = 0
    n_b = 0
    remaining = n_elec
    # 1s
    take = min(2, remaining)
    n_a += min(1, take)
    n_b += max(0, take - 1)
    remaining -= take
    # 2s
    take = min(2, remaining)
    n_a += min(1, take)
    n_b += max(0, take - 1)
    remaining -= take
    # 2p: three spatial, high spin first
    # occupations of (px, py, pz) alpha then beta
    p_a = min(3, remaining)
    remaining -= p_a
    p_b = min(3, remaining)
    remaining -= p_b
    n_a += p_a
    n_b += p_b
    # leftover: pair into further MOs, high spin if odd
    n_a += (remaining + 1) // 2
    n_b += remaining // 2
    return n_a, n_b


def _canon_orth(s: np.ndarray, thresh: float = 1e-8) -> np.ndarray:
    ev, u = np.linalg.eigh(s)
    keep = ev > thresh
    if not np.any(keep):
        raise RuntimeError("overlap has no positive eigenvalues")
    return u[:, keep] / np.sqrt(ev[keep])


def _eigh_gen(fock: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    fp = x.T @ fock @ x
    # numerical symmetrize
    fp = 0.5 * (fp + fp.T)
    eps, cp = np.linalg.eigh(fp)
    return eps, x @ cp


def _density(c: np.ndarray, nocc: int) -> np.ndarray:
    if nocc <= 0:
        return np.zeros((c.shape[0], c.shape[0]))
    co = c[:, :nocc]
    return co @ co.T


def _diis_solve(focks: list[np.ndarray], errs: list[np.ndarray]) -> np.ndarray | None:
    n = len(focks)
    if n < 2:
        return None
    b = np.zeros((n + 1, n + 1))
    for i in range(n):
        ei = errs[i].ravel()
        for j in range(i, n):
            bij = float(ei @ errs[j].ravel())
            b[i, j] = b[j, i] = bij
        b[i, n] = b[n, i] = -1.0
    rhs = np.zeros(n + 1)
    rhs[n] = -1.0
    try:
        coef = np.linalg.solve(b, rhs)
    except np.linalg.LinAlgError:
        return None
    out = np.zeros_like(focks[0])
    for i in range(n):
        out += coef[i] * focks[i]
    return out


def uhf_energy(
    z: float,
    n_elec: int,
    s: np.ndarray,
    h: np.ndarray,
    eri: np.ndarray,
    max_iter: int = 80,
    conv: float = 1e-8,
    mix: float = 0.35,
) -> dict:
    """UHF SCF. Every field is HEURISTIC except the exact N=0,1 notes."""
    n_ao = h.shape[0]
    n_a, n_b = hund_ab(n_elec)
    if n_a > n_ao or n_b > n_ao:
        return {
            "label": LABEL,
            "ok": False,
            "reason": "basis too small for N, spin",
            "N": n_elec,
            "Z": z,
            "n_alpha": n_a,
            "n_beta": n_b,
            "n_ao": n_ao,
        }
    x = _canon_orth(s)
    # Core-Hamiltonian guess (same spatial orbitals for alpha/beta).
    eps, c = _eigh_gen(h, x)
    pa = _density(c, n_a)
    pb = _density(c, n_b)
    e_old = 0.0
    hist_f_a: list[np.ndarray] = []
    hist_e_a: list[np.ndarray] = []
    hist_f_b: list[np.ndarray] = []
    hist_e_b: list[np.ndarray] = []
    energy = 0.0
    converged = False
    niter = 0
    shift = 0.0
    for niter in range(1, max_iter + 1):
        pt = pa + pb
        j = np.einsum("ijkl,kl->ij", eri, pt, optimize=True)
        ka = np.einsum("ikjl,kl->ij", eri, pa, optimize=True)
        kb = np.einsum("ikjl,kl->ij", eri, pb, optimize=True)
        fa = h + j - ka
        fb = h + j - kb
        if shift > 0.0:
            # Level shift on virtuals in AO metric: F += shift (S - S P S)
            virt_a = s - s @ pa @ s
            virt_b = s - s @ pb @ s
            fa = fa + shift * virt_a
            fb = fb + shift * virt_b
        err_a = fa @ pa @ s - s @ pa @ fa
        err_b = fb @ pb @ s - s @ pb @ fb
        hist_f_a.append(fa.copy())
        hist_e_a.append(err_a.copy())
        hist_f_b.append(fb.copy())
        hist_e_b.append(err_b.copy())
        if len(hist_f_a) > 8:
            hist_f_a.pop(0)
            hist_e_a.pop(0)
            hist_f_b.pop(0)
            hist_e_b.pop(0)
        if niter > 3:
            fa_d = _diis_solve(hist_f_a, hist_e_a)
            fb_d = _diis_solve(hist_f_b, hist_e_b)
            if fa_d is not None:
                fa = fa_d
            if fb_d is not None:
                fb = fb_d
        eps_a, ca = _eigh_gen(fa, x)
        eps_b, cb = _eigh_gen(fb, x)
        pa_n = _density(ca, n_a)
        pb_n = _density(cb, n_b)
        # Damping early; DIIS takes over later.
        damp = mix if niter < 8 else 0.15
        pa = (1.0 - damp) * pa_n + damp * pa
        pb = (1.0 - damp) * pb_n + damp * pb
        pt = pa + pb
        # Energy from the damped densities and the last raw Fock-like
        # rebuild so the formula is consistent.
        j = np.einsum("ijkl,kl->ij", eri, pt, optimize=True)
        ka = np.einsum("ikjl,kl->ij", eri, pa, optimize=True)
        kb = np.einsum("ikjl,kl->ij", eri, pb, optimize=True)
        fa_e = h + j - ka
        fb_e = h + j - kb
        energy = 0.5 * (
            np.trace(pa @ (h + fa_e)) + np.trace(pb @ (h + fb_e))
        )
        rms = math.sqrt(
            0.5
            * (
                np.mean(np.asarray(err_a) ** 2)
                + np.mean(np.asarray(err_b) ** 2)
            )
        )
        if rms < conv and abs(energy - e_old) < conv:
            # Final undamped occupy
            pa = pa_n
            pb = pb_n
            pt = pa + pb
            j = np.einsum("ijkl,kl->ij", eri, pt, optimize=True)
            ka = np.einsum("ikjl,kl->ij", eri, pa, optimize=True)
            kb = np.einsum("ikjl,kl->ij", eri, pb, optimize=True)
            fa_e = h + j - ka
            fb_e = h + j - kb
            energy = 0.5 * (
                np.trace(pa @ (h + fa_e)) + np.trace(pb @ (h + fb_e))
            )
            eps_a, ca = _eigh_gen(fa_e, x)
            eps_b, cb = _eigh_gen(fb_e, x)
            converged = True
            break
        if niter > 20 and abs(energy - e_old) > 0.5:
            shift = min(2.0, shift + 0.25)
        e_old = energy

    homo_a = float(eps_a[n_a - 1]) if n_a > 0 else None
    homo_b = float(eps_b[n_b - 1]) if n_b > 0 else None
    return {
        "label": LABEL,
        "ok": True,
        "scf_converged": converged,
        "N": n_elec,
        "Z": z,
        "E": float(energy),
        "n_alpha": n_a,
        "n_beta": n_b,
        "n_ao": n_ao,
        "n_iter": niter,
        "eps_alpha": [float(x) for x in eps_a],
        "eps_beta": [float(x) for x in eps_b],
        "homo_alpha": homo_a,
        "homo_beta": homo_b,
        "units": HARTREE,
    }


# ---------------------------------------------------------------------------
# Helium-like closed form
# ---------------------------------------------------------------------------


def helium_like(z: int, n_elec: int) -> dict:
    """One-parameter 1s Slater HF. Exact for this restricted ansatz."""
    if n_elec == 0:
        e = 0.0
        note = "bare nucleus"
    elif n_elec == 1:
        e = -0.5 * z * z
        note = "hydrogenic 1s, exact for N=1"
    elif n_elec == 2:
        zeff = z - 5.0 / 16.0
        e = -(zeff**2)
        note = "1s^2 Slater, zeta = Z - 5/16; E = -(Z - 5/16)^2"
    else:
        return {
            "label": LABEL,
            "ok": False,
            "reason": "helium-like ansatz only for N=0,1,2",
            "N": n_elec,
            "Z": z,
        }
    e1 = -0.5 * z * z
    certified = None
    if n_elec == 1 and e < 0.0:
        certified = {
            "threshold": 0.0,
            "threshold_name": "E(0,Z)=0",
            "below": True,
            "implies": "N0(Z) >= 1 (trivial hydrogenic)",
        }
    elif n_elec == 2:
        below = e < e1
        certified = {
            "threshold": e1,
            "threshold_name": "E(1,Z)=-Z^2/2",
            "below": below,
            "implies": "N0(Z) >= 2" if below else "no certificate (trial energy not below E(1))",
        }
    return {
        "label": LABEL,
        "ok": True,
        "method": "helium-like 1-parameter Slater 1s",
        "N": n_elec,
        "Z": z,
        "E": float(e),
        "note": note,
        "certified_vs_exact_previous": certified,
        "units": HARTREE,
    }


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------


def n_range(z: int) -> list[int]:
    """N = 0 .. Z+2, so consecutive ΔE(N,Z) exists through the anion."""
    return list(range(0, z + 3))


def _certified_vs_exact(n_elec: int, z: int, energy: float) -> dict | None:
    if n_elec == 1:
        return {
            "threshold": 0.0,
            "threshold_name": "E(0,Z)=0",
            "below": energy < 0.0,
            "implies": "N0(Z) >= 1" if energy < 0.0 else "no certificate",
        }
    if n_elec == 2:
        e1 = -0.5 * z * z
        below = energy < e1
        return {
            "threshold": e1,
            "threshold_name": "E(1,Z)=-Z^2/2 (exact hydrogenic)",
            "below": below,
            "implies": "N0(Z) >= 2" if below else "no certificate (HF trial not below exact E(1))",
        }
    return None


def run_basis_scan(
    z_list: Iterable[int],
    basis_name: str,
    make_basis,
) -> list[dict]:
    rows = []
    cache: dict[int, tuple[list[AO], np.ndarray, np.ndarray, np.ndarray]] = {}
    for z in z_list:
        basis = make_basis(z)
        s, h = one_electron(float(z), basis)
        eri = two_electron(basis)
        cache[z] = (basis, s, h, eri)
        for n in n_range(z):
            if n == 0:
                row = {
                    "label": LABEL,
                    "ok": True,
                    "method": basis_name,
                    "N": 0,
                    "Z": z,
                    "E": 0.0,
                    "scf_converged": True,
                    "note": "bare nucleus, exact",
                    "units": HARTREE,
                    "n_ao": len(basis),
                }
                rows.append(row)
                continue
            rec = uhf_energy(float(z), n, s, h, eri)
            rec["method"] = basis_name
            rec["basis_tags"] = [ao.tag for ao in basis]
            if rec.get("ok"):
                rec["certified_vs_exact_previous"] = _certified_vs_exact(
                    n, z, rec["E"]
                )
            rows.append(rec)
    return rows


def attach_binding(rows: list[dict]) -> list[dict]:
    """Flag the heuristic E(N) < E(N-1) comparison. Not a proof."""
    by = {}
    for r in rows:
        if not r.get("ok"):
            continue
        by.setdefault(r["Z"], {})[r["N"]] = r
    for z, byn in by.items():
        ns = sorted(byn)
        for n in ns:
            if n == 0:
                byn[n]["heuristic_binds_vs_N-1"] = None
                continue
            prev = byn.get(n - 1)
            if prev is None or not prev.get("ok"):
                byn[n]["heuristic_binds_vs_N-1"] = None
                continue
            e = byn[n]["E"]
            ep = prev["E"]
            byn[n]["E_N-1"] = ep
            byn[n]["heuristic_binds_vs_N-1"] = bool(e < ep)
            byn[n]["heuristic_delta_E"] = ep - e
            byn[n]["binding_note"] = (
                "HEURISTIC comparison of two variational energies; "
                "does not prove E(N)<E(N-1) unless E(N-1) is certified."
            )
    return rows


def n0_hat(rows: list[dict]) -> dict:
    """Largest N with heuristic binding. Residue, not a lower bound."""
    out = {}
    by = {}
    for r in rows:
        if not r.get("ok") or "E" not in r:
            continue
        if r.get("scf_converged") is False:
            continue
        by.setdefault(int(r["Z"]), {})[int(r["N"])] = r
    for z, byn in by.items():
        best = 0
        n = 1
        while n in byn:
            if byn[n].get("heuristic_binds_vs_N-1") is True:
                best = n
                n += 1
                continue
            break
        out[str(z)] = {
            "N0_hat": best,
            "label": LABEL,
            "note": (
                "Largest N in this table with E_HF(N)<E_HF(N-1) along "
                "the consecutive chain from N=1. Residue, not a lower bound."
            ),
        }
    return out


# ---------------------------------------------------------------------------
# Self-tests (analytic identities, not literature HF limits)
# ---------------------------------------------------------------------------


def self_test() -> list[str]:
    """Return a list of failure strings; empty means pass."""
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append(f"{name}: {detail}")

    # Normalized s-GTO identities.
    alpha = 0.3
    n = prim_norm(alpha, 0, 0, 0)
    s = n * n * overlap_prim(alpha, (0, 0, 0), alpha, (0, 0, 0))
    t = n * n * kinetic_prim(alpha, (0, 0, 0), alpha, (0, 0, 0))
    v1 = n * n * nuclear_prim(1.0, alpha, (0, 0, 0), alpha, (0, 0, 0))
    j = (n**4) * eri_prim(
        alpha, (0, 0, 0), alpha, (0, 0, 0), alpha, (0, 0, 0), alpha, (0, 0, 0)
    )
    check("s-norm", abs(s - 1.0) < 1e-12, f"S={s}")
    check("s-kinetic", abs(t - 1.5 * alpha) < 1e-10, f"T={t} vs {1.5 * alpha}")
    # <1/r> = sqrt(8 alpha / pi); nuclear_prim is -<1/r> for Z=1
    expect_v = -math.sqrt(8.0 * alpha / math.pi)
    check("s-nuclear", abs(v1 - expect_v) < 1e-10, f"V={v1} vs {expect_v}")
    check("s-coulomb", abs(j - 2.0 * math.sqrt(alpha / math.pi)) < 1e-10, f"J={j}")

    # Single-GTO hydrogen variational minimum.
    # E = 3α/2 - Z sqrt(8α/π), α* = 8 Z^2 / (9π), E* = -4 Z^2 / (3π)
    z = 1.0
    a_star = 8.0 / (9.0 * math.pi)
    n = prim_norm(a_star, 0, 0, 0)
    e = n * n * (
        kinetic_prim(a_star, (0, 0, 0), a_star, (0, 0, 0))
        + nuclear_prim(z, a_star, (0, 0, 0), a_star, (0, 0, 0))
    )
    e_star = -4.0 / (3.0 * math.pi)
    check("H-GTO-min", abs(e - e_star) < 1e-10, f"E={e} vs {e_star}")

    # (px px | ss) OS vs the closed s-recurrence.
    a = 0.4
    g1 = 2.0 * a
    g2 = 2.0 * a
    rho = g1 * g2 / (g1 + g2)
    pref = eri_ssss(a, a, a, a, 0)
    expect = (1.0 / (2.0 * g1)) * pref * (1.0 - rho / (3.0 * g1))
    got = eri_prim(a, (1, 0, 0), a, (1, 0, 0), a, (0, 0, 0), a, (0, 0, 0))
    check("eri-pxpx-ss", abs(got - expect) < 1e-12, f"{got} vs {expect}")

    # p-overlap / kinetic sanity: normalized px, <T> = 2.5 α
    # Unnormalized px, S = 1/(4α) (π/(2α))^{3/2}; T_norm = 5α/2.
    npx = prim_norm(alpha, 1, 0, 0)
    sp = npx * npx * overlap_prim(alpha, (1, 0, 0), alpha, (1, 0, 0))
    tp = npx * npx * kinetic_prim(alpha, (1, 0, 0), alpha, (1, 0, 0))
    check("p-norm", abs(sp - 1.0) < 1e-12, f"S={sp}")
    check("p-kinetic", abs(tp - 2.5 * alpha) < 1e-9, f"T={tp} vs {2.5 * alpha}")

    # Helium-like numbers.
    h1 = helium_like(1, 1)
    h2 = helium_like(1, 2)
    check("He-like H", abs(h1["E"] + 0.5) < 1e-15, str(h1["E"]))
    check("He-like H-", abs(h2["E"] + (11.0 / 16.0) ** 2) < 1e-15, str(h2["E"]))
    check("H- not certified", h2["certified_vs_exact_previous"]["below"] is False, "")
    he2 = helium_like(2, 2)
    check("He certified", he2["certified_vs_exact_previous"]["below"] is True, "")

    # UHF on H / He in the even-tempered s basis: near the hydrogenic / HF values.
    basis = even_tempered_sp(1, with_p=False)
    s, h = one_electron(1.0, basis)
    eri = two_electron(basis)
    rec = uhf_energy(1.0, 1, s, h, eri)
    check("H-UHF-ok", rec.get("ok") and rec.get("scf_converged"), str(rec))
    if rec.get("ok"):
        check("H-UHF-range", -0.5 - 1e-8 <= rec["E"] <= -0.498, str(rec["E"]))

    basis = even_tempered_sp(2, with_p=False)
    s, h = one_electron(2.0, basis)
    eri = two_electron(basis)
    rec = uhf_energy(2.0, 2, s, h, eri)
    check("He-UHF-ok", rec.get("ok") and rec.get("scf_converged"), str(rec))
    if rec.get("ok"):
        # Cannot beat the HF limit -2.86168; a decent s basis sits just above.
        check(
            "He-UHF-range",
            -2.86168 - 1e-4 <= rec["E"] <= -2.85,
            str(rec["E"]),
        )

    # Hund occupations.
    check("hund-1", hund_ab(1) == (1, 0), str(hund_ab(1)))
    check("hund-2", hund_ab(2) == (1, 1), str(hund_ab(2)))
    check("hund-7", hund_ab(7) == (5, 2), str(hund_ab(7)))
    check("hund-10", hund_ab(10) == (5, 5), str(hund_ab(10)))

    # Li: the 3-electron UHF energy should sit below the 2-electron energy
    # in this basis (heuristic binding, not a certificate).
    basis = even_tempered_sp(3)
    s, h = one_electron(3.0, basis)
    eri = two_electron(basis)
    e2 = uhf_energy(3.0, 2, s, h, eri)
    e3 = uhf_energy(3.0, 3, s, h, eri)
    check("Li2-ok", e2.get("ok") and e2.get("scf_converged"), str(e2))
    check("Li3-ok", e3.get("ok") and e3.get("scf_converged"), str(e3))
    if e2.get("ok") and e3.get("ok"):
        check("Li-binds-heuristic", e3["E"] < e2["E"], f"{e3['E']} vs {e2['E']}")
    return fails


def build_table(z_max: int = 10) -> dict:
    z_list = list(range(1, z_max + 1))
    he_rows = []
    for z in z_list:
        for n in (0, 1, 2):
            he_rows.append(helium_like(z, n))
    attach_binding(he_rows)

    uhf_rows = run_basis_scan(
        z_list,
        "UHF even-tempered Gaussian 1s/2s/2p, analytic same-centre integrals",
        even_tempered_sp,
    )
    attach_binding(uhf_rows)

    # s-only: N = 0, 1, 2 only. Extra electrons in a spherical s basis are
    # not a model of B–Ne and produce meaningless positive energies.
    s_rows = []
    for z in z_list:
        basis = even_tempered_s(z, n_s=8)
        s_mat, h_mat = one_electron(float(z), basis)
        eri = two_electron(basis)
        for n in (0, 1, 2):
            if n == 0:
                s_rows.append(
                    {
                        "label": LABEL,
                        "ok": True,
                        "method": "UHF even-tempered s-GTO (N<=2 spherical check)",
                        "N": 0,
                        "Z": z,
                        "E": 0.0,
                        "scf_converged": True,
                        "note": "bare nucleus, exact",
                        "units": HARTREE,
                        "n_ao": len(basis),
                    }
                )
                continue
            rec = uhf_energy(float(z), n, s_mat, h_mat, eri)
            rec["method"] = "UHF even-tempered s-GTO (N<=2 spherical check)"
            if rec.get("ok"):
                rec["certified_vs_exact_previous"] = _certified_vs_exact(
                    n, z, rec["E"]
                )
            s_rows.append(rec)
    attach_binding(s_rows)

    table = {
        "label": LABEL,
        "disclaimer": (
            "HEURISTIC. Not a bound on N0(Z). Solovej (arXiv:math-ph/0012026) "
            "already proved the ionization conjecture in Hartree–Fock; these "
            "numbers do not move that theorem. Comparing two variational "
            "energies is not a proof of binding. Experimental ionization "
            "energies are leads, not certificates. An incomplete search is "
            "not a lower bound."
        ),
        "units": HARTREE,
        "status": "residue",
        "helium_like_slater": {
            "label": LABEL,
            "method": "1-parameter 1s Slater; E(1)=-Z^2/2, E(2)=-(Z-5/16)^2",
            "rows": he_rows,
            "N0_hat": n0_hat(he_rows),
        },
        "uhf_sp": {
            "label": LABEL,
            "method": (
                "UHF, even-tempered same-centre Gaussians with 1s/2s/2p "
                "scales, analytic s and Cartesian p integrals"
            ),
            "rows": uhf_rows,
            "N0_hat": n0_hat(uhf_rows),
        },
        "uhf_s_n12": {
            "label": LABEL,
            "method": "UHF, even-tempered s-Gaussians only, N=0,1,2",
            "rows": s_rows,
            "N0_hat": n0_hat(s_rows),
        },
        "hf_limit_neutral_lead": {
            "label": LABEL,
            "note": (
                "Published numerical HF limits for neutrals, for orientation. "
                "Leads, not used as thresholds or certificates."
            ),
            "E": HF_LIMIT_NEUTRAL,
        },
    }
    return table


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Heuristic atomic HF table")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--z-max", type=int, default=10)
    p.add_argument(
        "--out",
        default=os.path.join(CERT_DIR, "hf_table.json"),
        help="output JSON (default: certs/hf_table.json)",
    )
    args = p.parse_args(argv)

    fails = self_test()
    if fails:
        print("SELF-TEST FAILED")
        for f in fails:
            print(" ", f)
        return 1
    print("self-test: ok")
    if args.self_test:
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    table = build_table(z_max=args.z_max)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(table, fh, indent=2)
        fh.write("\n")
    print(f"wrote {args.out}  label={LABEL}")
    for name in ("helium_like_slater", "uhf_sp", "uhf_s_n12"):
        block = table[name]
        print(f"\n{name}  N0_hat (HEURISTIC, residue):")
        for z, rec in block["N0_hat"].items():
            print(f"  Z={z}  N0_hat={rec['N0_hat']}")
        # Neutral energies
        print("  neutrals E(Z,Z):")
        for r in block["rows"]:
            if r.get("ok") and r.get("N") == r.get("Z"):
                conv = r.get("scf_converged", True)
                print(
                    f"    Z={r['Z']}  E={r['E']:.8f}  conv={conv}  "
                    f"binds={r.get('heuristic_binds_vs_N-1')}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
