#!/usr/bin/env python3
"""Evaluate the stored CKLS-fork F₄ ray at c below 0.34640.

Does not overwrite f4_or_new_certificate.json. Writes scan_stored_c.json.
A stored ray that stays strictly negative at a smaller c is a new certificate
only after verify_q4_certificate.py accepts a written file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PARENT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(HERE))
from extra_forms import fork_coeffs as fork_coeffs_css  # noqa: E402
from hkn_replay import AR, BR, ac_slices, indT_coeffs, indV_coeffs  # noqa: E402
from hunt_threshold import try_lp  # noqa: E402

KEEP = HERE / "certs" / "keep"
CERT = KEEP / "f4_or_new_certificate.json"
OUT = KEEP / "scan_stored_c.json"
MARGIN = 0.05


def F_at(c, Q, b, cT, cV, d, css_beta, MS, AR_A, BR_A):
    sos = np.array([float(np.sum(Q * Mk)) for Mk in MS])
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs_css(c, css_beta))
    return sos + (np.array(b) @ (BR_A - c * AR_A)) + cT * it + cV * iv + d * fk


def main():
    cert = json.loads(CERT.read_text())
    Q = 0.5 * (np.array(cert["Q"], dtype=float) + np.array(cert["Q"], dtype=float).T)
    b = cert["b"]
    cT = float(cert["cT"])
    cV = float(cert["cV"])
    d = float(cert["d"])
    css_beta = float(cert["css_beta"])
    MS = [np.array(M, dtype=float) for M in ac_slices()]
    AR_A = np.array(AR, dtype=float)
    BR_A = np.array(BR, dtype=float)
    ev = float(np.linalg.eigvalsh(Q).min())
    sos = np.array([float(np.sum(Q * Mk)) for Mk in MS])

    targets = [
        0.34640,
        0.34639,
        0.34638,
        0.34637,
        0.34636,
        0.34635,
        0.34634,
        0.34633,
        0.34632,
        0.34631,
        0.34630,
        0.34625,
        0.34620,
        0.34610,
        0.34600,
    ]
    rows = []
    best_stored = None
    best_refit = None
    for c in targets:
        coords = F_at(c, Q, b, cT, cV, d, css_beta, MS, AR_A, BR_A)
        worst = float(coords.max())
        idx = int(np.argmax(coords))
        stored_ok = bool(np.all(coords < -MARGIN) and ev >= -1e-8)
        got = try_lp(c, sos, css_beta=css_beta)
        refit = None if got is None else {
            "t": got["t"],
            "ok": got["ok"],
            "cT": got["cT"],
            "cV": got["cV"],
            "d": got["d"],
        }
        rec = {
            "c": c,
            "stored_worst_F": worst,
            "stored_worst_index": idx,
            "stored_ok_margin_0.05": stored_ok,
            "refit": refit,
        }
        rows.append(rec)
        refit_t = "None" if got is None else f"{got['t']:+.6f}"
        refit_ok = None if got is None else got["ok"]
        print(
            f"c={c:.5f} stored_worst={worst:+.6f} ok={stored_ok} "
            f"refit_t={refit_t} refit_ok={refit_ok}",
            flush=True,
        )
        if stored_ok:
            best_stored = c
        if got is not None and got["ok"]:
            best_refit = c

    out = {
        "source": str(CERT.name),
        "css_beta": css_beta,
        "Q_min_eig": ev,
        "margin": MARGIN,
        "best_stored_ok": best_stored,
        "best_refit_ok": best_refit,
        "rows": rows,
        "note": (
            "stored_ok means the same (Q,b,cT,cV,d) ray stays below -0.05. "
            "refit_ok means HiGHS finds some linear multipliers on the same Q. "
            "Neither overwrites the stored 0.34640 certificate."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2))
    print("wrote", OUT, "best_stored", best_stored, "best_refit", best_refit)


if __name__ == "__main__":
    main()
