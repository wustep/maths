#!/usr/bin/env python3
"""Sanity-check C copositivity against a Python face sweep, n=12."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from beta3_kernel import assemble_mid
from certify_beta3 import parse_faces, write_matrix

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def python_face_min_M(M: np.ndarray) -> float:
    n = M.shape[0]
    best = min(float(M[i, i]) for i in range(n))
    nfaces = (1 << n) - 1
    for mask in range(1, nfaces + 1):
        idx = [b for b in range(n) if mask & (1 << b)]
        k = len(idx)
        if k <= 1:
            continue
        Ms = M[np.ix_(idx, idx)]
        try:
            x = np.linalg.solve(Ms, np.ones(k))
        except np.linalg.LinAlgError:
            continue
        if np.any(np.abs(x) <= 1e-12):
            continue
        signs = np.sign(x)
        if not np.all(signs == signs[0]):
            continue
        s = float(np.sum(x))
        if abs(s) <= 1e-12:
            continue
        val = 1.0 / s
        # evaluate exactly
        m = x / s
        val2 = float(m @ Ms @ m)
        best = min(best, val, val2)
    return best


def main():
    CERTS.mkdir(exist_ok=True)
    blob = assemble_mid(4, 12)
    n = 12
    A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
    c = np.array([float(x) for x in blob["rmid2"]])

    subprocess.check_call(
        ["gcc", "-O3", "-o", str(HERE / "verify_beta3"), str(HERE / "verify_beta3.c"), "-lm"]
    )

    for gt, expect_ok in ((0.9040, True), (0.9200, False)):
        M = A - (gt / 2.0) * (c[:, None] + c[None, :])
        py = python_face_min_M(M)
        write_matrix(blob, gt, CERTS / "beta3_matrix.txt")
        rc = subprocess.call([str(HERE / "verify_beta3")], cwd=str(HERE))
        faces = parse_faces(CERTS / "beta3_faces.txt")
        print(
            f"gamma={gt}  py min mᵀMm={py:.6e}  C={faces['min_mMm']:.6e}  "
            f"C_ok={faces['copositive']} rc={rc}"
        )
        if abs(py - faces["min_mMm"]) > 1e-8:
            raise SystemExit(f"C/Python min m^T M m disagree: {py} vs {faces['min_mMm']}")
        if expect_ok and (rc != 0 or not faces["copositive"]):
            raise SystemExit("expected copositive")
        if (not expect_ok) and (rc == 0 or faces["copositive"]):
            raise SystemExit("expected NOT copositive")
    print("test_faces_small.py PASS")


if __name__ == "__main__":
    main()
