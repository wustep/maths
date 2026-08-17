"""Float search for CE Laguerre double-root locations in dimension 2.

This is the discovery engine. A hit is not a bound: certify.py / verify.py
must pass on exact rationals before anything is claimed.
"""

from __future__ import annotations

import math
from itertools import product

import numpy as np

# Hexagonal target: 2π r² = 4π/√3
HEX_R = 4 * math.pi / math.sqrt(3)  # 7.255197456...
LEV_DENSITY = (3.8317059702075125**2) / (16 * math.pi)  # Levenshtein δ
HEX_DENSITY = math.sqrt(3) / 6


def laguerre_vals(n_max: int, t: float):
    """L_0(t),...,L_{n_max}(t) and derivatives via recurrence."""
    L = np.zeros(n_max + 1)
    dL = np.zeros(n_max + 1)
    L[0] = 1.0
    dL[0] = 0.0
    if n_max >= 1:
        L[1] = 1.0 - t
        dL[1] = -1.0
    for k in range(1, n_max):
        # (k+1) L_{k+1} = (2k+1-t) L_k - k L_{k-1}
        L[k + 1] = ((2 * k + 1 - t) * L[k] - k * L[k - 1]) / (k + 1)
        dL[k + 1] = ((2 * k + 1 - t) * dL[k] - L[k] - k * dL[k - 1]) / (k + 1)
    return L, dL


def odd_idx(m):
    return list(range(1, 4 * m + 4, 2))


def even_idx(m):
    return list(range(0, 4 * m + 3, 2))


def build_G_float(m: int, t_roots: list[float]):
    odds = odd_idx(m)
    n = len(odds)
    nmax = odds[-1]
    A = np.zeros((n - 1, n))
    # G(0)=sum a
    A[0, :] = 1.0
    r = 1
    for ti in t_roots:
        L, dL = laguerre_vals(nmax, ti)
        A[r, :] = [L[k] for k in odds]
        A[r + 1, :] = [dL[k] for k in odds]
        r += 2
    # 1d kernel via SVD
    _, s, vh = np.linalg.svd(A)
    if s[-1] > 1e-10:
        return None
    a = vh[-1, :].copy()
    if a[0] < 0:
        a = -a
    return a


def G_value_deriv(m, a, t):
    odds = odd_idx(m)
    L, dL = laguerre_vals(odds[-1], t)
    v = sum(aj * L[k] for aj, k in zip(a, odds))
    dv = sum(aj * dL[k] for aj, k in zip(a, odds))
    return v, dv


def last_sign_change(m, a, t_roots=None, t_lo=0.05, t_hi=40.0, ngrid=5000):
    """Scan for last odd-multiplicity sign change of G, skipping forced doubles."""
    skip = [] if t_roots is None else list(t_roots)
    ts = np.linspace(t_lo, t_hi, ngrid)
    vals = np.array([G_value_deriv(m, a, t)[0] for t in ts])
    last = None
    for i in range(len(ts) - 1):
        if vals[i] == 0 or vals[i] * vals[i + 1] >= 0:
            continue
        lo, hi = ts[i], ts[i + 1]
        vlo = vals[i]
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            vm = G_value_deriv(m, a, mid)[0]
            if vlo * vm <= 0:
                hi, vhi = mid, vm
            else:
                lo, vlo = mid, vm
        cand = 0.5 * (lo + hi)
        if any(abs(cand - z) < 0.35 for z in skip):
            continue
        last = cand
    return last


def density(R):
    return R / (8 * math.pi)


def ratio(R):
    return R * math.sqrt(3) / (4 * math.pi)


def eval_roots(m, t_roots, t_hi=250.0):
    a = build_G_float(m, t_roots)
    if a is None:
        return None
    r = last_sign_change(m, a, t_roots=t_roots, t_hi=t_hi)
    if r is None:
        return None
    return {"a": a, "r": r, "dens": density(r), "ratio": ratio(r), "t": t_roots}


def scan_m1():
    print("=== m=1 scan ===")
    best = None
    for z in np.linspace(10.0, 80.0, 281):
        rec = eval_roots(1, [float(z)])
        if rec is None:
            continue
        if rec["r"] > 15:
            continue
        if best is None or rec["r"] < best["r"]:
            best = rec
            print(f"  z={z:.4f}  r={rec['r']:.6f}  dens={rec['dens']:.8f}  ratio={rec['ratio']:.8f}")
    return best


