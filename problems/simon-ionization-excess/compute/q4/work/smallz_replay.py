#!/usr/bin/env python3
"""Replay published Nc envelopes at Z=2..6 with the q3 dent coefficients.

Includes the q3 simplified inequality N_c < 1.1118 Z + 3.966 Z^{1/3}
(Z>=4) alongside Lieb, Nam, and the HPS printed / q1 remainders.

One new finite-Z try (residue, not a dent):
  (A) Nam Lemma 1 at the Lieb-allowed edge N = floor(2Z+1)-1 = 2Z for
      Z=2..6, and at the unsettled candidates N=3,4 at Z=2.
  (B) Four-electron product trial for Z=2: exact Hylleraas 1s^2 core
      (-54353/18800) plus two hydrogenic 1s electrons on the same
      screening parameter zeta. This is a variational upper bound on
      E(4,2); comparing it to the three-electron hydrogenic 1s^2 2s
      trial from q1 does not prove non-binding (both are variational).

Integer exclusion: N_c < U => N_c <= largest integer strictly below U.

Replay: python3 smallz_replay.py
Writes: ../certs/smallz.json
"""

from __future__ import annotations

import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE.parent / "certs"

# Published constants (replay, not tightened here)
BETA_NAM = 0.8218
LAM_S2 = 0.628336  # q1 window; printed 0.6284 is weaker
LEAD_Q3 = 1.1118
REM_Q3 = 3.966
LEAD_HPS = 1.1185
REM_HPS_Q1 = 3.9781


def b2() -> float:
    return 0.5 * (math.sqrt(2.0) + 1.0)


def b3() -> float:
    s = 1.0 + math.sqrt(2.0)
    return (2.0 / 3.0) * (s ** (1.0 / 3.0)) / (s ** (2.0 / 3.0) - 1.0)


def beta2() -> float:
    return 2.0 * (math.sqrt(2.0) - 1.0)


def z13(z: int) -> float:
    return z ** (1.0 / 3.0)


def max_int_below(U: float) -> int:
    """Largest integer N with N < U."""
    n = math.floor(U)
    if abs(U - n) < 1e-15:
        return n - 1
    return int(n)


def pack(U: float) -> dict:
    nmax = max_int_below(U)
    return {"U": U, "nmax": nmax, "excludes_geq": nmax + 1}


def hps_s3(z: int, rem: float) -> float:
    t = z13(z)
    return b3() * z + rem * t + 0.0134 + 0.184 / t + 0.0196 / (t * t)


def nam_alpha_prop1_lower(N: int, beta: float = BETA_NAM) -> float:
    rem = 3.0 * (beta / 6.0) ** (1.0 / 3.0) * (N ** (-2.0 / 3.0))
    return (N / (N - 1)) * (beta - rem)


def nam_lemma1_rhs(Z: int, N: int) -> float:
    return Z * (1.0 + 0.68 * (N ** (-2.0 / 3.0)))


def nam_lemma1_try(Z: int, N: int) -> dict:
    """Nam Lemma 1 consistency at (Z, N). Contradiction needs a published lower."""
    lo_alpha = max(0.5, nam_alpha_prop1_lower(N), math.sqrt(5.0) / 4.0)
    lhs = lo_alpha * (N - 1)
    rhs = nam_lemma1_rhs(Z, N)
    return {
        "Z": Z,
        "N": N,
        "alpha_lower": lo_alpha,
        "lhs_lower": lhs,
        "lemma1_rhs": rhs,
        "contradiction": lhs > rhs + 1e-12,
        "margin": rhs - lhs,
    }


def he4_separated_trial() -> dict:
    """He + 2H at infinity: valid variational upper bound on E(4,2)."""
    e_he = float(Fraction(-54353, 18800))
    e_h = -0.5
    e_sep = e_he + 2.0 * e_h
    return {
        "trial": "He_Hylleraas_at_infinity_plus_2H_1s",
        "Z": 2,
        "N": 4,
        "energy_upper": e_sep,
        "hylleraas_core_exact": e_he,
        "hydrogenic_1s_exact": e_h,
    }


def he4_compact_trial(zeta: float, Z: float = 2.0) -> float:
    """He Hylleraas core + two hydrogenic 1s with mutual repulsion only.

    Omits core–outer repulsion, so this is not a legal variational upper
    bound (energy is too low). Recorded only as a failed compact attempt.
    """
    e_hyll = float(Fraction(-54353, 18800))
    i1 = 0.5 * zeta * zeta - Z * zeta
    j11 = 0.625 * zeta
    e_outer = 2.0 * i1 + j11
    return e_hyll + e_outer


