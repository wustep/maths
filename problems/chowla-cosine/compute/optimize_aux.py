#!/usr/bin/env python3
"""Search a 2-parameter family of auxiliaries around Bedert §7.

f = 2 (1 + alpha sin(2 pi t x)) hat{1}_A
r = (1 - beta cos(2 pi t x + phi)) (f * f)

Bedert: (alpha, beta, phi) = (1, 1, pi/4).

We evaluate the 32 windows in complex float (for search only) and
report the isolation gap and the implied C_* using the same Q1/Q2
constants as the exact tracker. A candidate is only a lead — the
certified bound uses the exact Bedert point unless a later exact
check upgrades it.
"""

from __future__ import annotations

import cmath
import json
import math
from pathlib import Path


def rho_float(bits, alpha, beta, phi):
    u, a, b, c, v = bits

    def fhat(am_tm1, am, am_tp1):
        return 2 * am - 1j * alpha * am_tm1 + 1j * alpha * am_tp1

    fm = fhat(a, b, c)
    fmt = fhat(u, a, b)
    ftp = fhat(b, c, v)
    eip = cmath.exp(1j * phi)
    return fm * fm - (beta * eip / 2) * (fmt * fmt) - (beta * eip.conjugate() / 2) * (ftp * ftp)


def stats(alpha, beta, phi):
    max_re = -1e300
    max_im = 0.0
    min_neg_im_bt = 1e300
    n_bt = 0
    sign_ok = True
    for mask in range(32):
        bits = tuple((mask >> k) & 1 for k in range(5))
        rho = rho_float(bits, alpha, beta, phi)
        re, im = rho.real, rho.imag
        max_re = max(max_re, re)
        max_im = max(max_im, abs(im))
        if bits[1] == 1 and bits[2] == 1 and bits[3] == 0:
            n_bt += 1
            if im > 1e-12:
                sign_ok = False
            min_neg_im_bt = min(min_neg_im_bt, -im)
    gap = min_neg_im_bt - max_re
    cr = 4.0 * (1.0 + abs(alpha)) ** 2 * (1.0 + abs(beta))
    return {
        "alpha": alpha,
        "beta": beta,
        "phi": phi,
        "gap": gap,
        "max_re": max_re,
        "max_im": max_im,
        "min_neg_im_bt": min_neg_im_bt,
        "sign_ok": sign_ok,
        "C_r": cr,
        "n_bt": n_bt,
    }


def cstar_from(st, c_q1=3.0, c_q2=14.0):
    """Same quadratic as track_constants.py, float preview."""
    gap = st["gap"]
    if gap <= 0 or not st["sign_ok"]:
        return None
    psi = st["max_re"]
    phi_b = st["min_neg_im_bt"]
    phi_m = st["max_im"]
    cr = st["C_r"]
    A = 2 * c_q2 * (phi_m + psi) / gap
    B = (c_q2 ** 2 * (phi_m + psi) + cr * c_q1 ** 2) / gap
    # z^2 <= A z + B
    disc = A * A + 4 * B
    z = 0.5 * (A + math.sqrt(disc))
    return z * z


def main():
    bedert = stats(1.0, 1.0, math.pi / 4)
    bedert["Cstar_preview"] = cstar_from(bedert)
    print("Bedert (1,1,pi/4):", {k: bedert[k] for k in bedert if k != "n_bt"})

    best = bedert
    # coarse grid
    alphas = [i / 10 for i in range(5, 11)]
    betas = [i / 10 for i in range(5, 11)]
    phis = [math.pi * i / 16 for i in range(0, 17)]
    scanned = 0
    leads = []
    for a in alphas:
        for b in betas:
            for p in phis:
                scanned += 1
                st = stats(a, b, p)
                cs = cstar_from(st)
                if cs is None:
                    continue
                st["Cstar_preview"] = cs
                if cs < best["Cstar_preview"] - 1e-6:
                    best = st
                    leads.append(st)

    print(f"scanned {scanned} grid points")
    print("best Cstar preview:", {k: best[k] for k in ("alpha", "beta", "phi", "gap", "C_r", "Cstar_preview")})

    # refine around best
    a0, b0, p0 = best["alpha"], best["beta"], best["phi"]
    for da in [-0.05, -0.02, 0, 0.02, 0.05]:
        for db in [-0.05, -0.02, 0, 0.02, 0.05]:
            for dp in [-0.05, -0.02, 0, 0.02, 0.05]:
                a = min(1.0, max(0.0, a0 + da))
                b = min(1.0, max(0.0, b0 + db))
                p = p0 + dp
                st = stats(a, b, p)
                cs = cstar_from(st)
                if cs is None:
                    continue
                st["Cstar_preview"] = cs
                if cs < best["Cstar_preview"] - 1e-6:
                    best = st

    print("refined best:", {k: best[k] for k in ("alpha", "beta", "phi", "gap", "C_r", "Cstar_preview")})

    out = {
        "bedert_Cstar_preview": bedert["Cstar_preview"],
        "best_preview": {
            "alpha": best["alpha"],
            "beta": best["beta"],
            "phi": best["phi"],
            "gap": best["gap"],
            "C_r": best["C_r"],
            "Cstar_preview": best["Cstar_preview"],
        },
        "improved": best["Cstar_preview"] < bedert["Cstar_preview"] - 1e-3,
        "note": "float search only; certified bound uses exact Bedert point unless upgraded",
    }
    Path(__file__).resolve().parent.joinpath("aux_search.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