def scan_m2():
    print("=== m=2 coarse grid ===")
    best = None
    for z1 in np.linspace(18.0, 26.0, 17):
        for z2 in np.linspace(26.0, 40.0, 15):
            if z2 <= z1 + 0.5:
                continue
            rec = eval_roots(2, [float(z1), float(z2)])
            if rec is None or rec["r"] > 12:
                continue
            if best is None or rec["r"] < best["r"]:
                best = rec
                print(
                    f"  z={z1:.3f},{z2:.3f}  r={rec['r']:.6f}  "
                    f"dens={rec['dens']:.8f}  ratio={rec['ratio']:.8f}"
                )
    return best


def refine(m, t0, steps=80, step0=0.4):
    """Coordinate descent on last sign change."""
    t = list(t0)
    rec = eval_roots(m, t)
    if rec is None:
        return None
    best_t, best_r = t[:], rec["r"]
    print(f"  refine start t={t} r={best_r:.8f}")
    step = step0
    for it in range(steps):
        improved = False
        for i in range(m):
            for sgn in (+1, -1):
                trial = best_t[:]
                trial[i] = trial[i] + sgn * step
                if trial[i] <= (best_t[i - 1] + 0.2 if i else 8.0):
                    continue
                if i + 1 < m and trial[i] >= best_t[i + 1] - 0.2:
                    continue
                rec = eval_roots(m, trial)
                if rec is None:
                    continue
                if rec["r"] + 1e-8 < best_r and rec["r"] > 6.5:
                    best_r = rec["r"]
                    best_t = trial
                    improved = True
                    print(f"  it={it} t={[round(x,5) for x in best_t]} r={best_r:.8f} ratio={ratio(best_r):.8f}")
        if not improved:
            step *= 0.5
            if step < 1e-5:
                break
    rec = eval_roots(m, best_t)
    return rec


def main():
    print(f"hex R={HEX_R:.12f}  hex dens={HEX_DENSITY:.12f}")
    print(f"Levenshtein dens≈{LEV_DENSITY:.8f}  ratio≈{LEV_DENSITY/HEX_DENSITY:.6f}")
    print(f"CE Table4 R=7.25520  dens={density(7.25520):.10f}  ratio={ratio(7.25520):.10f}")

    print("\n=== CE Table 4 seeds m=5 ===")
    ce = [21.77, 29.02, 50.79, 65.34, 90.19]
    rec = eval_roots(5, ce, t_hi=30.0)
    print("CE seeds", rec)
    if rec:
        rec = refine(5, ce, steps=40, step0=0.3)

    print("\n=== A2 shell seeds (N=3,4,7,9,12) ===")
    # 2π |x|² = (4π/√3) * N for isodual A2
    shells = [3, 4, 7, 9, 12]
    seed = [HEX_R * n for n in shells]
    print("shell t", seed)
    rec2 = eval_roots(5, seed, t_hi=30.0)
    print("shell rec", None if rec2 is None else {k: rec2[k] for k in ("r", "dens", "ratio")})
    if rec2:
        refine(5, seed, steps=40, step0=0.2)

    print("\n=== slightly perturbed shells ===")
    for eps in (0.01, 0.05, 0.1, 0.2, -0.05, 0.3):
        t = [HEX_R * n + eps for n in shells]
        recp = eval_roots(5, t, t_hi=20.0)
        if recp:
            print(f"  eps={eps:+.2f} r={recp['r']:.8f} ratio={recp['ratio']:.8f}")

    b1 = scan_m1()
    if b1:
        refine(1, b1["t"], steps=30, step0=0.5)
    b2 = scan_m2()
    if b2:
        refine(2, b2["t"], steps=40, step0=0.3)

    # m=3 from first three shells
    print("\n=== m=3 shells ===")
    s3 = [HEX_R * n for n in (3, 4, 7)]
    rec3 = eval_roots(3, s3, t_hi=20)
    print("m=3", None if rec3 is None else (rec3["r"], rec3["ratio"]))
    if rec3:
        refine(3, s3, steps=40, step0=0.25)

    print("\n=== m=4 shells ===")
    s4 = [HEX_R * n for n in (3, 4, 7, 9)]
    rec4 = eval_roots(4, s4, t_hi=20)
    print("m=4", None if rec4 is None else (rec4["r"], rec4["ratio"]))
    if rec4:
        refine(4, s4, steps=40, step0=0.25)


if __name__ == "__main__":
    main()
