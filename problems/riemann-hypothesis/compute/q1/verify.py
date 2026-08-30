#!/usr/bin/env python3
"""Small independent replay for the first Riemann-hypothesis campaign.

This verifies exact parameter arithmetic, the printed 2011 Lehmer-pair
calculation, and the integrity and decisive lines of the fresh Arb logs.  It
does not turn the off-arXiv candidate into a published result or regenerate
its 3,149,013-row finite certificate.
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certificate.json"
FRESH = HERE / "fresh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def frac(text: str) -> Fraction:
    return Fraction(text)


def check_hashes(cert: dict) -> None:
    for name, expected in cert["fresh_logs"].items():
        path = FRESH / name
        require(path.is_file(), f"fresh log exists: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, f"fresh log hash: {name}")


def check_logs() -> None:
    for bits in (256, 512):
        prop = (FRESH / f"prop410_arb_{bits}.log").read_text()
        require(f"precision={bits}" in prop, f"Prop. 4.10 precision {bits}")
        require("TOTAL CHECKS: 31; FAILURES: 0" in prop, f"Prop. 4.10 checks at {bits} bits")
        require("RESULT: ALL ARB PROP410 CHECKS PASS" in prop, f"Prop. 4.10 result at {bits} bits")

        tail = (FRESH / f"tail_arb_{bits}.log").read_text()
        require(f"precision={bits}" in tail, f"tail precision {bits}")
        require("TOTAL CHECKS: 36; FAILURES: 0" in tail, f"tail checks at {bits} bits")
        require("RESULT: ALL ARB TAIL CHECKS PASS" in tail, f"tail result at {bits} bits")

    barrier = (FRESH / "barrier_target_closed.log").read_text()
    prisms = [line for line in barrier.splitlines() if line.startswith("Prism(")]
    indices = [int(re.match(r"Prism\((\d+)\)", line).group(1)) for line in prisms]
    require(indices == list(range(1, 884)), "barrier has 883 consecutive prisms")
    require(all(line.endswith(" PASS") for line in prisms), "every barrier prism passes")
    require("Closed coverage endpoint: [0.161250000000000000000000000000" in barrier,
            "barrier closes at t0=129/800")
    require("Rigorous winding interval: [+/- 8.95e-13]" in barrier,
            "barrier winding interval contains only integer zero")
    require("RESULT: CLOSED SLAB CERTIFIED" in barrier, "barrier replay result")

    margins = [Decimal(re.search(r"margin=\[([0-9.]+)", line).group(1)) for line in prisms]
    require(min(margins) > Decimal("0.5198"), "barrier minimum printed margin exceeds 0.5198")

    provenance = (FRESH / "storedsum_provenance.log").read_text()
    require("components: 7688" in provenance and "containment failures: 0" in provenance,
            "all 7,688 regenerated barrier components fit the stored balls")
    require("RESULT: STORED-SUM PROVENANCE PASS" in provenance, "stored-sum provenance result")

    taylor = (FRESH / "storedsum_taylor_tail.log").read_text()
    require("Taylor truncation upper = [1.954234593244761" in taylor,
            "factorial Taylor tail is below 2e-22")

    uniform = (FRESH / "uniform_error.log").read_text()
    require("uniform conservative error total < 0.00125" in uniform,
            "uniform barrier error is below its allowance")
    require("analytic justification at t=0 remains external" in uniform,
            "fresh log preserves its analytic scope note")

    singleton = (FRESH / "singleton_N690988.log").read_text().splitlines()
    canonical = [line for line in singleton if line.startswith(("TBOX ", "N "))]
    require(canonical == [
        "TBOX 16125/100000 16125/100000",
        "N 690988 L12 0.000000791366 GT089 0",
    ], "fresh finite producer matches the sealed first canonical row")


def check_exact_arithmetic(cert: dict) -> None:
    published = cert["published"]
    require(frac(published["rodgers_tao_lower"]) == 0, "Rodgers-Tao endpoint is zero")
    require(frac(published["platt_trudgian_upper"]) == Fraction(1, 5),
            "published upper endpoint is 1/5")

    row = published["table_row"]
    rounded_value = frac(row["t0"]) + frac(row["y0"]) ** 2 / 2
    require(rounded_value == frac(row["rounded_parameter_value"]),
            "printed Table 1 decimals give 0.19999966445 exactly")
    require(rounded_value < Fraction(1, 5), "printed decimal arithmetic lies below 0.2")
    height = published["platt_trudgian_height"]
    require(height - row["X"] // 2 == 500_175_235_371,
            "published verified height covers the rounded Table 1 X/2")

    candidate = cert["candidate"]
    value = frac(candidate["t0"]) + frac(candidate["y0_squared"]) / 2
    require(value == frac(candidate["claimed_upper"]),
            "candidate identity is 893927/5000000 = 0.1787854")
    require(value < Fraction(1, 5), "candidate target is below the published 0.2")
    require((2 * height - candidate["X"]) == 350_479_773,
            "published height exceeds candidate X/2 by 350479773/2")

    finite = candidate["finite_range"]
    expected_rows = finite["last_N"] - finite["first_N"] + 1
    require(expected_rows == finite["stored_rows_parsed"] == 3_149_013,
            "stored finite range has 3,149,013 consecutive indices")
    require(finite["fresh_singletons"] == [finite["first_N"]]
            and not finite["full_range_freshly_regenerated"],
            "fresh finite scope is exactly the first singleton")

    assembly = candidate["stored_assembly"]
    require(frac(assembly["finite_floor"]) - frac(assembly["finite_error_upper"])
            > frac(assembly["finite_margin_lower"]),
            "stored finite floor exceeds error by more than 557e-9")


def check_lehmer_pair(cert: dict) -> None:
    data = cert["lehmer_pair"]
    with localcontext() as ctx:
        ctx.prec = 80
        t_m1 = Decimal(data["t_k_minus_1"])
        t_0 = Decimal(data["t_k"])
        t_1 = Decimal(data["t_k_plus_1"])
        t_2 = Decimal(data["t_k_plus_2"])
        height = Decimal(data["verified_height_T"])
        x_m1, x_0, x_1, x_2 = (2 * v for v in (t_m1, t_0, t_1, t_2))
        pi = Decimal(
            "3.141592653589793238462643383279502884197169399375105820974944592307816406286"
        )
        g = (
            2 * x_1.ln() / (x_1 - x_2) ** 2
            + 2 * x_0.ln() / (x_0 - x_m1) ** 2
            + (x_0.ln() + x_1.ln()) * pi**2 / 12
            + Decimal("4e10") / (x_0 - 2 * height) ** 2
            + 4
        )
        delta_squared_g = (x_1 - x_0) ** 2 * g
        lam = (
            ctx.power(1 - Decimal(5) * delta_squared_g / 4, Decimal(4) / 5) - 1
        ) / (8 * g)

    require(Decimal("379.1994") < g < Decimal(data["printed_G_upper"]),
            "printed Lehmer data reproduce G < 379.1995")
    require(delta_squared_g < Decimal(data["printed_delta_squared_G_upper"]),
            "printed Lehmer data reproduce delta^2 G < 3.47471e-8")
    require(Decimal("-1.14542e-11") < lam < Decimal("-1.14540e-11"),
            "Lehmer formula reproduces -1.14541e-11")
    print(f"INFO: Lehmer replay G={g}")
    print(f"INFO: Lehmer replay lambda={lam}")


def main() -> None:
    cert = json.loads(CERT_PATH.read_text())
    require(cert["schema"] == "riemann-q1-v1", "certificate schema")
    check_exact_arithmetic(cert)
    check_hashes(cert)
    check_logs()
    check_lehmer_pair(cert)
    print("PASS riemann_hypothesis_q1_python")
    print("STATUS: published explicit window remains 0 <= Lambda <= 0.2")


if __name__ == "__main__":
    main()
