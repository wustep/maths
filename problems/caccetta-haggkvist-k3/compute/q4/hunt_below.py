#!/usr/bin/env python3
"""Hunt F₄ emptiness at c < 0.34640. Does not overwrite the stored 0.34640 cert."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from extra_forms import (  # noqa: E402
    CSS_BETA_CKLS,
    check_kappa4,
    compute_AC_eta,
    compute_beta_regularity,
    compute_eta_regularity,
    ind2_coeffs,
)
from hunt_threshold import (  # noqa: E402
    F_coords,
    build_regs,
    load_warm_Qs,
    rand_psd,
    refine_chol,
    try_lp,
    MS,
)

KEEP = HERE / "certs" / "keep"
STORED = KEEP / "f4_or_new_certificate.json"
OUT = KEEP / "hunt_below.json"
TRIAL = KEEP / "f4_below_trial.json"
# Tight reading of CKLS μ=0.16065 (1/(1+μ)≈0.861586). Published theorem is 0.8616.
CSS_MU = 1.0 / (1.0 + 0.16065)


def write_trial(c, hit, AC, css_beta, use_ex, tag):
    Qb = np.array(hit["Qb"], dtype=float)
    Qb = 0.5 * (Qb + Qb.T)
    w, V = np.linalg.eigh(Qb)
    if w.min() < -1e-8:
        return None
    Qb = (V * np.clip(w, 0, None)) @ V.T
    Qe = None if hit.get("Qe") is None else np.array(hit["Qe"], dtype=float)
    i2 = ind2_coeffs(c) if use_ex else None
    beta_reg = compute_beta_regularity()[:4]
    eta_reg = compute_eta_regularity()[:4]
    rg = build_regs(beta_reg, eta_reg, c) if use_ex else None
    coords = F_coords(
        c,
        Qb,
        hit["b"],
        hit["cT"],
        hit["cV"],
        hit["d"],
        Qe=Qe,
        AC=AC,
        css_beta=css_beta,
        ind2=i2,
        regs=rg,
        extra=hit.get("extra"),
    )
    if not np.all(coords < -1e-6):
        return None
    rec = {
        "c": c,
        "published_hkn": 0.3465,
        "stored_f4": 0.34640,
        "css_beta": css_beta,
        "tag": tag,
        "t": hit["t"],
        "worst_F": float(coords.max()),
        "worst_index": int(np.argmax(coords)),
        "Q_min_eig": float(np.linalg.eigvalsh(Qb).min()),
        "b": hit["b"],
        "cT": hit["cT"],
        "cV": hit["cV"],
        "d": hit["d"],
        "extra": hit.get("extra", []),
        "Q": Qb.tolist(),
        "Qe": None if Qe is None else Qe.tolist(),
        "F": coords.tolist(),
    }
    TRIAL.write_text(json.dumps(rec, indent=2))
    print("WROTE TRIAL", TRIAL, "c=", c, "worst=", coords.max(), flush=True)
    return rec


def main():
    ok_k, _ = check_kappa4()
    print("kappa4", ok_k, flush=True)
    AC, _ = compute_AC_eta()
    beta_reg = compute_beta_regularity()[:4]
    eta_reg = compute_eta_regularity()[:4]
    warms = load_warm_Qs()
    stored = json.loads(STORED.read_text())
    warms["stored_ckls"] = np.array(stored["Q"], dtype=float)
    print("warm", list(warms), "css_mu", CSS_MU, flush=True)

    targets = [0.34639, 0.34638, 0.34635]
    css_list = [CSS_BETA_CKLS, CSS_MU]
    rng = np.random.default_rng(21)
    n_try = 240
    scales = (8.0, 20.0, 40.0, 70.0, 100.0)
    best = {}
    found = None

    for c in targets:
        i2 = ind2_coeffs(c)
        hit = None
        for css_b in css_list:
            for use_ex in (False, True):
                regs = build_regs(beta_reg, eta_reg, c) if use_ex else None
                for qn, Qb in warms.items():
                    sos = np.array([float(np.sum(Qb * Mk)) for Mk in MS])
                    got = try_lp(
                        c,
                        sos,
                        css_beta=css_b,
                        ind2=i2 if use_ex else None,
                        regs=regs,
                    )
                    if got is None:
                        continue
                    rec = {**got, "kind": f"{qn}/css{css_b}/ex{use_ex}", "Qb": Qb.tolist(), "Qe": None}
                    if hit is None or rec["t"] < hit["t"]:
                        hit = rec
                    print(f"  c={c} {rec['kind']} t={got['t']:+.6f} ok={got['ok']}", flush=True)
                    if got["ok"] and found is None:
                        found = write_trial(c, rec, AC, css_b, use_ex, rec["kind"])

        Qb0 = warms["stored_ckls"]
        for i in range(n_try):
            scale = float(scales[i % len(scales)])
            lam = float(rng.random())
            Qb = lam * Qb0 + (1.0 - lam) * rand_psd(rng, 8, scale)
            Qe = rand_psd(rng, 9, 0.6 * scale) if i % 3 != 2 else np.zeros((9, 9))
            sos = np.array([float(np.sum(Qb * Mk)) for Mk in MS])
            sos = sos + np.einsum("ij,ijk->k", Qe, AC)
            for css_b, use_ex in ((CSS_BETA_CKLS, True), (CSS_MU, True), (CSS_BETA_CKLS, False)):
                regs = build_regs(beta_reg, eta_reg, c) if use_ex else None
                got = try_lp(c, sos, css_beta=css_b, ind2=i2 if use_ex else None, regs=regs)
                if got is None:
                    continue
                if hit is None or got["t"] < hit["t"]:
                    hit = {**got, "kind": f"mix#{i}/css{css_b}", "Qb": Qb.tolist(), "Qe": Qe.tolist()}
                    print(f"  c={c} {hit['kind']} t={got['t']:+.6f} ok={got['ok']}", flush=True)
                    if got["ok"] and (found is None or c < found["c"] - 1e-12):
                        found = write_trial(c, hit, AC, css_b, use_ex, hit["kind"])

        if hit is not None and "Qb" in hit:
            ref = refine_chol(
                c,
                np.array(hit["Qb"]),
                AC,
                Qe=None if hit.get("Qe") is None else np.array(hit["Qe"]),
                steps=16,
                css_beta=float(hit.get("css_beta", CSS_BETA_CKLS)),
                ind2=i2,
                regs=build_regs(beta_reg, eta_reg, c),
            )
            if ref is not None and (hit is None or ref["t"] < hit["t"]):
                hit = {**ref, "kind": hit.get("kind", "") + "+refine"}
                print(f"  c={c} refine t={ref['t']:+.6f} ok={ref['ok']}", flush=True)
                if ref["ok"] and (found is None or c < found["c"] - 1e-12):
                    found = write_trial(c, hit, AC, float(hit.get("css_beta", CSS_BETA_CKLS)), True, hit["kind"])

        best[str(c)] = None if hit is None else {k: hit[k] for k in hit if k not in ("Qb", "Qe", "Q")}
        print("BEST", c, None if hit is None else hit["t"], flush=True)

    rec = {
        "best_t_by_c": best,
        "css_mu": CSS_MU,
        "certificate": None if found is None else {k: found[k] for k in ("c", "t", "worst_F", "css_beta", "tag")},
        "note": "Did not overwrite f4_or_new_certificate.json.",
    }
    OUT.write_text(json.dumps(rec, indent=2))
    print("wrote", OUT, "found", None if found is None else found["c"])


if __name__ == "__main__":
    main()
