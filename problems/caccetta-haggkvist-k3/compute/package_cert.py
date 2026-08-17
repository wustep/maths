#!/usr/bin/env python3
"""Freeze the F₄ certificate at the clean threshold c=0.34645."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from verify_certificate import F_coords

HERE = Path(__file__).resolve().parent
src = json.loads((HERE / "certs" / "optimize_bound.json").read_text())
cert = src["certificate"]
C = 0.34645
Q = np.array(cert["Q"], dtype=float)
Q = 0.5 * (Q + Q.T)
coords = F_coords(C, Q, cert["b"], cert["cT"], cert["cV"], cert["d"])
ev = np.linalg.eigvalsh(Q)
out = {
    "c": C,
    "published_hkn": 0.3465,
    "personal_communication_3388": 0.3388,
    "method": (
        "F4 flag-algebra Farkas certificate: Q≽0 on the 8×8 β-flag "
        "Cauchy–Schwarz slices, plus out-regularity, order-3 induction, "
        "and the CSS-fork inequality. Matrices independently rebuilt in "
        "flags4.py / ind_fork.py and matched to Hladký–Král'–Norin "
        "Combinatorica 37 (2017) Tables 1–2 and (4.14)–(4.15)."
    ),
    "worst_F": float(coords.max()),
    "worst_index": int(np.argmax(coords)),
    "all_negative": bool(np.all(coords < 0)),
    "Q_min_eig": float(ev.min()),
    "b": cert["b"],
    "cT": cert["cT"],
    "cV": cert["cV"],
    "d": cert["d"],
    "Q": Q.tolist(),
    "F": coords.tolist(),
}
path = HERE / "certs" / "f4_certificate.json"
path.write_text(json.dumps(out, indent=2))
print(f"c={C} worst={coords.max():+.6f} mineig={ev.min():+.3e} -> {path}")
