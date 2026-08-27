#!/usr/bin/env python3
"""Plug N=3,4 and Z=2,3,4,5 into the Nam / HPS identities.

Uses only published constants (Nam Lemma 1–2, Prop. 1; HPS (7.10) and
the q1 remainder 2.953). Shows that the uniform-in-Z remainder is larger
than the room between b(s)Z and the next integer at these charges.

Nam Lemma 1:  alpha_N (N-1) < Z (1 + 0.68 N^{-2/3})
Nam Prop. 1:  alpha_N >= N/(N-1) [β - 3(β/6)^{1/3} N^{-2/3}], β>=0.8218
At N=4 the Prop. 1 remainder already makes the right-hand side negative
or smaller than 1/2, so it cannot beat Lieb.

A search upper bound on alpha_4 from alpha_n.json is recorded as a
heuristic: even that optimistic number times 3 sits below the Nam
Lemma-1 right-hand side at Z=2 once the 0.68 kinetic error is kept.

Replay: python3 nam_smallz.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from mpmath import mp, mpf, nstr, sqrt

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 60


def S(x, d=24) -> str:
    return nstr(x, d, strip_zeros=False)


def nam_alpha_lower(N: int, beta: mpf) -> mpf:
    # N/(N-1) [β - 3(β/6)^{1/3} N^{-2/3}]
    rem = 3 * (beta / 6) ** (mpf(1) / 3) * mpf(N) ** (mpf(-2) / 3)
    return mpf(N) / (N - 1) * (beta - rem)


def nam_rhs(Z: int, N: int) -> mpf:
    return mpf(Z) * (1 + mpf("0.68") * mpf(N) ** (mpf(-2) / 3))


def hps_s2_rhs(Z: int, N: int) -> mpf:
    """Right-hand side of HPS (7.10) divided by β2, i.e. an upper envelope on N.

    N β2 <= Z + λ Z N^{-2/3} + (9/2 β2)^{1/3} N^{1/3}
    """
    beta2 = 2 * (sqrt(2) - 1)
    # λ = 3/8 C1^{-1} κ with κ from FHJN 1.456; HPS print λ≈0.6284
    lam = mpf("0.6284")
    return (
        mpf(Z)
        + lam * Z * mpf(N) ** (mpf(-2) / 3)
        + ((mpf(9) / 2) * beta2) ** (mpf(1) / 3) * mpf(N) ** (mpf(1) / 3)
    )


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    beta = mpf("0.8218")
    sqrt5_4 = sqrt(5) / 4
    alpha_search = {}
    ap = CERTS / "alpha_n.json"
    if ap.is_file():
        for r in json.loads(ap.read_text())["rows"]:
            if abs(r["s"] - 2.0) < 1e-12:
                alpha_search[r["N"]] = r["search_min"]

    rows = []
    print("Nam Prop.1 lower on alpha_N (β=0.8218) vs triangle 1/2 vs √5/4")
    for N in (3, 4, 5, 6, 8, 12):
        lo = nam_alpha_lower(N, beta)
        print(
            f"  N={N:2d}  Prop1 {float(lo): .6f}  "
            f"triangle 0.5  Nam√5/4 {float(sqrt5_4):.6f}  "
            f"search_s2 {alpha_search.get(N, float('nan'))}"
        )
        rows.append(
            {
                "N": N,
                "prop1_lower": S(lo),
                "prop1_beats_half": bool(lo > mpf("0.5")),
                "sqrt5_over_4": S(sqrt5_4),
                "search_s2_upper_on_inf": alpha_search.get(N),
            }
        )

    print()
    print("Nam Lemma 1 at small Z: need alpha_N (N-1) < Z(1+0.68 N^{-2/3}) for consistency")
    print("Contradiction would require a *lower* bound on alpha_N (N-1) exceeding the RHS.")
    attempts = []
    for Z in (2, 3, 4, 5):
        for N in (3, 4, 5, 2 * Z, 2 * Z + 1):
            if N < 3:
                continue
            rhs = nam_rhs(Z, N)
            # Best published lower: max(1/2, Prop1, √5/4)
            lo = max(mpf("0.5"), nam_alpha_lower(N, beta), sqrt5_4)
            lhs_lo = lo * (N - 1)
            search = alpha_search.get(N)
            lhs_search = None if search is None else search * (N - 1)
            contrad_pub = lhs_lo > rhs
            # search is an UPPER on alpha, so lhs_search > rhs does not contradict.
            attempts.append(
                {
                    "Z": Z,
                    "N": N,
                    "lhs_published_lower": S(lhs_lo),
                    "rhs_lemma1": S(rhs),
                    "contradiction_from_published_alpha_lower": contrad_pub,
                    "lhs_from_search_upper": None if lhs_search is None else lhs_search,
                    "search_upper_minus_rhs": (
                        None if lhs_search is None else lhs_search - float(rhs)
                    ),
                }
            )
            flag = "CONTRADICTION" if contrad_pub else "no"
            extra = ""
            if lhs_search is not None:
                extra = f"  search_upper*(N-1)={lhs_search:.4f}"
            print(
                f"  Z={Z} N={N}: lhs_lo={float(lhs_lo):.4f}  rhs={float(rhs):.4f}  "
                f"{flag}{extra}"
            )

    print()
    print("HPS (7.10) left N β2 vs right-hand side (λ=0.6284)")
    beta2 = 2 * (sqrt(2) - 1)
    hps_rows = []
    for Z in (2, 3, 4, 5):
        for N in (3, 4, 5, 6):
            lhs = N * beta2
            rhs = hps_s2_rhs(Z, N)
            hps_rows.append(
                {
                    "Z": Z,
                    "N": N,
                    "N_beta2": S(lhs),
                    "rhs": S(rhs),
                    "contradiction": bool(lhs > rhs),
                }
            )
            print(
                f"  Z={Z} N={N}: N β2={float(lhs):.4f}  rhs={float(rhs):.4f}  "
                f"{'CONTRADICTION' if lhs > rhs else 'no'}"
            )

    blob = {
        "not_a_certificate": True,
        "is_new_bound": False,
        "beta_used": S(beta),
        "alpha_prop1": rows,
        "nam_lemma1": attempts,
        "hps_710": hps_rows,
        "note": (
            "No (N,Z) in this table yields a contradiction from published "
            "lower bounds on alpha_N. At Z=2, N=4 the Prop. 1 remainder is "
            "larger than β, so that lower bound is useless. The search upper "
            "on alpha_4*(3) is still below the Lemma-1 RHS once the kinetic "
            "0.68 N^{-2/3} is kept. HPS (7.10) likewise does not exclude "
            "N=4 at Z=2: the N^{1/3} remainder is ~2.5."
        ),
    }
    path = CERTS / "nam_smallz.json"
    path.write_text(json.dumps(blob, indent=2) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