def scan_he4(Z: float = 2.0) -> dict:
    sep = he4_separated_trial()
    best = None
    for i in range(401):
        z = 0.05 + (2.5 - 0.05) * i / 400.0
        e = he4_compact_trial(z, Z)
        if best is None or e < best[0]:
            best = (e, z)
    e3_hydrogenic = -6642153923171 / 911250000000  # q1 Z=2 1s^2 2s upper
    return {
        "separated_He_plus_2H": sep,
        "compact_attempt": {
            "trial": "Hylleraas_1s2_times_exp(-zeta(r3+r4))^2_outer_1s_only",
            "best_energy_if_repulsion_ignored": best[0],
            "best_zeta": best[1],
            "valid_variational_upper": False,
            "reason": "core–outer repulsion omitted; energy too negative",
        },
        "q1_three_electron_hydrogenic_1s2_2s_upper": e3_hydrogenic,
        "separated_upper_above_N3_upper": sep["energy_upper"] > e3_hydrogenic,
        "proves_N4_nonbinding": False,
        "note": (
            "Separated He+2H gives a legal upper bound E(4,2) <= -54353/18800 - 1. "
            "Comparing to the q1 N=3 hydrogenic upper does not prove E(4,2) >= E(3,2). "
            "Variational uppers alone cannot prove non-binding."
        ),
    }


def envelope_row(z: int) -> dict:
    t = z13(z)
    row = {
        "Z": z,
        "lieb": pack(2.0 * z + 1.0),
        "nam": pack(1.22 * z + 3.0 * t),
        "hps_s2_printed": pack(b2() * z + 2.96 * t),
        "hps_s2_q1": pack(b2() * z + 2.953 * t),
        "hps_s3_printed": pack(hps_s3(z, 3.90)) if z >= 4 else None,
        "hps_s3_q1": pack(hps_s3(z, 3.892)) if z >= 4 else None,
        "hps_simp_printed": pack(LEAD_HPS * z + 4.0 * t) if z >= 4 else None,
        "hps_simp_q1": pack(LEAD_HPS * z + REM_HPS_Q1 * t) if z >= 4 else None,
        "q3_simp_printed": pack(LEAD_Q3 * z + REM_Q3 * t) if z >= 4 else None,
    }
    published = [
        ("lieb", row["lieb"]),
        ("nam", row["nam"]),
        ("hps_s2_printed", row["hps_s2_printed"]),
        ("hps_s2_q1", row["hps_s2_q1"]),
    ]
    if row["hps_s3_printed"] is not None:
        published.extend(
            [
                ("hps_s3_printed", row["hps_s3_printed"]),
                ("hps_s3_q1", row["hps_s3_q1"]),
                ("hps_simp_printed", row["hps_simp_printed"]),
                ("hps_simp_q1", row["hps_simp_q1"]),
            ]
        )
    best_pub_name, best_pub = min(published, key=lambda kv: kv[1]["U"])
    row["best_published_name"] = best_pub_name
    row["best_published_nmax"] = best_pub["nmax"]

    all_bounds = list(published)
    if row["q3_simp_printed"] is not None:
        all_bounds.append(("q3_simp_printed", row["q3_simp_printed"]))
    best_all_name, best_all = min(all_bounds, key=lambda kv: kv[1]["U"])
    row["best_including_q3_name"] = best_all_name
    row["best_including_q3_nmax"] = best_all["nmax"]
    row["q3_excludes_extra_vs_published"] = (
        row["best_including_q3_nmax"] < row["best_published_nmax"]
    )
    row["unsettled"] = list(range(z, row["best_published_nmax"] + 1))
    return row


def sanity(rows: list[dict]) -> None:
    b2v, b3v = b2(), b3()
    if not (1.2071 < b2v < 1.2072):
        raise SystemExit("b(2) window")
    if not (1.1184 < b3v < 1.1185):
        raise SystemExit("b(3) window")
    byz = {r["Z"]: r for r in rows}
    if abs(byz[2]["nam"]["U"] - 6.21976314968462) > 1e-10:
        raise SystemExit("Z=2 Nam drifted")
    if abs(byz[5]["hps_s2_printed"]["U"] - 11.097062708095761) > 1e-10:
        raise SystemExit("Z=5 HPS s=2 drifted")
    for r in rows:
        if r["lieb"]["nmax"] != 2 * r["Z"]:
            raise SystemExit(f"Lieb integer at Z={r['Z']}")
        if r["best_published_nmax"] != 2 * r["Z"]:
            raise SystemExit(f"best published not Lieb at Z={r['Z']}")
        if r["q3_excludes_extra_vs_published"]:
            raise SystemExit(f"unexpected q3 integer gain at Z={r['Z']}")
        if r["Z"] >= 4 and r["q3_simp_printed"]["U"] >= r["hps_simp_q1"]["U"]:
            raise SystemExit("q3 simp should beat q1 HPS simp as reals")
        if r["Z"] >= 4 and r["q3_simp_printed"]["nmax"] < r["lieb"]["nmax"]:
            raise SystemExit("q3 unexpectedly beats Lieb integer")


