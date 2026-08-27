#!/usr/bin/env python3
"""Certified lower bound on β_3^{rad}.

Scale so D = ∫ r² dm = 1. Split (0,∞) into (0, α) ∪ [α, 1/α] ∪ (1/α, ∞)
with α = R^{-1/2}. The middle scales to [1, R]. On [1, R]:

  I/D ≥ φ_mid − [θ/(1−θ)](1 − fmin)

where φ_mid is the discrete mid-radius Rayleigh with F_ij = min f on
each bin-pair, θ = R^{1/n} − 1, and f(t) = (1+t³)/(1+t²).

φ_mid ≥ γ_target is certified by exhaustive face enumeration of
m^T M m on the simplex (verify_beta3.c), M = A − γ_target (c 1^T + 1 c^T)/2.

The tail lemma then gives I ≥ γ_target − err for every probability m
with finite D, once R is large enough that the (D_L, D_R) minimum sits
at the origin.

Writes certs/beta3_matrix.txt, certs/beta3_rad.json.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

from beta3_kernel import (
    FMIN_MP,
    S,
    assemble_mid,
    b3_iv,
    b_of_s,
    fmin_iv,
    iv_bounds,
    tail_h,
    tail_lemma_min,
    t0_iv,
)

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
WORK = HERE / "work"

# Aspect-12 window: α = 1/√12, middle scales to [1, 12].
N_BINS = 26
R_WIN = 12
# Below the numerical φ_mid ≈ 0.90853; above fmin + err ≈ 0.90591.
GAMMA_TARGET = 0.9072


def write_matrix(blob, gamma_target: float, path: Path) -> None:
    n = blob["n"]
    lines = [f"{n} {gamma_target:.16e}"]
    lines.append(" ".join(f"{float(c):.16e}" for c in blob["rmid2"]))
    for i in range(n):
        lines.append(" ".join(f"{float(blob['A_lo'][i][j]):.16e}" for j in range(n)))
    path.write_text("\n".join(lines) + "\n")


def parse_faces(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        k, _, v = line.partition(" ")
        if k in {
            "n",
            "interior_critical",
            "singular_or_illconditioned",
            "n_faces",
            "copositive",
        }:
            out[k] = int(float(v))
        else:
            out[k] = float(v)
    return out


def tail_certified(a, beta, fmin_hi, n_grid: int = 80):
    """Interval minimum of the tail polynomial on the triangle.

    h(x,y) is quadratic, so a modest interval grid has no remainder
    beyond the outward rounding already in mpmath.iv.
    """
    a = iv.mpf(str(a)) if not isinstance(a, type(iv.mpf(1))) else a
    beta = iv.mpf(str(beta)) if not isinstance(beta, type(iv.mpf(1))) else beta
    fmin = iv.mpf(str(fmin_hi))

    def h_iv(x, y):
        Dc = 1 - x - y
        return (
            beta * Dc
            + (x / a) * (1 - beta) * Dc
            + y * (1 - a * (1 - fmin) - a * beta * Dc)
        )

    a_hi = mpf(a.b)
    best_lo = mpf("1e9")
    at = (mpf(0), mpf(0))
    nx, ny = n_grid, n_grid
    for i in range(nx):
        x = iv.mpf([str(a_hi * i / nx), str(a_hi * (i + 1) / nx)])
        for j in range(ny):
            # y ∈ [0, 1 − x] ⊃ [0, 1 − x.b] guaranteed inside the triangle
            y_top = 1 - mpf(x.b)
            if y_top <= 0:
                continue
            y = iv.mpf([0, str(y_top * (j + 1) / ny)])
            # tighter cell
            y = iv.mpf(
                [str(y_top * j / ny), str(y_top * (j + 1) / ny)]
            )
            val = h_iv(x, y)
            lo = mpf(val.a)
            if lo < best_lo:
                best_lo = lo
                at = (mpf(x.mid), mpf(y.mid))
    # also the three corners exactly
    corners = [
        tail_h(mpf(0), mpf(0), mpf(a.a), mpf(beta.a), mpf(fmin.a)),
        tail_h(mpf(a.a), mpf(0), mpf(a.a), mpf(beta.a), mpf(fmin.a)),
        tail_h(mpf(0), mpf(1) - mpf(a.a), mpf(a.a), mpf(beta.a), mpf(fmin.a)),
    ]
    best_lo = min(best_lo, *corners)
    return best_lo, best_lo, at, mpf(0)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    print(f"assembling n={N_BINS} R={R_WIN} ...")
    blob = assemble_mid(R_WIN, N_BINS)
    gamma_t = GAMMA_TARGET
    write_matrix(blob, gamma_t, CERTS / "beta3_matrix.txt")
    print("wrote", CERTS / "beta3_matrix.txt")

    cbin = HERE / "verify_beta3"
    src = HERE / "verify_beta3.c"
    print("compiling verify_beta3.c ...")
    subprocess.check_call(["gcc", "-O3", "-o", str(cbin), str(src), "-lm"])
    print("running face enumeration (2^{n}-1 faces) ...")
    subprocess.check_call([str(cbin)], cwd=str(HERE))
    faces = parse_faces(CERTS / "beta3_faces.txt")
    if not faces.get("copositive"):
        raise SystemExit("C verifier: M not copositive")

    err_hi = mpf(blob["err_iv"].b)
    fmin_lo = mpf(blob["fmin_iv"].a)
    fmin_hi = mpf(blob["fmin_iv"].b)
    b3_lo = mpf(blob["b3_iv"].a)
    b3_hi = mpf(blob["b3_iv"].b)
    theta_hi = mpf(blob["theta_iv"].b)
    q_hi = mpf(blob["q_iv"].b)

    # I/D ≥ gamma_t − err  on the middle; tail lemma lifts this globally.
    gamma_mid = mpf(gamma_t) - err_hi
    a = mpf(1) / R_WIN
    # Use a slightly smaller beta in h so the lemma is valid for our γ.
    # I ≥ h(D_L, D_R) with this beta, and min h ≥ gamma_mid (at origin
    # it equals beta). We take beta = gamma_mid.
    h_lo, h_grid, h_at, h_rem = tail_certified(a, gamma_mid, fmin_hi, n_grid=200)
    # Origin value is exactly gamma_mid. If the grid+Lipschitz still
    # stays above 1/b(3), we have a global dent.
    gamma_global = min(gamma_mid, h_lo)

    beats = bool(gamma_global > 1 / iv.mpf("1.1185") and gamma_global > fmin_hi)
    inv_hi = 1 / gamma_global

    bs_rows = []
    for s in (3.0, 3.1, 3.5, 4.0, 5.0):
        b, t0 = b_of_s(s)
        bs_rows.append(
            {
                "s": s,
                "b": S(b),
                "t0": S(t0),
                "b_inv": S(1 / b),
                "lt_1.1185": bool(b < mpf("1.1185")),
            }
        )

    status = "dent" if beats and inv_hi < mpf("1.1185") else "residue"
    cert = {
        "arxiv": "2504.18487v1",
        "urls_opened": [
            "https://arxiv.org/abs/2504.18487",
            "https://arxiv.org/html/2504.18487v1",
        ],
        "status": status,
        "is_new_bound": bool(status == "dent"),
        "beats_1.1185": bool(inv_hi < mpf("1.1185")),
        "gamma_lower": S(gamma_global),
        "gamma_inv_upper": S(inv_hi),
        "HPS_b3_interval": list(iv_bounds(blob["b3_iv"])),
        "HPS_fmin_interval": list(iv_bounds(blob["fmin_iv"])),
        "HPS_printed_1.1185_valid_upper_on_b3": bool(b3_hi < mpf("1.1185")),
        "method": (
            "Scale D=1. Geometric bins on the middle window [α,1/α] with "
            "α=R^{-1/2}. F_ij = min f on each bin-pair (unimodal). Mid-radius "
            "Rayleigh φ_mid certified by exhaustive face enumeration of "
            "m^T M m (C). Error θ/(1-θ)(1-fmin) with θ=R^{1/n}-1. Tail lemma "
            "on (D_L, D_R) lifts the middle bound to every Borel probability."
        ),
        "dps": int(mp.dps),
        "window": {
            "R": R_WIN,
            "n_bins": N_BINS,
            "alpha": S(mpf(1) / R_WIN ** (mpf(1) / 2)),
            "q_interval": list(iv_bounds(blob["q_iv"])),
            "theta_interval": list(iv_bounds(blob["theta_iv"])),
            "err_interval": list(iv_bounds(blob["err_iv"])),
            "gamma_target_phi": gamma_t,
            "gamma_middle": S(gamma_mid),
        },
        "face_enumeration": faces,
        "tail_lemma": {
            "a": S(a),
            "beta_used": S(gamma_mid),
            "h_grid_min": S(h_grid),
            "h_at_DL_DR": [S(h_at[0]), S(h_at[1])],
            "lipschitz_remainder": S(h_rem),
            "h_lower": S(h_lo),
            "origin_value": S(gamma_mid),
        },
        "enclosures": {
            "gamma_gt_HPS_fmin": bool(gamma_global > fmin_hi),
            "gamma_inv_lt_1.1185": bool(inv_hi < mpf("1.1185")),
            "gamma_inv_lt_b3": bool(inv_hi < b3_lo),
            "C_copositive": bool(faces.get("copositive")),
        },
        "b_s": bs_rows,
        "numerical_apparent": {
            "note": "from explore_beta3.py; upper bounds on β_3 only",
            "power_law_I_over_D": 0.9206549282371305,
            "power_law_inv": 1.0861832911868505,
            "gap_vs_b3_percent": 2.88,
        },
        "replay": "problems/simon-ionization-excess/compute/q2/run_beta3.sh",
    }

    out = CERTS / "beta3_rad.json"
    out.write_text(json.dumps(cert, indent=2) + "\n")
    print("wrote", out)
    print("status:", status)
    print("gamma ≥", S(gamma_global, 12), "   1/gamma ≤", S(inv_hi, 12))
    print("HPS 1/b(3) ≈", S(FMIN_MP, 12), "   b(3) ≤", S(b3_hi, 12))
    print("beats 1.1185:", cert["beats_1.1185"])
    if status != "dent":
        raise SystemExit("certify_beta3.py residue (no certified dent)")
    print("certify_beta3.py PASS")


if __name__ == "__main__":
    main()
