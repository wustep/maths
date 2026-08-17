#!/usr/bin/env python3
"""Dump Hou–Zhao R=8 kernels with L=6 QP weights as a float candidate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vector_smoothing import solve_boundary_qp  # noqa: E402

ROOT = Path(__file__).resolve().parent
ns: dict = {}
exec((ROOT / "refs" / "sidon_numerical_search.py").read_text(), ns)
ker, lam = ns["stored_candidates"]()[8]
ker = np.asarray(ker, dtype=float)
lam = np.asarray(lam, dtype=float)
L = 6
wL, wR, a, b, g = solve_boundary_qp(ker, lam, L)
payload = {
    "tag": "hz-r8-L6-float",
    "m": 32,
    "L": L,
    "asymmetric": False,
    "gamma_float": g,
    "a_float": a,
    "b_float": b,
    "lambdas": lam.tolist(),
    "kernels": ker.tolist(),
    "weights_left": wL.tolist(),
    "weights_right": wR.tolist(),
}
out = ROOT / "certs" / "hz_r8_L6_float.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
print("gamma", g)
print("wrote", out)
