#!/usr/bin/env python3
"""Mass-stationary cut Q > R/(R+1) vs the certified compact γ.

Same algebra as q3, now at the best certified (R,n). Writes
certs/aspect_identities.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

from select_row import best_row

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 80
iv.dps = 60


def S(x, d: int = 40) -> str:
    return nstr(x, d, strip_zeros=False)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    row = best_row()
    R = mpf(row["R"])
    gamma = mpf(str(row["compact_gamma"]))
    cut = R / (R + 1)
    ok = True
    empty_ok = True
    for qn in range(890, 1000):
        Q = mpf(qn) / 1000
        lo = ((1 - Q) / Q) * (R**2)
        hi = Q / (1 - Q)
        if lo < hi and Q <= cut:
            empty_ok = False
            ok = False
    cut_beats = bool(cut > gamma)
    leading = 1 / gamma
    blob = {
        "status": "ok" if ok and cut_beats else "fail",
        "R_split": int(row["R"]),
        "n": int(row["n"]),
        "target": row["target"],
        "Q_cut": f"{int(row['R'])}/{int(row['R'])+1}",
        "Q_cut_value": S(cut),
        "compact_gamma": S(gamma),
        "compact_inv": S(leading),
        "cut_exceeds_compact_gamma": cut_beats,
        "empty_D_interval_for_Q_le_cut": empty_ok,
        "algebra": (
            "Mass-stationarity at inf=1 and sup=R gives "
            "M_{-1}=Q+(Q-1)D>0 and M_3=(Q-1)R^3+Q D R>0, "
            "hence R<Q/(1-Q) and Q>R/(R+1)."
        ),
        "beats_1.1021": bool(leading < mpf("1.1021")),
        "beats_1.1026": bool(leading < mpf("1.1026")),
        "beats_1.1035": bool(leading < mpf("1.1035")),
        "beats_1.1057": bool(leading < mpf("1.1057")),
        "beats_1.1118": bool(leading < mpf("1.1118")),
        "beats_1.108741": bool(leading < mpf("1.108741")),
        "faces": row.get("faces"),
        "source": row.get("_path"),
    }
    out = CERTS / "aspect_identities.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("R", int(row["R"]), "cut", float(cut), "γ", float(gamma), "1/γ", float(leading))
    print("cut>γ", cut_beats, "empty", empty_ok)
    print("wrote", out)
    if not (ok and cut_beats and leading < mpf("1.1021")):
        raise SystemExit("aspect_identities.py FAIL")
    print("aspect_identities.py PASS")


if __name__ == "__main__":
    main()
