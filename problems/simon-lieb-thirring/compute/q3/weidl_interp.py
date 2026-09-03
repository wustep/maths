#!/usr/bin/env python3
"""Replay Weidl 1996 real-interpolation bound at gamma=1, with HLT L_{1/2,1}=1/2.

Weidl, Commun. Math. Phys. 178 (1996) 135–146 / arXiv:quant-ph/9504013,
Theorem 4 and (32)–(34). The paper used L_{1/2,1} ≤ ς(3)/3 < 1.005.
Hundertmark–Lieb–Thomas later proved L_{1/2,1}=1/2. This file plugs that
sharp endpoint into Weidl's interpolation between gamma=1/2 and gamma=3/2.

Not a bound on the CCR record: the Ky-Fan (1+N) factor makes C(1/2)>2,
so the converted ratio sits near 3.8, above CCR 1.44655.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from constants import CCR_L, FHJN_L, LCL_11, Q1_L

HERE = Path(__file__).resolve().parent
U0 = math.sqrt(2.0 / (2.0 + math.sqrt(3.0)))
TMAX = 1.0 - U0


def simpson(f, a: float, b: float, n: int = 200000) -> float:
    if n % 2:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        s += (4.0 if i % 2 else 2.0) * f(x)
    return s * h / 3.0


def theta_1_2(eta: float) -> float:
    return (2.0**eta) / (eta * (1.0 - eta) * (1.0 + eta))


def I0(eta: float) -> float:
    # t = 1-u, then t = s^{2/eta} regularizes t^{(eta-2)/2}.
    smax = TMAX ** (eta / 2.0)

    def f(s: float) -> float:
        t = 0.0 if s <= 0.0 else s ** (2.0 / eta)
        return (1.0 - t) * ((2.0 - t) ** ((eta - 1.0) / 2.0))

    return (2.0 / eta) * simpson(f, 0.0, smax, n=250000)


def I1(eta: float) -> float:
    def f(t: float) -> float:
        return (1.0 - t) * (t ** (eta / 2.0)) * ((2.0 - t) ** ((eta - 3.0) / 2.0))

    return simpson(f, 0.0, TMAX, n=250000)


def theta_half_three_half(eta: float) -> tuple[float, float, float]:
    a = (2.0 / 3.0) * math.sqrt(1.0 + 2.0 / math.sqrt(3.0))
    term1 = (a ** (1.0 - eta)) / (1.0 - eta)
    i0 = I0(eta)
    i1 = I1(eta)
    term2 = math.sqrt(0.5) * ((1.5) ** eta) * (i0 + (2.0 / 3.0) * i1)
    return term1 + term2, i0, i1


def M_eta(eta: float) -> tuple[float, float]:
    best = float("inf")
    nstar = None
    for k in range(1, 80):
        for n in (float(k), 1.0 / k):
            val = ((1.0 + n) ** (1.0 - eta)) * ((1.0 + 1.0 / n) ** eta)
            if val < best:
                best, nstar = val, n
    return best, nstar


def C_of_eta(eta: float) -> dict:
    th12 = theta_1_2(eta)
    th, i0, i1 = theta_half_three_half(eta)
    mval, nstar = M_eta(eta)
    den = math.sqrt((eta**eta) * ((1.0 - eta) ** (1.0 - eta)))
    c = (th12 / th) * mval / den
    return {
        "eta": eta,
        "gamma": 0.5 + eta,
        "C": c,
        "Theta_1_2": th12,
        "Theta_half_3half": th,
        "M": mval,
        "Nstar": nstar,
        "I0": i0,
        "I1": i1,
        "den": den,
    }


def L_starstar(eta: float, L_half: float = 0.5) -> dict:
    rec = C_of_eta(eta)
    # Weidl (33) with sharp L_{1/2,1}=1/2 and L_{3/2,1}=3/16.
    L = rec["C"] * (L_half ** (1.0 - eta)) * ((3.0 / 16.0) ** eta)
    Lcl = math.gamma(rec["gamma"] + 1.0) / (
        2.0 * math.sqrt(math.pi) * math.gamma(rec["gamma"] + 1.5)
    )
    naive = (L_half ** (1.0 - eta)) * ((3.0 / 16.0) ** eta)
    rec.update(
        {
            "L_starstar": L,
            "Lcl_gamma": Lcl,
            "ratio": L / Lcl,
            "naive_Hadamard_L": naive,
            "naive_ratio": naive / Lcl,
            "L_half_used": L_half,
        }
    )
    return rec


def main() -> int:
    rec = L_starstar(0.5)
    rec["beats_CCR"] = bool(rec["ratio"] < CCR_L)
    rec["beats_FHJN"] = bool(rec["ratio"] < FHJN_L)
    rec["beats_q1"] = bool(rec["ratio"] < Q1_L)
    rec["note"] = (
        "Weidl interpolation at gamma=1 with HLT L_{1/2,1}=1/2. "
        "Ky-Fan factor M(1/2)=2 forces C>2; the ratio is far above CCR 1.44655. "
        "The C=1 Hadamard envelope applies only to characteristic-function potentials "
        "(Weidl (23)), where it would read ~1.44287, still not a bound for general V."
    )
    dest = HERE / "certs" / "weidl_interp.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=2) + "\n")
    print("=== q3 Weidl interpolation (HLT endpoint) ===")
    print(f"C(1/2)           = {rec['C']:.6f}")
    print(f"M(1/2)           = {rec['M']:.6f}  (N*={rec['Nstar']})")
    print(f"L_1,1^{{**}}      = {rec['L_starstar']:.6f}")
    print(f"L/Lcl            = {rec['ratio']:.6f}")
    print(f"naive Hadamard   = {rec['naive_ratio']:.6f}  (characteristic V only)")
    print(f"CCR 1.44655 beat = {rec['beats_CCR']}")
    print(f"wrote {dest}")
    if rec["beats_CCR"]:
        raise SystemExit("unexpected: Weidl interpolation beat CCR — inspect")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
