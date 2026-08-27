#!/usr/bin/env python3
"""Replay published Lieb–Thirring comparison constants. Not a new bound."""

from __future__ import annotations

import json
import math
from pathlib import Path

# Frank–Hundertmark–Jex–Nam, JEMS 23 (2021) / arXiv:1808.09017, Theorem 1.
FHJN_RATIO = 1.456
FHJN_FINER = 1.455786
# One-bound-state / classical ratio at (γ, d) = (1, 1). Lieb–Thirring conjecture.
ONE_OVER_CL_1D_GAMMA1 = 2 / math.sqrt(3)


def l_classical(gamma: float, d: int) -> float:
    """Lcl(γ,d) = 2^{-d} π^{-d/2} Γ(γ+1) / Γ(γ+1+d/2)."""
    return (
        (2.0 ** -d)
        * (math.pi ** (-0.5 * d))
        * math.gamma(gamma + 1.0)
        / math.gamma(gamma + 1.0 + 0.5 * d)
    )


def sech_power_integral(p: float) -> float:
    """∫ sech^p(x) dx over R, p>0, equals √π Γ(p/2) / Γ((p+1)/2)."""
    return math.sqrt(math.pi) * math.gamma(p / 2.0) / math.gamma((p + 1.0) / 2.0)


def poschl_teller_ratio(nu: int, gamma: float) -> dict:
    """Exact bound-state ratio for V = −ν(ν+1) sech² on L²(R).

    Eigenvalues E_n = −(ν−n)² for n = 0, …, ν−1. The ratio
    (sum |E_n|^γ) / ∫ V_−^{γ+1/2} is a lower bound on L(γ,1).
    """
    if nu < 1:
        raise ValueError("nu >= 1")
    energies = [(nu - n) ** 2 for n in range(nu)]
    moment = sum(e**gamma for e in energies)
    amp = float(nu * (nu + 1))
    integ = (amp ** (gamma + 0.5)) * sech_power_integral(2.0 * gamma + 1.0)
    return {
        "nu": nu,
        "gamma": gamma,
        "n_bound": nu,
        "moment": moment,
        "integral": integ,
        "ratio": moment / integ,
        "ratio_over_classical": (moment / integ) / l_classical(gamma, 1),
    }


def build_record() -> dict:
    lcl_11 = l_classical(1.0, 1)
    lcl_32_1 = l_classical(1.5, 1)
    witnesses = [poschl_teller_ratio(nu, 1.0) for nu in (1, 2, 3, 4)]
    witnesses += [poschl_teller_ratio(nu, 1.25) for nu in (1, 2, 3)]
    return {
        "classical": {
            "formula": "2^{-d} pi^{-d/2} Gamma(gamma+1)/Gamma(gamma+1+d/2)",
            "Lcl_1_1": lcl_11,
            "Lcl_1_1_closed": "2/(3pi)",
            "Lcl_1_1_closed_value": 2.0 / (3.0 * math.pi),
            "Lcl_3_2_1": lcl_32_1,
            "Lcl_3_2_1_closed": "3/16",
            "Lcl_3_2_1_closed_value": 3.0 / 16.0,
            "Lcl_1_3": l_classical(1.0, 3),
        },
        "published": {
            "fhjn_theorem_1_ratio": FHJN_RATIO,
            "fhjn_finer_ratio": FHJN_FINER,
            "one_bound_state_over_classical_1d_gamma1": ONE_OVER_CL_1D_GAMMA1,
            "citation": "Frank–Hundertmark–Jex–Nam, arXiv:1808.09017 / JEMS 23 (2021)",
        },
        "sech2_witnesses": witnesses,
        "note": (
            "Witness ratios are lower bounds on L(gamma,1), not upper bounds. "
            "They do not improve 1.456."
        ),
    }


def verify(record: dict, atol: float = 1e-12) -> list[str]:
    errors = []
    cl = record["classical"]
    if abs(cl["Lcl_1_1"] - cl["Lcl_1_1_closed_value"]) > atol:
        errors.append("Lcl(1,1) != 2/(3pi)")
    if abs(cl["Lcl_3_2_1"] - cl["Lcl_3_2_1_closed_value"]) > atol:
        errors.append("Lcl(3/2,1) != 3/16")
    pub = record["published"]
    if abs(pub["one_bound_state_over_classical_1d_gamma1"] - 2 / math.sqrt(3)) > atol:
        errors.append("2/sqrt(3) mismatch")
    if not (1.1547 < pub["one_bound_state_over_classical_1d_gamma1"] < 1.1548):
        errors.append("2/sqrt(3) not in the printed window")
    if pub["fhjn_finer_ratio"] >= pub["fhjn_theorem_1_ratio"]:
        errors.append("finer ratio should be < 1.456")
    if pub["one_bound_state_over_classical_1d_gamma1"] >= pub["fhjn_theorem_1_ratio"]:
        errors.append("conjectured 2/sqrt(3) should sit below 1.456")
    for w in record["sech2_witnesses"]:
        if w["ratio_over_classical"] >= FHJN_RATIO:
            errors.append(f"sech2 nu={w['nu']} gamma={w['gamma']} exceeds 1.456")
        if w["ratio_over_classical"] <= 0:
            errors.append(f"non-positive witness nu={w['nu']}")
    return errors


def main() -> None:
    here = Path(__file__).resolve().parent
    record = build_record()
    out = here / "record.json"
    out.write_text(json.dumps(record, indent=2) + "\n")
    errors = verify(record)
    print(f"wrote {out}")
    print(f"Lcl(1,1) = {record['classical']['Lcl_1_1']:.12f} (2/(3pi))")
    print(f"Lcl(3/2,1) = {record['classical']['Lcl_3_2_1']:.12f} (3/16)")
    print(f"2/sqrt(3) = {record['published']['one_bound_state_over_classical_1d_gamma1']:.12f}")
    print(f"FHJN Theorem 1 ratio = {FHJN_RATIO}")
    for w in record["sech2_witnesses"]:
        print(
            f"  sech2 nu={w['nu']} gamma={w['gamma']}: "
            f"ratio/Lcl = {w['ratio_over_classical']:.6f}"
        )
    if errors:
        print("VERIFY FAIL:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)
    print("VERIFY OK")


if __name__ == "__main__":
    main()
