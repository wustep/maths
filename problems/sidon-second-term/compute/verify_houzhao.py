#!/usr/bin/env python3
"""Independent exact check of the Hou–Zhao eight-kernel Sidon certificate.

Reads the integer tables from the downloaded manuscript script (data only)
and re-implements covering, a, and b from arXiv:2607.01169v2 Lemma 2.1 /
equations (1)–(3). Does not import their checker and does not trust their
EXPECTED_* constants.

A pass means: the published rational data is a valid instance of Lemma 2.1
with sqrt(a*b) < 0.9435. It is not a new bound.
"""

from __future__ import annotations

import ast
import hashlib
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "refs" / "sidon_certificate_8kernel.py"
PAPER_SHA256 = "957a5afadd849ac4f97c2b71252abb5c796c2db3c91a608ab35097e3c49292a8"
TARGET = Fraction(9435, 10000) ** 2


def fail(msg: str) -> None:
    raise SystemExit("FAIL: " + msg)


def eval_const(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -eval_const(node.operand)
    if isinstance(node, ast.List):
        return [eval_const(x) for x in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(eval_const(x) for x in node.elts)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"F", "Fraction"}:
        args = [eval_const(a) for a in node.args]
        if len(args) == 1:
            return Fraction(args[0])
        if len(args) == 2:
            return Fraction(args[0], args[1])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        return eval_const(node.left) ** eval_const(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return eval_const(node.left) * eval_const(node.right)
    return ast.literal_eval(node)


def load_data(path: Path) -> dict:
    tree = ast.parse(path.read_text())
    out: dict = {}
    wanted = {"m", "L", "n", "R"}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0]
            if isinstance(name, ast.Name) and (name.id.isupper() or name.id in wanted):
                try:
                    out[name.id] = eval_const(node.value)
                except (ValueError, KeyError):
                    continue
    return out


def symmetric(half, den: int) -> list[Fraction]:
    vals = [Fraction(x, den) for x in half]
    return vals + list(reversed(vals))


def cover_one(lam, p, w, q: int, n: int) -> Fraction:
    total = Fraction(0)
    m = len(p)
    for i, pi in enumerate(p):
        j = q + i
        total += lam * pi * (w[j] if j < n else Fraction(1))
    return total


def main() -> None:
    raw = SRC.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PAPER_SHA256:
        fail(f"unexpected 8-kernel file hash {digest}")

    D = load_data(SRC)
    m = D["m"]
    L = D["L"]
    n = m * L

    lambdas = [Fraction(x, D["DL"]) for x in D["LAMBDA_INTS"]]
    if any(x <= 0 for x in lambdas):
        fail("a mixing weight is not positive")
    if sum(lambdas) != 1:
        fail(f"mixing weights sum to {sum(lambdas)}, not 1")

    kernels = [
        symmetric(D["P1_HALF_INTS"], D["DP"]),
        [Fraction(1, m)] * m,
        symmetric(D["P3_HALF_INTS"], D["DP"]),
        symmetric(D["P4_HALF_INTS"], D["DP"]),
        symmetric(D["P5_HALF_INTS"], D["DP"]),
        symmetric(D["P6_HALF_INTS"], D["DP"]),
        symmetric(D["P7_HALF_INTS"], D["DP"]),
        symmetric(D["P8_HALF_INTS"], D["DP"]),
    ]
    eta = D["ETA"]
    if not isinstance(eta, Fraction):
        eta = Fraction(eta)
    weight_keys = [f"W{i}_INTS" for i in range(1, 9)]
    weights = [[Fraction(x, D["DQ"]) + eta for x in D[k]] for k in weight_keys]

    if len(lambdas) != 8 or len(kernels) != 8 or len(weights) != 8:
        fail("expected R=8")
    for r, p in enumerate(kernels):
        if len(p) != m:
            fail(f"kernel {r} length")
        if any(x < 0 for x in p):
            fail(f"kernel {r} negative")
        if sum(p) != 1:
            fail(f"kernel {r} mass {sum(p)}")
        if p != list(reversed(p)):
            fail(f"kernel {r} not symmetric")
    for r, w in enumerate(weights):
        if len(w) != n:
            fail(f"weights {r} length {len(w)}")

    slacks: list[Fraction] = []
    for q in range(n + 1):
        slacks.append(
            sum(cover_one(lam, p, w, q, n) for lam, p, w in zip(lambdas, kernels, weights))
            - 1
        )
    if any(s < 0 for s in slacks):
        bad = min(range(len(slacks)), key=lambda q: slacks[q])
        fail(f"covering failed at q={bad} slack={slacks[bad]}")

    a = Fraction(m) * sum(
        lam * sum(x * x for x in p) for lam, p in zip(lambdas, kernels)
    )
    b = 1 + 2 * (
        Fraction(1, m)
        * sum(lam * sum(x * x for x in w) for lam, w in zip(lambdas, weights))
        - L
    )
    if b <= 0:
        fail(f"b={b} is not positive")
    c2 = a * b
    if c2 >= TARGET:
        fail(f"ab={c2} is not < (0.9435)^2")

    # Decimal is display only.
    gamma = math.sqrt(float(c2))
    least_pos = min(s for s in slacks if s > 0)
    print("source", SRC)
    print("sha256", digest)
    print("matches_paper_hash", digest == PAPER_SHA256)
    print("R", 8, "m", m, "L", L)
    print("min_slack", min(slacks))
    print("least_positive_slack", least_pos)
    print("a", a)
    print("b", b)
    print("ab", c2)
    print("gamma_float", gamma)
    print("certified_gamma_lt", "0.9435")
    print("PASS")


if __name__ == "__main__":
    main()
