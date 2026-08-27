#!/usr/bin/env python3
"""Independent checks of cert.json.

Does not re-solve the Lyapunov linear systems. Rebuilds F from the
stored coefficients, differentiates along the field, and checks the
identity through degree 8. Separately: Li Chengzhi polynomials,
resultant/discriminant equilibria, Jacobian at (0, 1), and the
exact five-cycle obstruction identities.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import sympy as sp

from field import (
    X,
    Y,
    five_cycle_obstructions,
    jacobian,
    l1_primitive,
    li_chengzhi,
    origin_linear_type,
    second_focus_linear_type,
    shi_field,
    unperturbed_equilibria,
)

HERE = Path(__file__).resolve().parent


def poly_from_mons(mons) -> sp.Expr:
    acc = 0
    for m in mons:
        acc += sp.Rational(m["num"], m["den"]) * X ** m["i"] * Y ** m["j"]
    return acc


def check_identity(cert) -> None:
    proved = cert["proved"]
    F = sum(poly_from_mons(mons) for mons in proved["F"].values())
    P, Q = shi_field(0, 0, 0, 0)
    dF = sp.expand(sp.diff(F, X) * P + sp.diff(F, Y) * Q)
    V3 = sp.Rational(proved["V3"]["num"], proved["V3"]["den"])
    V1 = sp.Rational(proved["V1"]["num"], proved["V1"]["den"])
    V2 = sp.Rational(proved["V2"]["num"], proved["V2"]["den"])
    assert V1 == 0 and V2 == 0
    assert V3 == sp.Rational(35625, 8)
    r2 = X**2 + Y**2
    target = V1 * r2**2 + V2 * r2**3 + V3 * r2**4
    rem = sp.expand(dF - target)
    low = sum(
        rem.coeff(X, i).coeff(Y, j) * X**i * Y**j
        for i in range(9)
        for j in range(9 - i)
    )
    if sp.expand(low) != 0:
        raise AssertionError(f"dF/dt identity fails, remainder {sp.expand(low)}")


def check_li(cert) -> None:
    L1, L2, L3 = li_chengzhi(-10, 5, 1, 1, -25)
    assert L1 == 0 and L2 == 0 and L3 == 57000
    V3 = sp.Rational(cert["proved"]["V3"]["num"], cert["proved"]["V3"]["den"])
    assert L3 / V3 == sp.Rational(64, 5)
    cc = cert["proved"]["li_chengzhi_crosscheck"]
    assert cc["L1"] == 0 and cc["L2"] == 0 and cc["L3"] == 57000
    assert cc["L3_over_V3"] == "64/5"


def check_equilibria(cert) -> None:
    eqs = unperturbed_equilibria()
    stored = cert["proved"]["equilibria"]
    assert stored["real_count"] == 2
    assert stored["complex_count"] == 2
    assert stored["second_branch_discriminant"] == -577500
    assert eqs["second_branch_discriminant"] == -577500
    P, Q = shi_field(0, 0, 0, 0)
    for pt, expected in (((0, 0), (0, 0)), ((0, 1), (0, 0))):
        valP = sp.expand(P.subs({X: pt[0], Y: pt[1]}))
        valQ = sp.expand(Q.subs({X: pt[0], Y: pt[1]}))
        assert (valP, valQ) == expected


def check_linear_types(cert) -> None:
    o = origin_linear_type()
    s = second_focus_linear_type()
    assert cert["proved"]["origin"]["type"] == "linear_center"
    assert cert["proved"]["second_focus"]["type"] == "strong_unstable_focus"
    assert o["charpoly"] == "t^2 + 1"
    assert s["charpoly"] == "t^2 - 5 t + 24"
    assert s["trace"] == 5 and s["det"] == 24 and s["disc"] == -71
    P, Q = shi_field(0, 0, 0, 0)
    J = jacobian(P, Q).subs({X: 0, Y: 1})
    assert J == sp.Matrix([[5, 1], [-24, 0]])


def check_obstructions(cert) -> None:
    facts = five_cycle_obstructions()
    stored = cert["five_cycle"]
    assert stored["mu_moves_second_equilibrium"]["L1_primitive_at_origin"] == "27 mu"
    assert facts["delta_minus_5_lambda_eps_0"]["second_det"] == -21
    assert stored["delta_minus_5_lambda_eps_0"]["second_type"] == "saddle"
    assert stored["circles_about_0_1_linear"]["amplitude_squared"] == 554
    # live identities
    assert l1_primitive(-10, 5, 1, 1, -25, 0) == 0
    assert l1_primitive(-10, 5, 1, 1, -25, 1) == 27
    L1, L2, L3 = li_chengzhi(-10, 0, 1, 1, 20)
    assert (L1, L2, L3) == (0, 0, 0)
    assert cert["status"] == "dropped"
    assert cert["published_Hn_moved"] is False
    assert cert["dropped_claim"] == "H(2) >= 5"
    assert cert["annulus"]["status"] == "residue"
    assert cert["annulus"]["certificate"] is None


def check_f_coeffs(cert) -> None:
    path = HERE / "f_coeffs.txt"
    text = path.read_text()
    F_from_file = {}
    Vs = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "F":
            deg, i, j, num, den = map(int, parts[1:])
            F_from_file.setdefault(deg, []).append(
                {"i": i, "j": j, "num": num, "den": den}
            )
        elif parts[0] == "V":
            k, num, den = map(int, parts[1:])
            Vs[k] = (num, den)
    assert Vs[1] == (0, 1) and Vs[2] == (0, 1) and Vs[3] == (35625, 8)
    for deg_s, mons in cert["proved"]["F"].items():
        deg = int(deg_s)
        file_mons = {(m["i"], m["j"]): (m["num"], m["den"]) for m in F_from_file[deg]}
        for m in mons:
            assert file_mons[(m["i"], m["j"])] == (m["num"], m["den"])


def main() -> int:
    cert_path = HERE / "cert.json"
    cert = json.loads(cert_path.read_text())
    check_identity(cert)
    check_li(cert)
    check_equilibria(cert)
    check_linear_types(cert)
    check_obstructions(cert)
    check_f_coeffs(cert)
    print("verify.py OK")
    print("  V1 = V2 = 0, V3 = 35625/8")
    print("  origin weak focus order 3; (0, 1) strong unstable focus")
    print("  H(2) >= 5 dropped; published H(n) not moved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