def main() -> None:
    rows = [envelope_row(z) for z in (2, 3, 4, 5, 6)]
    sanity(rows)

    nam_tries = []
    for z in (2, 3, 4, 5, 6):
        nam_tries.append(nam_lemma1_try(z, 2 * z))
    for n in (3, 4):
        nam_tries.append(nam_lemma1_try(2, n))

    he4 = scan_he4(2.0)

    extra_integers = [
        {
            "Z": r["Z"],
            "published_nmax": r["best_published_nmax"],
            "with_q3_nmax": r["best_including_q3_nmax"],
            "extra_excluded": r["q3_excludes_extra_vs_published"],
        }
        for r in rows
        if r["Z"] >= 4
    ]
    any_extra = any(x["extra_excluded"] for x in extra_integers)

    blob = {
        "not_a_new_bound": True,
        "is_new_bound": False,
        "status": "residue",
        "record": [
            "Lieb Phys. Rev. A 29 (1984): Nc < 2Z+1",
            "Nam arXiv:1009.2367v3: Nc < 1.22 Z + 3 Z^{1/3}",
            "HPS arXiv:2504.18487v1 Prop. 2.4–2.5 (printed remainders)",
            "q1 remainder tightening 2.953 / 3.892 / 3.9781",
            "q3 dent (Z>=4): N_c < 1.1118 Z + 3.966 Z^{1/3} via beta3 >= 0.899526",
        ],
        "constants": {
            "b2": b2(),
            "b3": b3(),
            "q3_leading": LEAD_Q3,
            "q3_Z4_remainder": REM_Q3,
        },
        "at": rows,
        "q3_integer_exclusion_at_Z_ge_4": {
            "any_extra_integer_excluded_vs_lieb_nam_hps_printed": any_extra,
            "by_Z": extra_integers,
        },
        "finite_Z_try": {
            "nam_lemma1_at_lieb_edge_and_Z2_candidates": nam_tries,
            "he4_hylleraas_product": he4,
        },
        "N0_minus_Z": {
            "can_move_this_session": False,
            "reason": (
                "No verified integer envelope beats Lieb at Z=2..6. The q3 "
                "leading dent is Z>=4 and does not tighten integer caps. "
                "A leading coefficient >1 cannot prove a Z-independent excess "
                "bound on N0(Z)-Z."
            ),
        },
        "punch": (
            "Best published integer bound at Z=2..6 remains Lieb Nc<=2Z. "
            "The q3 simplified envelope 1.1118 Z + 3.966 Z^{1/3} beats the "
            "printed HPS leading at Z>=4 as reals but excludes no extra "
            "integer N beyond Lieb/Nam/HPS printed. Nam Lemma 1 at the Lieb "
            "edge and a four-electron Hylleraas product trial for Z=2, N=4 "
            "do not yield a dent. N0(Z)-Z bounded cannot move here."
        ),
    }

    CERTS.mkdir(parents=True, exist_ok=True)
    out = CERTS / "smallz.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")

    print(f"{'Z':>3} {'Lieb':>8} {'Nam':>10} {'HPSs2':>10} {'q3simp':>10} {'best':>5} {'q3+':>4}")
    for r in rows:
        q3s = r["q3_simp_printed"]["U"] if r["q3_simp_printed"] else float("nan")
        print(
            f"{r['Z']:3d} {r['lieb']['U']:8.3f} {r['nam']['U']:10.6f} "
            f"{r['hps_s2_printed']['U']:10.6f} {q3s:10.6f} "
            f"{r['best_published_nmax']:5d} "
            f"{'yes' if r['q3_excludes_extra_vs_published'] else 'no'}"
        )
    print()
    print("q3 excludes extra integer at any Z>=4?", any_extra)
    print()
    print("Nam Lemma 1 (Lieb edge N=2Z and Z=2 candidates):")
    for t in nam_tries:
        flag = "CONTRADICTION" if t["contradiction"] else "no"
        print(
            f"  Z={t['Z']} N={t['N']}: lhs_lo={t['lhs_lower']:.4f} "
            f"rhs={t['lemma1_rhs']:.4f}  {flag}"
        )
    print()
    print("He Hylleraas + 2H separated trial for Z=2, N=4:")
    sep = he4["separated_He_plus_2H"]
    print(f"  E(4,2) <= {sep['energy_upper']:.6f}  (He Hylleraas + 2×H 1s at infinity)")
    print(
        f"  q1 N=3 hydrogenic upper = "
        f"{he4['q1_three_electron_hydrogenic_1s2_2s_upper']:.6f}"
    )
    print(f"  separated upper > N=3 upper? {he4['separated_upper_above_N3_upper']}")
    print(f"  proves N=4 non-binding? {he4['proves_N4_nonbinding']}")
    print()
    print(blob["punch"])
    print("wrote", out)


if __name__ == "__main__":
    main()
