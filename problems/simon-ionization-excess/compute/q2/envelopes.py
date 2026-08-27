#!/usr/bin/env python3
"""Published upper envelopes on Nc(Z) at integer Z = 2, 3, 4, 5.

Not a new bound. Replays, at these four charges, the printed inequalities
and the q1 arithmetic tightening of the HPS remainders:

  Lieb:              Nc < 2Z+1
  Nam:               Nc < 1.22 Z + 3 Z^{1/3}
  HPS s=2 printed:   Nc < b(2) Z + 2.96 Z^{1/3}                 (Z>=2)
  HPS s=2 q1:        Nc < b(2) Z + 2.953 Z^{1/3}                (Z>=2)
  HPS s=3 printed:   Nc < b(3) Z + 3.90 Z^{1/3}
                     + 0.0134 + 0.184 Z^{-1/3} + 0.0196 Z^{-2/3}  (Z>=4)
  HPS s=3 q1:        same extras, remainder 3.892                 (Z>=4)
  HPS simplified:    Nc < 1.1185 Z + 4 Z^{1/3}                   (Z>=4)
  HPS simp. q1:      Nc < 1.1185 Z + 3.9781 Z^{1/3}              (Z>=4)

b(2) = (sqrt(2)+1)/2, b(3) the HPS (2.9) closed form.
Cube roots via mpmath (80 dps); integer exclusion is exact from
Nc < U => Nc <= largest integer strictly less than U.

Sources (opened this session):
  Lieb, Phys. Rev. A 29 (1984);
  Nam, arXiv:1009.2367v3 HTML;
  Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1 HTML Prop. 2.4–2.5;
  q1 tighten_hps.py remainders 2.953, 3.892, 3.9781.

Replay: python3 envelopes.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from mpmath import mp, mpf, nstr, sqrt

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 80


def S(x, d: int = 40) -> str:
    return nstr(x, d, strip_zeros=False)


def b2() -> mpf:
    return (sqrt(2) + 1) / 2


def b3() -> mpf:
    u = (1 + sqrt(2)) ** (mpf(1) / 3)
    return (mpf(2) / 3) * u / (u**2 - 1)


def z13(z: int) -> mpf:
    return mpf(z) ** (mpf(1) / 3)


def lieb_U(z: int) -> mpf:
    return 2 * mpf(z) + 1


def nam_U(z: int) -> mpf:
    return mpf("1.22") * z + 3 * z13(z)


def hps_s2(z: int, rem: mpf) -> mpf:
    return b2() * z + rem * z13(z)


def hps_s3(z: int, rem: mpf) -> mpf:
    t = z13(z)
    return (
        b3() * z
        + rem * t
        + mpf("0.0134")
        + mpf("0.184") / t
        + mpf("0.0196") / (t * t)
    )


def hps_simp(z: int, rem: mpf) -> mpf:
    return mpf("1.1185") * z + rem * z13(z)


def max_integer_strictly_below(U: mpf) -> int:
    """Largest integer N with N < U."""
    # U is positive and modest. Compare integers in mpmath.
    n = int(math.floor(float(U))) + 2
    while mpf(n) >= U:
        n -= 1
    return n


def excluded_from(U: mpf) -> int:
    """Smallest integer N already excluded by Nc < U."""
    return max_integer_strictly_below(U) + 1


def pack(U: mpf | None, applicable: bool) -> dict | None:
    if not applicable or U is None:
        return None
    nmax = max_integer_strictly_below(U)
    return {
        "U": S(U),
        "U_float": float(U),
        "max_integer_Nc": nmax,
        "excludes_N_geq": nmax + 1,
    }


def row(z: int) -> dict:
    out = {
        "Z": z,
        "lieb": pack(lieb_U(z), True),
        "nam": pack(nam_U(z), True),
        "hps_s2_printed": pack(hps_s2(z, mpf("2.96")), z >= 2),
        "hps_s2_q1": pack(hps_s2(z, mpf("2.953")), z >= 2),
        "hps_s3_printed": pack(hps_s3(z, mpf("3.90")), z >= 4),
        "hps_s3_q1": pack(hps_s3(z, mpf("3.892")), z >= 4),
        "hps_simplified_printed": pack(hps_simp(z, mpf(4)), z >= 4),
        "hps_simplified_q1": pack(hps_simp(z, mpf("3.9781")), z >= 4),
    }
    named = [
        ("lieb", out["lieb"]),
        ("nam", out["nam"]),
        ("hps_s2_printed", out["hps_s2_printed"]),
        ("hps_s2_q1", out["hps_s2_q1"]),
        ("hps_s3_printed", out["hps_s3_printed"]),
        ("hps_s3_q1", out["hps_s3_q1"]),
        ("hps_simplified_printed", out["hps_simplified_printed"]),
        ("hps_simplified_q1", out["hps_simplified_q1"]),
    ]
    live = [(n, p) for n, p in named if p is not None]
    best_name, best = min(live, key=lambda kv: kv[1]["U_float"])
    out["best_published"] = {
        "name": best_name,
        "U": best["U"],
        "max_integer_Nc": best["max_integer_Nc"],
        "excludes_N_geq": best["excludes_N_geq"],
    }
    # Zhislin: binding for every N < Z+1, so N0(Z) >= Z for integer Z.
    out["zhislin_N0_at_least"] = z
    out["unsettled_integers"] = list(range(z, best["max_integer_Nc"] + 1))
    return out


def sanity() -> None:
    if not (mpf("1.2071") < b2() < mpf("1.2072")):
        raise SystemExit(f"b(2)={b2()} outside printed window")
    if not (mpf("1.1184") < b3() < mpf("1.1185")):
        raise SystemExit(f"b(3)={b3()} outside printed window")
    if max_integer_strictly_below(mpf(5)) != 4:
        raise SystemExit("Lieb Z=2 should give max integer 4")
    if max_integer_strictly_below(mpf("6.14")) != 6:
        raise SystemExit("6.14 should give max integer 6")


def main() -> None:
    sanity()
    CERTS.mkdir(parents=True, exist_ok=True)
    rows = [row(z) for z in (2, 3, 4, 5)]
    blob = {
        "not_a_new_bound": True,
        "is_new_bound": False,
        "record": [
            "Lieb Phys. Rev. A 29 (1984): Nc < 2Z+1",
            "Nam arXiv:1009.2367v3: Nc < 1.22 Z + 3 Z^{1/3}",
            "HPS arXiv:2504.18487v1 Prop. 2.4–2.5",
            "q1 remainder tightening 2.953 / 3.892 / 3.9781 (same HPS chain)",
        ],
        "constants": {
            "b2": S(b2()),
            "b3": S(b3()),
        },
        "at": rows,
        "punch": (
            "At Z=2,3,4,5 the best published integer bound is Lieb. "
            "Nam and both HPS envelopes sit above 2Z+1 here, so they "
            "exclude no extra integer N. Unsettled: Z=2 has N=2,3,4; "
            "Z=3 has N=3,4,5,6; Z=4 has N=4..8; Z=5 has N=5..10. "
            "Hydrogen uniqueness N0(1)=2 is Lieb 1984, not claimed here."
        ),
    }
    out = CERTS / "envelopes.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("b(2) =", S(b2(), 21))
    print("b(3) =", S(b3(), 21))
    print()
    print(f"{'Z':>3} {'source':<24} {'U':>12} {'Nc<=' :>5} {'excludes':>10}")
    for r in rows:
        z = r["Z"]
        for key in (
            "lieb",
            "nam",
            "hps_s2_printed",
            "hps_s2_q1",
            "hps_s3_printed",
            "hps_s3_q1",
            "hps_simplified_printed",
            "hps_simplified_q1",
        ):
            p = r[key]
            if p is None:
                print(f"{z:3d} {key:<24} {'(n/a)':>12}")
                continue
            print(
                f"{z:3d} {key:<24} {p['U_float']:12.6f} "
                f"{p['max_integer_Nc']:5d}   N>={p['excludes_N_geq']}"
            )
        b = r["best_published"]
        print(
            f"    BEST {b['name']}: Nc <= {b['max_integer_Nc']}; "
            f"unsettled {r['unsettled_integers']}"
        )
        print()
    print("wrote", out)
    print(blob["punch"])


if __name__ == "__main__":
    main()
