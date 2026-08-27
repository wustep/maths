#!/usr/bin/env python3
"""Hunt a flag-algebra c < 0.34645 on the rebuilt F₄ system plus extras.

Line 1: longer random-PSD + HiGHS on β and η SOS (extends the q3 9×9 block).
Line 2: extra F₄ linear forms rebuilt from flags4.enumerate_labeled:
  - Lemma 4.4 order-2 sink induction
  - β- and η-rooted out-regularity identities
  - CKLS 2015 CSS tighten of the fork penalty (published β<0.8616γ)

A certificate needs every F-coordinate strictly negative and Q ≽ 0.
Saturation at the old threshold is leftover, not a numerical dent.
Do not treat 0.3388 as published.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

PARENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PARENT))
from flags4 import induced, type_of, enumerate_labeled  # noqa: E402
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs  # noqa: E402
from optimize_bound import Q_from_as  # noqa: E402
from hkn_replay import A_VECS  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from extra_forms import (  # noqa: E402
    CSS_BETA_CKLS,
    CSS_BETA_DHP,
    CSS_BETA_HKN,
    check_kappa4,
    compute_AC_eta,
    compute_beta_regularity,
    compute_eta_regularity,
    fork_coeffs as fork_coeffs_css,
    ind2_coeffs,
)

# extra_forms.sos_eta is named below if missing
KEEP = HERE / "certs" / "keep"

ETA_FLAGS = [(a, b) for a in (0, 1, 2) for b in (0, 1, 2)]

AR_A = np.array(AR, dtype=float)
BR_A = np.array(BR, dtype=float)
MS = [np.array(M, dtype=float) for M in ac_slices()]


def sos_eta(Qe, AC):
    return np.einsum("ij,ijk->k", Qe, AC)


def load_warm_Qs():
    out = {"hkn": Q_from_as(A_VECS)}
    opt = PARENT / "certs" / "optimize_bound.json"
    sdp = PARENT / "certs" / "sdp_bound.json"
    if opt.exists():
        blob = json.loads(opt.read_text())
        cert = blob.get("certificate") or blob
        if "Q" in cert:
            out["optimize"] = np.array(cert["Q"], dtype=float)
    if sdp.exists():
        blob = json.loads(sdp.read_text())
        cert = blob.get("certificate") or blob
        if "Q" in cert:
            Q = np.array(cert["Q"], dtype=float)
            Q = 0.5 * (Q + Q.T)
            w, V = np.linalg.eigh(Q)
            out["sdp"] = (V * np.clip(w, 0, None)) @ V.T + 1e-8 * np.eye(8)
    return out


def try_lp(c, sos, *, css_beta=CSS_BETA_HKN, ind2=None, regs=None, eps=1e-6):
    """Min t s.t. sos + linear ≤ t. regs is a list of (coeff_32, free_bool)."""
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    if abs(css_beta - 1.0) < 1e-15:
        fk = np.array(fork_coeffs(c))
    else:
        fk = np.array(fork_coeffs_css(c, css_beta))
    extras = []
    if ind2 is not None:
        extras.append((np.array(ind2, dtype=float), False))  # ≥0 multiplier
    if regs:
        extras.extend(regs)
    n_ex = len(extras)
    nvar = 1 + 14 + 3 + n_ex
    A_ub = np.zeros((32, nvar))
    b_ub = np.zeros(32)
    for k in range(32):
        A_ub[k, 0] = -1.0
        for i in range(14):
            A_ub[k, 1 + i] = BR_A[i, k] - c * AR_A[i, k]
        A_ub[k, 15] = it[k]
        A_ub[k, 16] = iv[k]
        A_ub[k, 17] = fk[k]
        for j, (row, _) in enumerate(extras):
            A_ub[k, 18 + j] = row[k]
        b_ub[k] = -sos[k]
    bounds = [(None, None)] + [(None, None)] * 14 + [(0, None)] * 3
    bounds += [(None, None) if free else (0, None) for _, free in extras]
    cobj = np.zeros(nvar)
    cobj[0] = 1.0
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        return None
    t = float(res.x[0])
    return {
        "t": t,
        "b": res.x[1:15].tolist(),
        "cT": float(res.x[15]),
        "cV": float(res.x[16]),
        "d": float(res.x[17]),
        "extra": res.x[18:].tolist() if n_ex else [],
        "ok": t < -eps,
        "css_beta": css_beta,
    }


def F_coords(c, Qb, b, cT, cV, d, *, Qe=None, AC=None, css_beta=1.0, ind2=None, regs=None, extra=None):
    sos = np.array([float(np.sum(Qb * Mk)) for Mk in MS])
    if Qe is not None and AC is not None:
        sos = sos + sos_eta(Qe, AC)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c) if abs(css_beta - 1.0) < 1e-15 else fork_coeffs_css(c, css_beta))
    out = sos + (np.array(b) @ (BR_A - c * AR_A)) + cT * it + cV * iv + d * fk
    if extra:
        rows = []
        if ind2 is not None:
            rows.append(np.array(ind2, dtype=float))
        if regs:
            rows.extend(r for r, _ in regs)
        for coeff, row in zip(extra, rows):
            out = out + coeff * row
    return out


def rand_psd(rng, dim, scale=20.0):
    rnk = int(rng.integers(1, dim + 1))
    A = rng.normal(scale=scale, size=(dim, rnk))
    return A @ A.T


def pack_chol(x, dim):
    L = np.zeros((dim, dim))
    idx = 0
    for i in range(dim):
        for j in range(i + 1):
            L[i, j] = x[idx]
            idx += 1
    return L


def unpack_chol(L):
    out = []
    for i in range(L.shape[0]):
        for j in range(i + 1):
            out.append(L[i, j])
    return np.array(out)


def chol_of_psd(Q):
    Q = 0.5 * (Q + Q.T)
    w, V = np.linalg.eigh(Q)
    Qp = (V * np.clip(w, 0, None)) @ V.T
    dim = Q.shape[0]
    try:
        return np.linalg.cholesky(Qp + 1e-12 * np.eye(dim))
    except np.linalg.LinAlgError:
        return np.linalg.cholesky(Qp + 1e-8 * np.eye(dim))


def refine_chol(c, Qb, AC, *, Qe=None, steps=20, css_beta=1.0, ind2=None, regs=None):
    dim = 8
    L = chol_of_psd(np.array(Qb))
    x = unpack_chol(L)
    Qe = None if Qe is None else np.array(Qe)
    xe = None if Qe is None else unpack_chol(chol_of_psd(Qe))
    best_Qb = np.array(Qb)
    best_Qe = None if Qe is None else np.array(Qe)
    sos = np.array([float(np.sum(best_Qb * Mk)) for Mk in MS])
    if best_Qe is not None:
        sos = sos + sos_eta(best_Qe, AC)
    best = try_lp(c, sos, css_beta=css_beta, ind2=ind2, regs=regs)
    if best is None:
        return None
    scale = 4.0
    rng = np.random.default_rng(11)
    for _ in range(steps):
        improved = False
        order = rng.permutation(len(x))
        for j in order:
            for sgn in (+1.0, -1.0):
                trial = x.copy()
                trial[j] += sgn * scale
                Qt = pack_chol(trial, dim) @ pack_chol(trial, dim).T
                sos = np.array([float(np.sum(Qt * Mk)) for Mk in MS])
                if best_Qe is not None:
                    sos = sos + sos_eta(best_Qe, AC)
                got = try_lp(c, sos, css_beta=css_beta, ind2=ind2, regs=regs)
                if got is not None and got["t"] < best["t"] - 1e-9:
                    x = trial
                    best = {**got, "Qb": Qt.tolist(), "Qe": None if best_Qe is None else best_Qe.tolist()}
                    best_Qb = Qt
                    improved = True
                    break
        if xe is not None:
            eorder = rng.permutation(len(xe))
            for j in eorder:
                for sgn in (+1.0, -1.0):
                    trial = xe.copy()
                    trial[j] += sgn * scale
                    Qet = pack_chol(trial, 9) @ pack_chol(trial, 9).T
                    sos = np.array([float(np.sum(best_Qb * Mk)) for Mk in MS]) + sos_eta(Qet, AC)
                    got = try_lp(c, sos, css_beta=css_beta, ind2=ind2, regs=regs)
                    if got is not None and got["t"] < best["t"] - 1e-9:
                        xe = trial
                        best_Qe = Qet
                        best = {**got, "Qb": best_Qb.tolist(), "Qe": Qet.tolist()}
                        improved = True
                        break
        if not improved:
            scale *= 0.5
            if scale < 5e-4:
                break
    best["Qb"] = best_Qb.tolist()
    best["Qe"] = None if best_Qe is None else best_Qe.tolist()
    return best


def build_regs(beta_reg, eta_reg, c):
    regs = []
    if beta_reg is not None:
        ar1, br1, ar2, br2 = beta_reg
        for i in range(8):
            regs.append((br1[i] - c * ar1[i], True))
            regs.append((br2[i] - c * ar2[i], True))
    if eta_reg is not None:
        ar1, br1, ar2, br2 = eta_reg
        for i in range(9):
            regs.append((br1[i] - c * ar1[i], True))
            regs.append((br2[i] - c * ar2[i], True))
    return regs


def maybe_write_cert(c, hit, AC, css_beta, ind2, regs, tag):
    if hit is None or not hit.get("ok"):
        return None
    Qb = np.array(hit.get("Qb") if "Qb" in hit else hit.get("Q"), dtype=float)
    Qb = 0.5 * (Qb + Qb.T)
    w, V = np.linalg.eigh(Qb)
    if w.min() < -1e-8:
        return None
    Qb = (V * np.clip(w, 0, None)) @ V.T
    Qe = hit.get("Qe")
    Qe = None if Qe is None else np.array(Qe, dtype=float)
    if Qe is not None:
        Qe = 0.5 * (Qe + Qe.T)
        we, Ve = np.linalg.eigh(Qe)
        if we.min() < -1e-8:
            return None
        Qe = (Ve * np.clip(we, 0, None)) @ Ve.T
    i2 = None if ind2 is None else ind2_coeffs(c)
    rg = None if regs is None else build_regs(*regs, c) if isinstance(regs, tuple) else regs
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
    ev = np.linalg.eigvalsh(Qb)
    rec = {
        "c": c,
        "published_hkn": 0.3465,
        "stored_f4": 0.34645,
        "personal_communication_3388": 0.3388,
        "tag": tag,
        "t": hit["t"],
        "worst_F": float(coords.max()),
        "worst_index": int(np.argmax(coords)),
        "all_negative": True,
        "Q_min_eig": float(ev.min()),
        "css_beta": css_beta,
        "b": hit["b"],
        "cT": hit["cT"],
        "cV": hit["cV"],
        "d": hit["d"],
        "extra": hit.get("extra", []),
        "Q": Qb.tolist(),
        "Qe": None if Qe is None else Qe.tolist(),
        "F": coords.tolist(),
        "method": tag,
    }
    KEEP.mkdir(parents=True, exist_ok=True)
    path = KEEP / "f4_or_new_certificate.json"
    path.write_text(json.dumps(rec, indent=2))
    print("WROTE CERT", path, "c=", c, "worst=", coords.max(), "mineig=", ev.min(), flush=True)
    return rec


def main():
    ok_k, kap = check_kappa4()
    print("kappa4 matches HKN (4.7)?", ok_k, flush=True)
    if not ok_k:
        print("kappa mismatch", kap)
        sys.exit(2)

    print("building extra forms ...", flush=True)
    AC, n_type = compute_AC_eta()
    beta_reg = compute_beta_regularity()[:4]
    eta_reg = compute_eta_regularity()[:4]
    warms = load_warm_Qs()
    print("warm Qs", list(warms), "eta AC", AC.shape, flush=True)

    targets = [0.34645, 0.34644, 0.34640, 0.3460, 0.340, 0.3388]
    configs = [
        ("hkn-Q", CSS_BETA_HKN, False, False, False),
        ("hkn-Q+ckls-fork", CSS_BETA_CKLS, False, False, False),
        ("hkn-Q+dhp-fork", CSS_BETA_DHP, False, False, False),
        ("hkn-Q+ind2", CSS_BETA_HKN, True, False, False),
        ("hkn-Q+ckls+ind2", CSS_BETA_CKLS, True, False, False),
        ("hkn-Q+ckls+ind2+breg", CSS_BETA_CKLS, True, True, False),
        ("hkn-Q+ckls+ind2+allreg", CSS_BETA_CKLS, True, True, True),
        ("all-lin-hkn-fork", CSS_BETA_HKN, True, True, True),
    ]

    best = {}
    n_try = 160
    rng = np.random.default_rng(4)
    scales = (8.0, 20.0, 40.0, 70.0)
    Qb0 = warms["hkn"]
    found_cert = None

    for c in targets:
        i2 = ind2_coeffs(c)
        hit = None
        # deterministic linear extras on warm Qs
        for name, css_b, use_i2, use_br, use_er in configs:
            regs = build_regs(beta_reg if use_br else None, eta_reg if use_er else None, c)
            for qn, Qb in warms.items():
                sos = np.array([float(np.sum(Qb * Mk)) for Mk in MS])
                got = try_lp(
                    c,
                    sos,
                    css_beta=css_b,
                    ind2=i2 if use_i2 else None,
                    regs=regs or None,
                )
                if got is None:
                    continue
                rec = {
                    **got,
                    "kind": f"{name}/{qn}",
                    "Qb": Qb.tolist(),
                    "Qe": None,
                }
                if hit is None or rec["t"] < hit["t"]:
                    hit = rec
                print(f"  c={c} {name}/{qn} t={got['t']:+.6f} ok={got['ok']}", flush=True)
                if got["ok"] and found_cert is None:
                    found_cert = maybe_write_cert(
                        c,
                        rec,
                        AC,
                        css_b,
                        i2 if use_i2 else None,
                        (beta_reg if use_br else None, eta_reg if use_er else None),
                        f"{name}/{qn}",
                    )

        # random PSD + HiGHS, with and without extras
        for i in range(n_try):
            scale = float(scales[i % len(scales)])
            Qbase = warms["sdp"] if (i % 5 == 0 and "sdp" in warms) else Qb0
            lam = float(rng.random())
            Qb = lam * Qbase + (1.0 - lam) * rand_psd(rng, 8, scale)
            Qe = rand_psd(rng, 9, 0.6 * scale) if i % 3 != 2 else np.zeros((9, 9))
            sos = np.array([float(np.sum(Qb * Mk)) for Mk in MS]) + sos_eta(Qe, AC)
            # two LPs: HKN linear, and CKLS+ind2+regs
            for css_b, use_ex, tag in (
                (CSS_BETA_HKN, False, "mixed-hkn"),
                (CSS_BETA_CKLS, True, "mixed-ckls"),
            ):
                regs = build_regs(beta_reg, eta_reg, c) if use_ex else None
                got = try_lp(
                    c,
                    sos,
                    css_beta=css_b,
                    ind2=i2 if use_ex else None,
                    regs=regs,
                )
                if got is None:
                    continue
                if hit is None or got["t"] < hit["t"]:
                    hit = {
                        **got,
                        "kind": tag,
                        "Qb": Qb.tolist(),
                        "Qe": Qe.tolist(),
                    }
                    print(f"  c={c} {tag}#{i} t={got['t']:+.6f} ok={got['ok']}", flush=True)
                    if got["ok"] and (found_cert is None or c < found_cert["c"] - 1e-12):
                        found_cert = maybe_write_cert(
                            c,
                            hit,
                            AC,
                            css_b,
                            i2 if use_ex else None,
                            (beta_reg, eta_reg) if use_ex else (None, None),
                            tag,
                        )

        # refine the best Q a bit
        if hit is not None and "Qb" in hit:
            Qb = np.array(hit["Qb"])
            Qe = None if hit.get("Qe") is None else np.array(hit["Qe"])
            use_ex = "ckls" in hit.get("kind", "")
            css_b = CSS_BETA_CKLS if use_ex else CSS_BETA_HKN
            regs = build_regs(beta_reg, eta_reg, c) if use_ex else None
            ref = refine_chol(
                c,
                Qb,
                AC,
                Qe=Qe,
                steps=12,
                css_beta=css_b,
                ind2=i2 if use_ex else None,
                regs=regs,
            )
            if ref is not None and ref["t"] < hit["t"]:
                hit = {**ref, "kind": hit.get("kind", "") + "+refine"}
                print(f"  c={c} refine t={ref['t']:+.6f} ok={ref['ok']}", flush=True)
                if ref["ok"] and (found_cert is None or c < found_cert["c"] - 1e-12):
                    found_cert = maybe_write_cert(
                        c,
                        hit,
                        AC,
                        css_b,
                        i2 if use_ex else None,
                        (beta_reg, eta_reg) if use_ex else (None, None),
                        hit["kind"],
                    )

        slim = None if hit is None else {k: hit[k] for k in hit if k not in ("Qb", "Qe", "Q")}
        best[str(c)] = slim
        print(
            f"BEST c={c} t={None if hit is None else hit['t']} kind={None if hit is None else hit.get('kind')}",
            flush=True,
        )
        if found_cert is not None and c < 0.34645 - 1e-12:
            # keep gathering t at the remaining targets for the report
            pass

    rec = {
        "n_labeled_by_type": n_type,
        "eta_flags": 9,
        "n_try": n_try,
        "scales": list(scales),
        "css_beta_ckls": CSS_BETA_CKLS,
        "kappa4_ok": ok_k,
        "best_t_by_c": best,
        "certificate": None
        if found_cert is None
        else {k: found_cert[k] for k in ("c", "t", "worst_F", "Q_min_eig", "tag", "css_beta")},
        "note": (
            "t<0 certifies emptiness at that c. "
            "If the best t at c<0.34645 stays nonnegative, F4 did not move. "
            "0.3388 is a personal communication."
        ),
    }
    KEEP.mkdir(parents=True, exist_ok=True)
    path = KEEP / "hunt_threshold.json"
    path.write_text(json.dumps(rec, indent=2))
    print("wrote", path, flush=True)
    if found_cert:
        print("certified c=", found_cert["c"], "worst=", found_cert["worst_F"])
    else:
        print("no c<0.34645 certified")


if __name__ == "__main__":
    main()
