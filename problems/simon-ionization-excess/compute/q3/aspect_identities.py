#!/usr/bin/env python3
"""Algebra of the mass-stationary aspect bound.

HPS arXiv:2504.18487v1, s=3 Newton kernel
  g(r,u)=(r³+u³)/(2 max(r,u)).
For a probability m supported in [1,R],
  V(1)=D/2 + M_{-1}/2,   V(R)=R²/2 + M_3/(2R),
with D=∫ r² dm, M_{-1}=∫ r^{-1} dm, M_3=∫ r³ dm.
Mass-stationarity at both ends is V=(Q/2)(r²+D), hence
  M_{-1}=Q+(Q-1)D,   M_3=(Q-1)R³ + Q D R.
Then M_{-1}>0 and M_3>0 force R < Q/(1-Q), i.e. Q > R/(R+1).

At R=12 this is Q > 12/13. Combined with the q2 compact lower
bound on aspect ≤ 12, every mass-stationary atomic measure has
Q above the compact γ.

Writes certs/aspect_identities.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
Q2_COMPACT = HERE.parent / "q2" / "certs" / "beta3_compact.json"

mp.dps = 80
iv.dps = 60


def S(x, d: int = 40) -> str:
    return nstr(x, d, strip_zeros=False)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    compact = json.loads(Q2_COMPACT.read_text())
    row = None
    for r in compact["configs"]:
        if r["R"] == 12:
            row = r
            break
    if row is None:
        raise SystemExit("R=12 row missing from q2 compact cert")

    gamma = mpf(row["compact_gamma"])
    inv = mpf(row["compact_inv"])
    twelve_thirteenths = mpf(12) / 13
    # Algebra: R < Q/(1-Q) ⇔ Q > R/(R+1)
    # Check a grid of (Q,D,R) with the two moment signs, plus the R=12 cut.
    R0 = iv.mpf(12)
    cut = R0 / (R0 + 1)
    cut_lo, cut_hi = mpf(cut.a), mpf(cut.b)

    # Enclosure: if 0<Q<1, D>0, R>1, M_{-1}>0, M_3>0 ⇒ R(1-Q)<Q.
    # Proof (exact): M_3>0 ⇒ D > ((1-Q)/Q) R²; M_{-1}>0 ⇒ D < Q/(1-Q);
    # hence ((1-Q)/Q) R² < Q/(1-Q) ⇒ R < Q/(1-Q).
    samples = []
    ok = True
    for qn in range(895, 1000):
        Q = mpf(qn) / 1000
        if Q <= 0 or Q >= 1:
            continue
        # pick D in the open interval if nonempty
        # ((1-Q)/Q) R² < D < Q/(1-Q) at R=12
        lo = ((1 - Q) / Q) * 144
        hi = Q / (1 - Q)
        samples.append(
            {
                "Q": S(Q, 12),
                "D_lo_at_R12": S(lo, 12),
                "D_hi": S(hi, 12),
                "interval_empty": bool(lo >= hi),
                "R_star": S(hi, 12),
            }
        )
        if lo >= hi and Q <= twelve_thirteenths + mpf("1e-12"):
            # expected: no mass-stationary measure at R=12 with this Q
            pass
        if lo < hi and Q <= twelve_thirteenths:
            # would be a hole in the algebra
            ok = False

    # Strict cut
    cut_beats_gamma = bool(twelve_thirteenths > gamma)
    inv_cut = mpf(13) / 12
    leading_from_gamma = 1 / gamma

    # Interval form of the implication at generic Q
    # Take Q in (12/13, 1) and R=12: the D-interval is nonempty.
    Q_iv = iv.mpf("0.93")
    Dlo = ((1 - Q_iv) / Q_iv) * (iv.mpf(12) ** 2)
    Dhi = Q_iv / (1 - Q_iv)
    nonempty_at_093 = bool(mpf(Dlo.b) < mpf(Dhi.a))

    blob = {
        "status": "ok" if ok and cut_beats_gamma else "fail",
        "R_split": 12,
        "Q_cut": "12/13",
        "Q_cut_value": S(twelve_thirteenths),
        "Q_cut_inv": S(inv_cut),
        "compact_gamma_R12": S(gamma),
        "compact_inv_R12": S(inv),
        "cut_exceeds_compact_gamma": cut_beats_gamma,
        "algebra": (
            "Mass-stationarity at inf=1 and sup=R gives "
            "M_{-1}=Q+(Q-1)D>0 and M_3=(Q-1)R^3+Q D R>0, "
            "hence R<Q/(1-Q) and Q>R/(R+1)."
        ),
        "nonempty_D_interval_at_Q_0.93_R_12": nonempty_at_093,
        "empty_D_interval_for_Q_le_12_13_at_R_12": ok,
        "samples_Q_0.895_to_0.999": samples[::20],
        "leading_from_compact_gamma": S(leading_from_gamma),
        "beats_1.1185_if_lifted": bool(leading_from_gamma < mpf("1.1185")),
        "faces_row": {
            "copositive": row.get("faces", {}).get("copositive"),
            "singular_or_illconditioned": row.get("faces", {}).get(
                "singular_or_illconditioned"
            ),
            "min_mMm_safe": row.get("faces", {}).get("min_mMm_safe"),
            "certified_phi": row.get("certified_phi"),
        },
    }
    out = CERTS / "aspect_identities.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("R=12 cut 12/13 =", float(twelve_thirteenths))
    print("compact γ     =", float(gamma), "1/γ =", float(leading_from_gamma))
    print("cut > γ      =", cut_beats_gamma)
    print("empty D-interval for Q≤12/13 at R=12:", ok)
    print("wrote", out)
    if not (ok and cut_beats_gamma and leading_from_gamma < mpf("1.1185")):
        raise SystemExit("aspect_identities.py FAIL")
    print("aspect_identities.py PASS")


if __name__ == "__main__":
    main()
