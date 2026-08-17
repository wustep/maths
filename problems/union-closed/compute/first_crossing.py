"""First mean on the {b,1} ray at which the mix ratio drops below 1.

c(β) := inf { a + (1-a)b  :  ratio_β(a,b) < 1 }.
The claimed ray-constant is max_β c(β).

Independent C3 is used for the CIID term (it is the worse endpoint
on this ray).  Replayable: numpy mesh, no local solver.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

LN2 = math.log(2)


def h_np(p):
    p = np.asarray(p, dtype=np.float64)
    out = np.zeros_like(p)
    m = (p > 0.0) & (p < 1.0)
    q = 1.0 - p[m]
    out[m] = -(p[m] * np.log(p[m]) + q * np.log(q)) / LN2
    return out


def a_ex4_np(t):
    t = np.asarray(t, dtype=np.float64)
    out = np.zeros_like(t)
    out[t >= 0.5] = 1.0
    thresh = 1.0 - 1.0 / np.sqrt(2.0)
    mid = (t > thresh) & (t < 0.5)
    tm = t[mid]
    tb = 1.0 - tm
    num = 1.0 - 2.0 * tb * tb
    den = 2.0 * tm * tb
    out[mid] = np.sqrt(np.maximum(num, 0.0) / den)
    return out


def h_or_indep_np(s, t=None):
    if t is None:
        t = s
    return h_np(1.0 - (1.0 - s) * (1.0 - t))


def h_or_ex4_bb_np(b):
    # Π(b,b)(0,0) = b̄² + a(b)² (b̄ - b̄²)
    bb = 1.0 - b
    aa = a_ex4_np(b)
    pi0 = bb * bb + aa * aa * (bb - bb * bb)
    return h_np(1.0 - pi0)


def h_or_ex5_bb_np(b):
    bb = 1.0 - b
    # f(s̄)=s̄ s, Π= b̄² + (b̄ b)²
    pi0 = bb * bb + (bb * b) ** 2
    return h_np(1.0 - pi0)


def first_crossing(proto, n_b=4000, n_a=3000, betas=None):
    if betas is None:
        betas = np.linspace(0.0, 0.40, 161)
    b = np.linspace(0.02, 0.499, n_b)
    a = np.linspace(0.0, 0.499, n_a)
    B, A = np.meshgrid(b, a, indexing="ij")  # shapes (nb, na)
    mean = A + (1.0 - A) * B
    hb = h_np(b)[:, None]
    hid = h_or_indep_np(b)[:, None]
    if proto == "ex4":
        hp = h_or_ex4_bb_np(b)[:, None]
    else:
        hp = h_or_ex5_bb_np(b)[:, None]
    eh = (1.0 - A) * hb
    eiid = (1.0 - A) ** 2 * hid
    e_ind = (1.0 - A) ** 2 * hp
    e_cor = (1.0 - A) * hp
    ep = np.minimum(e_ind, e_cor)

    rows = []
    best = None
    for beta in betas:
        num = (1.0 - beta) * eiid + beta * ep
        # avoid eh=0
        ratio = np.divide(num, eh, out=np.full_like(num, 10.0), where=eh > 1e-16)
        bad = ratio < 1.0
        if not np.any(bad):
            c = float(mean.max())
            rows.append(dict(beta=float(beta), c=c, n_bad=0))
            continue
        c = float(mean[bad].min())
        # arg
        idx = np.argmin(np.where(bad, mean, 1e9))
        ib, ia = np.unravel_index(idx, mean.shape)
        rec = dict(
            beta=float(beta),
            c=c,
            a=float(A[ib, ia]),
            b=float(B[ib, ia]),
            mean=float(mean[ib, ia]),
            ratio=float(ratio[ib, ia]),
            n_bad=int(bad.sum()),
        )
        rows.append(rec)
        if best is None or rec["c"] > best["c"]:
            best = rec
        print(f"  β={beta:.4f}  c={c:.10f}  at b={rec.get('b',0):.5f} a={rec.get('a',0):.5f}",
              flush=True)
    return best, rows


def main():
    report = {}
    for proto in ("ex5", "ex4"):
        print("====", proto, flush=True)
        best, rows = first_crossing(proto)
        report[proto] = {"best": best, "curve": rows}
        print("BEST", proto, best, flush=True)

    # also a denser β scan around the winner
    print("==== ex4 dense", flush=True)
    betas = np.linspace(0.08, 0.28, 201)
    best, rows = first_crossing("ex4", n_b=5000, n_a=4000, betas=betas)
    report["ex4_dense"] = {"best": best, "curve": rows}
    print("BEST dense", best, flush=True)

    path = Path(__file__).resolve().parent / "first_crossing.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
