#!/usr/bin/env python3
"""High-resolution float estimate of C_1. Not a bound."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent


def power_f(t, mu, alpha, beta):
    t = np.asarray(t, dtype=np.float64)
    return (1.0 + mu * np.power(np.maximum(t, 0.0), alpha)) ** (-beta)


def phi_raw(s, support, gamma, delta, eps, kappa):
    s = np.asarray(s, dtype=np.float64)
    out = np.zeros_like(s)
    mid = (s >= 0.0) & (s < support)
    r = np.clip(s[mid] / support, 0.0, 1.0)
    out[mid] = ((1.0 - r**gamma) ** delta) / ((1.0 + eps * s[mid]) ** kappa)
    out[s == 0.0] = 1.0
    return out


def estimate(params: dict, n_s: int = 20000, n_t: int = 16000, T: float = 1e8) -> dict:
    alpha = float(params["alpha"])
    beta = float(params["beta"])
    gamma = float(params["gamma"])
    delta = float(params["delta"])
    eps = float(params.get("eps", 1.0))
    kappa = float(params.get("kappa", 1.0))
    support = float(params.get("support", params.get("T", 1.0)))

    def h(u: float) -> float:
        return (1.0 + u**alpha) ** (-2.0 * beta)

    I_f, _ = quad(h, 0.0, np.inf, epsabs=1e-14, limit=500)
    mu = I_f**alpha

    s = np.linspace(0.0, support, n_s)
    raw = phi_raw(s, support, gamma, delta, eps, kappa)
    trap = np.trapezoid
    I_phi = trap(raw, s)
    phi = raw / I_phi
    a = float(trap(phi * phi, s))

    t = np.exp(np.linspace(math.log(1e-4), math.log(T), n_t))
    g = np.empty_like(t)
    for i, ti in enumerate(t):
        g[i] = float(trap(phi * power_f(s * ti, mu, alpha, beta), s))
    g = np.clip(g, 0.0, 1.0)
    integrand = (1.0 - g) ** 2 * np.power(t, -1.5)
    # near 0: 1-g ≤ β μ (S t)^α
    coef = beta * mu * support**alpha
    expo = 2.0 * alpha - 0.5
    near = (coef * coef) * (t[0] ** expo) / expo
    core = float(trap(integrand, t))
    tail = 2.0 * T ** (-0.5)
    I = near + core + tail
    C1 = math.sqrt(a) * 0.5 * I
    return {
        "mu": float(mu),
        "a": a,
        "C_1_float": C1,
        "C_1_core_only": math.sqrt(a) * 0.5 * core,
        "near": near,
        "tail": tail,
        "I": I,
        "L_over_Lcl_float": (9.0 * math.sqrt(3.0) / 4.0) * C1,
    }


def main() -> None:
    paper = {
        "alpha": 4.5,
        "beta": 0.25,
        "gamma": 0.36,
        "delta": 2.1,
        "eps": 1.0,
        "kappa": 1.0,
        "support": 1.0,
    }
    best = json.loads((HERE / "opt_best_A.json").read_text())["best"]["parameters"]
    best["support"] = best.get("T", best.get("support"))
    out = {"lemma11_second": estimate(paper), "opt_best_A": estimate(best)}
    dest = HERE / "float_c1.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    for k, v in out.items():
        print(f"{k}: C_1_float={v['C_1_float']:.12f}  L/Lcl={v['L_over_Lcl_float']:.9f}  "
              f"(not a bound)")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
