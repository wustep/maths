#!/usr/bin/env python3
"""Independent dump of the stored F₄ F-coordinates at c=0.3464.

Loads Q, b, cT, cV, d from f4_or_new_certificate.json. Rebuilds the 8×8
AC slices from hkn_replay.ac_slices and 4Ψ(κ) from flags4.enumerate_labeled.
Does not import verify_q4_certificate.py.

Fork penalty is the CKLS-tightened HKN (4.7) form:
    4Ψ(κ) − 12(3c−1)²/0.8616.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

PARENT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PARENT))
from flags4 import enumerate_labeled, induced, type_of  # noqa: E402
from hkn_replay import AR, BR, ac_slices, indT_coeffs, indV_coeffs  # noqa: E402

KEEP = HERE / "certs" / "keep"
CERT = KEEP / "f4_or_new_certificate.json"
OUT = KEEP / "f_coords_0.3464.json"
CSS_BETA = 0.8616

# HKN (4.7): 4Ψ(κ) extras. Only these types have a fork among their four triples.
HKN_47 = {
    4: 1,
    7: 1,
    8: 3,
    12: 1,
    17: 1,
    19: 1,
    20: 2,
    21: 2,
    23: 1,
    25: 1,
    26: 1,
    29: 1,
    30: 2,
}


def is_induced_fork(sub) -> bool:
    for ctr in range(3):
        leaves = [i for i in range(3) if i != ctr]
        if (ctr, leaves[0]) not in sub or (ctr, leaves[1]) not in sub:
            continue
        if (leaves[0], leaves[1]) in sub or (leaves[1], leaves[0]) in sub:
            continue
        if (leaves[0], ctr) in sub or (leaves[1], ctr) in sub:
            continue
        return True
    return False


def kappa4_from_labeled() -> list[float]:
    """4Ψ(κ): average number of induced-fork triples on a labeled type-t 4-graph."""
    n_type = [0] * 32
    n_fork = [0] * 32
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        forks = sum(
            1
            for triple in itertools.combinations(range(4), 3)
            if is_induced_fork(induced(arcs, triple))
        )
        n_fork[t] += forks
    return [n_fork[t] / n_type[t] if n_type[t] else 0.0 for t in range(32)]


def fork_coeffs(c: float, kappa: list[float]) -> list[float]:
    penalty = 12.0 * (3.0 * c - 1.0) ** 2 / CSS_BETA
    return [kappa[k] - penalty for k in range(32)]


def main() -> None:
    blob = json.loads(CERT.read_text())
    cert = blob.get("certificate") or blob
    c = float(cert["c"])
    if abs(c - 0.3464) > 1e-12:
        raise SystemExit(f"expected c=0.3464, got {c}")
    Q = np.array(cert["Q"], dtype=float)
    Q = 0.5 * (Q + Q.T)
    b = np.array(cert["b"], dtype=float)
    cT = float(cert["cT"])
    cV = float(cert["cV"])
    d = float(cert["d"])

    ev = np.linalg.eigvalsh(Q)
    min_eig = float(ev.min())

    kappa = kappa4_from_labeled()
    pub = [float(HKN_47.get(k, 0)) for k in range(32)]
    if any(abs(kappa[k] - pub[k]) > 1e-12 for k in range(32)):
        raise SystemExit("FAIL: rebuilt 4Ψ(κ) does not match HKN (4.7) extras")

    MS = [np.array(M, dtype=float) for M in ac_slices()]
    sos = np.array([float(np.sum(Q * Mk)) for Mk in MS])
    AR_A = np.array(AR, dtype=float)
    BR_A = np.array(BR, dtype=float)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c, kappa))
    coords = sos + (b @ (BR_A - c * AR_A)) + cT * it + cV * iv + d * fk
    coords = coords.astype(float)
    worst_i = int(np.argmax(coords))
    worst = float(coords[worst_i])
    all_lt = bool(np.all(coords < -0.05))
    penalty = 12.0 * (3.0 * c - 1.0) ** 2 / CSS_BETA

    print(f"c={c}")
    print(f"min eig(Q)={min_eig:+.16e}")
    print("4Ψ(κ) matches HKN (4.7) extras: True")
    print(f"fork penalty 12*(3c-1)^2/{CSS_BETA}={penalty:.16f}")
    print("F-coords:")
    for k, val in enumerate(coords):
        print(f"  {k:2d}  {val:+.16e}")
    print(f"worst={worst:+.16e}  at r_{worst_i}")
    print(f"all F < -0.05? {all_lt}")

    payload = {
        "c": c,
        "css_beta": CSS_BETA,
        "source": str(CERT.relative_to(HERE)),
        "kappa4_matches_hkn_47": True,
        "kappa4": kappa,
        "fork_penalty": penalty,
        "Q_min_eig": min_eig,
        "F": coords.tolist(),
        "worst": worst,
        "worst_index": worst_i,
        "all_lt_minus_0.05": all_lt,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
