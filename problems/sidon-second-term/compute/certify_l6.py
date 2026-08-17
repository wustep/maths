#!/usr/bin/env python3
"""Exact L=6 lift of the published Hou–Zhao kernels (λ and p unchanged).

a is therefore the same rational as Claim 4.1. Only the boundary length and
the weight vectors change. If the new b is small enough that
sqrt(a b) < 0.943492590713545, this is a strict improvement of their γ0.
"""

from __future__ import annotations

import ast
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vector_smoothing import solve_boundary_qp  # noqa: E402

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "refs" / "sidon_certificate_8kernel.py"
HZ_GAMMA0 = 0.943492590713545


def eval_const(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [eval_const(x) for x in node.elts]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"F", "Fraction"}:
        args = [eval_const(a) for a in node.args]
        return Fraction(*args) if len(args) == 2 else Fraction(args[0])
    return ast.literal_eval(node)


def load_hz():
    tree = ast.parse(SRC.read_text())
    D = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0]
            if isinstance(name, ast.Name) and (name.id.isupper() or name.id in {"m", "L"}):
                try:
                    D[name.id] = eval_const(node.value)
                except Exception:
                    continue
    return D


def main():
    D = load_hz()
    m = D["m"]
    L = 6
    n = m * L
    lams = [Fraction(x, D["DL"]) for x in D["LAMBDA_INTS"]]

    def sym(half):
        v = [Fraction(x, D["DP"]) for x in half]
        return v + list(reversed(v))

    kernels = [
        sym(D["P1_HALF_INTS"]),
        [Fraction(1, m)] * m,
        sym(D["P3_HALF_INTS"]),
        sym(D["P4_HALF_INTS"]),
        sym(D["P5_HALF_INTS"]),
        sym(D["P6_HALF_INTS"]),
        sym(D["P7_HALF_INTS"]),
        sym(D["P8_HALF_INTS"]),
    ]
    a = Fraction(m) * sum(lam * sum(x * x for x in p) for lam, p in zip(lams, kernels))

    ker_f = np.array([[float(x) for x in row] for row in kernels], dtype=float)
    lam_f = np.array([float(x) for x in lams], dtype=float)
    wL_f, _, _, b_float, g_float = solve_boundary_qp(ker_f, lam_f, L)
    print("float_gamma_L6", g_float)
    print("float_b", b_float)

    den_w = 10**12
    w_rat = []
    for row in wL_f:
        w_rat.append([Fraction(int(round(float(x) * den_w)), den_w) for x in row])

    def slacks(weights):
        out = []
        for q in range(n + 1):
            tot = Fraction(0)
            for lam, p, w in zip(lams, kernels, weights):
                for i, pi in enumerate(p):
                    j = q + i
                    tot += lam * pi * (w[j] if j < n else Fraction(1))
            out.append(tot - 1)
        return out

    sl = slacks(w_rat)
    eta = Fraction(0)
    for q, s in enumerate(sl[:-1]):
        if s < 0:
            rho = Fraction(0)
            for lam, p in zip(lams, kernels):
                for i, pi in enumerate(p):
                    if q + i < n:
                        rho += lam * pi
            if rho <= 0:
                raise SystemExit(f"cannot repair q={q}")
            need = (-s) / rho
            if need > eta:
                eta = need
    # add a tiny extra 1/den_w
    eta += Fraction(1, den_w)
    w_rat = [[x + eta for x in row] for row in w_rat]
    sl = slacks(w_rat)
    if any(s < 0 for s in sl):
        raise SystemExit(f"covering still fails min={min(sl)}")

    energy = sum(lam * sum(x * x for x in w) for lam, w in zip(lams, w_rat))
    b = 1 + 2 * (energy / m - L)
    g2 = a * b
    gamma = math.sqrt(float(g2))
    print("eta", eta)
    print("min_slack", min(sl))
    print("a", a)
    print("b", b)
    print("ab", g2)
    print("gamma", gamma)
    print("hz_gamma0", HZ_GAMMA0)
    print("beats_hz_gamma0", gamma < HZ_GAMMA0)
    print("lt_0.94349259", g2 < Fraction(94349259, 100000000) ** 2)
    print("lt_0.9435", g2 < Fraction(9435, 10000) ** 2)

    cert = {
        "m": m,
        "L": L,
        "asymmetric": False,
        "eta": str(eta),
        "lambdas": [str(x) for x in lams],
        "kernels": [[str(x) for x in row] for row in kernels],
        "weights_left": [[str(x) for x in row] for row in w_rat],
        "weights_right": [[str(x) for x in row] for row in w_rat],
        "a": str(a),
        "b": str(b),
        "source_tag": "hz-kernels-L6-exact-a",
        "source_gamma_float": g_float,
    }
    out = ROOT / "certs" / "hz_kernels_L6.json"
    out.write_text(json.dumps(cert, indent=2) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
