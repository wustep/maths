#!/usr/bin/env python3
"""F₄ linear forms rebuilt from labeled 4-graphs, plus a published CSS tighten.

Lemma 4.4 of Hladký–Král'–Norin (Combinatorica 2017) gives induction for every
type whose vertex 1 is a sink. Order 3 yields only T and V (already in HKN).
The unique order-2 sink type (arc 2→1) expands to a linear form on F₄ after
averaging over the four triples of each 4-graph.

Out-regularity (4.1) lifts to β- and η-flags: each root still has out-density c,
so K_i·(α−c) and η_i·(α−c) are identities on F₄.

Fork: HKN use CSS β≤γ, hence Ψ(κ)≥3(3c−1)². Chen–Karson–Liu–Shen (Electron. J.
Linear Algebra 28, 2015; arXiv:0909.2468) prove β<0.8616 γ for 3-free digraphs.
HHK's √(2k) argument then gives deg⁺<√(2·0.8616 k), and the same chain as HKN
Lemmas 3.5–4.7 yields Ψ(κ)≥3(3c−1)²/0.8616. The 4Ψ(κ) type-coefficients are
rebuilt by enumeration; only the penalty changes.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

PARENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PARENT))
from flags4 import (  # noqa: E402
    K_flag,
    canon_key,
    enumerate_labeled,
    induced,
    type_of,
)

# Chen–Karson–Liu–Shen 2015, Theorem 2.5.
CSS_BETA_CKLS = 0.8616
CSS_BETA_DHP = 0.88  # Dunkum–Hamburger–Pór, Combinatorica 31 (2011)
CSS_BETA_HKN = 1.0

ETA_FLAGS = [(a, b) for a in (0, 1, 2) for b in (0, 1, 2)]


def eta_id(arcs3) -> int | None:
    if (0, 1) in arcs3 or (1, 0) in arcs3:
        return None

    def code(u, v):
        if (u, v) in arcs3:
            return 1
        if (v, u) in arcs3:
            return 2
        return 0

    return ETA_FLAGS.index((code(0, 2), code(1, 2)))


def compute_AC_eta():
    n_type = [0] * 32
    acc = np.zeros((9, 9, 32))
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for perm in itertools.permutations(range(4)):
            x, y, z, w = perm
            if (x, y) in arcs or (y, x) in arcs:
                continue
            ki = eta_id(induced(arcs, (x, y, z)))
            kj = eta_id(induced(arcs, (x, y, w)))
            if ki is None or kj is None:
                continue
            acc[ki, kj, t] += 1
    AC = np.zeros((9, 9, 32))
    for t in range(32):
        if n_type[t]:
            AC[:, :, t] = acc[:, :, t] / n_type[t]
    return AC, n_type


_KAPPA4_CACHE: list[float] | None = None


def kappa4_coeffs():
    """4Ψ(κ) type coefficients by labeled 4-count. Must match HKN (4.7)."""
    global _KAPPA4_CACHE
    if _KAPPA4_CACHE is not None:
        return _KAPPA4_CACHE
    n_type = [0] * 32
    n_fork = [0] * 32
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        forks = 0
        for triple in itertools.combinations(range(4), 3):
            sub = induced(arcs, triple)
            for ctr in range(3):
                leaves = [i for i in range(3) if i != ctr]
                if (ctr, leaves[0]) in sub and (ctr, leaves[1]) in sub:
                    if (leaves[0], leaves[1]) not in sub and (leaves[1], leaves[0]) not in sub:
                        if (leaves[0], ctr) not in sub and (leaves[1], ctr) not in sub:
                            forks += 1
                            break
        n_fork[t] += forks
    _KAPPA4_CACHE = [n_fork[t] / n_type[t] if n_type[t] else 0.0 for t in range(32)]
    return _KAPPA4_CACHE


KAPPA4_PUB = [0.0] * 32
for _k, _m in [
    (4, 1),
    (7, 1),
    (8, 3),
    (12, 1),
    (17, 1),
    (19, 1),
    (20, 2),
    (21, 2),
    (23, 1),
    (25, 1),
    (26, 1),
    (29, 1),
    (30, 2),
]:
    KAPPA4_PUB[_k] = float(_m)


def fork_coeffs(c: float, css_beta: float = CSS_BETA_HKN) -> list[float]:
    """Fork(Ψ) = 4Ψ(κ) − 12(3c−1)²/css_beta.

    css_beta=1 is HKN. css_beta=0.8616 is CKLS 2015 via the HHK √(2βk) lemma.
    """
    if css_beta <= 0:
        raise ValueError("css_beta must be positive")
    penalty = 12.0 * (3.0 * c - 1.0) ** 2 / css_beta
    kappa = kappa4_coeffs()
    return [kappa[k] - penalty for k in range(32)]


def _ind2_on_triple(arcs3, c: float) -> float:
    """Lemma 4.4 for σ = (2→1): sum over embeddings of n_src + c(n_F0 − n_emb)."""
    n_emb = n_src = n_f0 = 0
    verts = (0, 1, 2)
    for v1, v2, extra in itertools.permutations(verts):
        if (v2, v1) not in arcs3:
            continue
        n_emb += 1
        if (extra, v1) in arcs3 or (extra, v2) in arcs3:
            continue
        if (v1, extra) in arcs3 and (v2, extra) in arcs3:
            n_f0 += 1
        else:
            n_src += 1
    if n_emb == 0:
        return 0.0
    return n_src + c * (n_f0 - n_emb)


def ind2_coeffs(c: float) -> list[float]:
    """Pull [[f(σ)]]_σ, σ the order-2 sink type, to F₄ by averaging triples."""
    n_type = [0] * 32
    acc = [0.0] * 32
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        s = 0.0
        for drop in range(4):
            verts = tuple(v for v in range(4) if v != drop)
            s += _ind2_on_triple(induced(arcs, verts), c)
        acc[t] += s / 4.0
    return [acc[t] / n_type[t] if n_type[t] else 0.0 for t in range(32)]


def compute_beta_regularity():
    """AR/BR for K_i · (α_at_root − c), roots 0 and 1 of a β-edge.

    Returns (AR1, BR1, AR2, BR2) each 8×32, averaged per labeled type.
    """
    n_type = [0] * 32
    ar1 = np.zeros((8, 32))
    br1 = np.zeros((8, 32))
    ar2 = np.zeros((8, 32))
    br2 = np.zeros((8, 32))
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for perm in itertools.permutations(range(4)):
            x, y, z, w = perm
            if (x, y) not in arcs:
                continue
            ki = K_flag(induced(arcs, (x, y, z)))
            if ki is None:
                continue
            ar1[ki, t] += 1
            ar2[ki, t] += 1
            if (x, w) in arcs:
                br1[ki, t] += 1
            if (y, w) in arcs:
                br2[ki, t] += 1
    for arr in (ar1, br1, ar2, br2):
        for i in range(8):
            for t in range(32):
                if n_type[t]:
                    arr[i, t] /= n_type[t]
    return ar1, br1, ar2, br2, n_type


def compute_eta_regularity():
    """AR/BR for η_i · (α_at_root − c) on the order-2 non-edge type."""
    n_type = [0] * 32
    ar1 = np.zeros((9, 32))
    br1 = np.zeros((9, 32))
    ar2 = np.zeros((9, 32))
    br2 = np.zeros((9, 32))
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for perm in itertools.permutations(range(4)):
            x, y, z, w = perm
            if (x, y) in arcs or (y, x) in arcs:
                continue
            ki = eta_id(induced(arcs, (x, y, z)))
            if ki is None:
                continue
            ar1[ki, t] += 1
            ar2[ki, t] += 1
            if (x, w) in arcs:
                br1[ki, t] += 1
            if (y, w) in arcs:
                br2[ki, t] += 1
    for arr in (ar1, br1, ar2, br2):
        for i in range(9):
            for t in range(32):
                if n_type[t]:
                    arr[i, t] /= n_type[t]
    return ar1, br1, ar2, br2, n_type


def check_kappa4():
    got = kappa4_coeffs()
    ok = all(abs(got[k] - KAPPA4_PUB[k]) < 1e-12 for k in range(32))
    return ok, got


def three_vertex_type_count():
    """Sanity: how many unlabeled C3-free oriented 3-graphs."""
    keys = set()
    n = 0
    for arcs in enumerate_labeled(3):
        n += 1
        keys.add(canon_key(arcs, 3))
    return n, len(keys)


if __name__ == "__main__":
    ok, kap = check_kappa4()
    print("kappa4 matches HKN (4.7)?", ok)
    if not ok:
        raise SystemExit(2)
    print("nonzero 4Ψ(κ) types:", [k for k in range(32) if abs(kap[k]) > 1e-12])
    nlab, ntyp = three_vertex_type_count()
    print("labeled/unlabeled C3-free 3-graphs:", nlab, ntyp)
