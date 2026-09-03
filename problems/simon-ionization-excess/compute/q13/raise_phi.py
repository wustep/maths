#!/usr/bin/env python3
"""Raise φ_target on a stored or freshly assembled mid-radius matrix.

Usage:
  python3 raise_phi.py --R 12 --n 22 --target 0.9068
  python3 raise_phi.py --R 12 --n 24 --target 0.9064
  python3 raise_phi.py --from-q2-R12 --target 0.9068

Writes certs/beta3_mid_R{R}_n{n}_t{target}.txt and a faces dump.
Exit 0 only if the C enumerator certifies copositivity.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from mpmath import mpf

HERE = Path(__file__).resolve().parent
Q2 = HERE.parent / "q2"
sys.path.insert(0, str(Q2))

from beta3_kernel import assemble_mid  # noqa: E402

CERTS = HERE / "certs"
Q2_CERTS = Q2 / "certs"
C_SRC = HERE / "verify_beta3.c"


def write_matrix(A, c, lam, path: Path) -> None:
    n = A.shape[0]
    lines = [f"{n} {lam:.16e}"]
    lines.append(" ".join(f"{c[i]:.16e}" for i in range(n)))
    for i in range(n):
        lines.append(" ".join(f"{A[i, j]:.16e}" for j in range(n)))
    path.write_text("\n".join(lines) + "\n")


def load_q2_R12():
    path = Q2_CERTS / "beta3_mid_R12_n22.txt"
    toks = path.read_text().split()
    n = int(float(toks[0]))
    old_t = float(toks[1])
    c = np.array([float(x) for x in toks[2 : 2 + n]])
    A = np.array([float(x) for x in toks[2 + n : 2 + n + n * n]]).reshape(n, n)
    return n, old_t, A, c


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
            "gray_i",
        }:
            out[k] = int(float(v))
        else:
            out[k] = float(v)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--n", type=int, default=22)
    ap.add_argument("--target", type=float, required=True)
    ap.add_argument("--from-q2-R12", action="store_true")
    args = ap.parse_args()

    CERTS.mkdir(parents=True, exist_ok=True)
    if args.from_q2_R12:
        n, old_t, A, c = load_q2_R12()
        R = 12.0
        src = "q2 stored R=12 n=22 matrix (A,c reused; only γ changes)"
        print(f"loaded q2 matrix n={n} old_target={old_t}")
    else:
        R = args.R
        n = args.n
        blob = assemble_mid(R, n)
        A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
        c = np.array([float(blob["rmid2"][i]) for i in range(n)])
        src = f"assemble_mid R={R} n={n}"

    tag = f"R{int(R)}_n{n}_t{args.target:.4f}".replace(".", "p")
    mat = CERTS / f"beta3_mid_{tag}.txt"
    fac = CERTS / f"beta3_mid_faces_{tag}.txt"
    write_matrix(A, c, args.target, mat)

    print(f"enumerating {n} bins, {(1<<n)-1} faces, target={args.target}")
    nfaces = (1 << n) - 1
    skip_enum = False
    if fac.exists():
        try:
            prev = parse_faces(fac)
            gi = int(prev.get("gray_i", 0))
            if (
                int(prev.get("copositive", 0)) == 1
                and float(prev.get("min_mMm_safe", -1)) >= 0
                and gi >= nfaces
            ):
                print(f"reusing complete Gray dump {fac.name}")
                skip_enum = True
        except (OSError, ValueError, KeyError):
            skip_enum = False
    if not skip_enum:
        gray_src = HERE / "verify_gray.c"
        gray_bin = HERE / "verify_gray"
        subprocess.check_call(
            ["gcc", "-O3", "-march=native", "-o", str(gray_bin), str(gray_src), "-lm"]
        )
        subprocess.check_call([str(gray_bin), str(mat), str(fac)], cwd=str(HERE))
    faces = parse_faces(fac)

    q = float(R) ** (1.0 / n)
    P = (q - 1.0) / (q + 1.0)
    # interval-style upper on P: use a hair more
    from mpmath import iv, mp

    mp.dps = 60
    iv.dps = 60
    q_iv = iv.exp(iv.log(iv.mpf(str(R))) / n)
    P_iv = (q_iv - 1) / (q_iv + 1)
    fmin_iv = (iv.mpf(3) / 2) * (
        iv.exp(iv.log(1 + iv.sqrt(2)) / 3) - 1 / iv.exp(iv.log(1 + iv.sqrt(2)) / 3)
    )
    err = P_iv * (1 - fmin_iv)
    err_hi = float(mpf(err.b))
    certified = bool(faces.get("copositive") and faces.get("min_mMm_safe", -1) >= 0)
    gamma = args.target - err_hi if certified else None
    inv = (1.0 / gamma) if gamma else None
    blob = {
        "source": src,
        "R": R,
        "n": n,
        "target": args.target,
        "faces": faces,
        "certified": certified,
        "err_P_hi": err_hi,
        "P_max_hi": float(mpf(P_iv.b)),
        "compact_gamma": gamma,
        "compact_inv": inv,
        "cut": R / (R + 1.0),
        "split_gamma": (min(gamma, R / (R + 1.0)) if gamma else None),
        "split_inv": (
            1.0 / min(gamma, R / (R + 1.0)) if gamma else None
        ),
        "matrix": str(mat.relative_to(HERE)),
        "faces_path": str(fac.relative_to(HERE)),
    }
    out = CERTS / f"raise_{tag}.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print(json.dumps({k: blob[k] for k in (
        "certified", "compact_gamma", "compact_inv", "split_inv", "cut"
    )}, indent=2))
    print("wrote", out)
    if not certified:
        raise SystemExit("raise_phi.py FAIL (not copositive)")
    print("raise_phi.py PASS")


if __name__ == "__main__":
    main()
