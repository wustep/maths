#!/usr/bin/env python3
"""Replay published Nc envelopes at Z=2..6, plus one cheap finite-Z try.

Not a new bound. Integer exclusion is Nc < U => Nc <= largest integer
strictly below U.

Published (opened this session):
  Lieb, Phys. Rev. A 29 (1984): Nc < 2Z+1
  Nam, arXiv:1009.2367v3 HTML: Nc < 1.22 Z + 3 Z^{1/3},
    and that real envelope is < 2Z+1 when Z>=6
  HPS, arXiv:2504.18487v1 HTML Prop. 2.4–2.5 / (7.10)
  q1 remainders 2.953 / 3.892 / 3.9781 (same HPS chain)
  BGB, arXiv:2511.07582v1: N < 1.4811 Z + 3.1516 Z^{1/3} only for Z>=12

New try (not a dent):
  (1) HPS (7.10) and the Prop. 2.4 remainder a(x) at the actual
      Lieb edge N/Z < 2+1/Z, not the uniform x<=5/2.
  (2) Nam Lemma 1 / Prop. 1 at the Lieb-allowed edge N=2Z.
  (3) Exact pair-geometry configs: tetrahedron (q2), 5 octahedron
      vertices, regular octahedron, centred line.

Replay: python3 smallz_replay.py
"""

from __future__ import annotations

import math
from fractions import Fraction

from mpmath import mp, mpf, nstr, pi, sqrt

mp.dps = 80


def S(x, d: int = 24) -> str:
    return nstr(x, d, strip_zeros=False)


def b2() -> mpf:
    return (sqrt(2) + 1) / 2


def b3() -> mpf:
    u = (1 + sqrt(2)) ** (mpf(1) / 3)
    return (mpf(2) / 3) * u / (u**2 - 1)


def beta2() -> mpf:
    return 2 * (sqrt(2) - 1)


def z13(z: int) -> mpf:
    return mpf(z) ** (mpf(1) / 3)


def max_integer_strictly_below(U: mpf) -> int:
    n = int(math.floor(float(U))) + 2
    while mpf(n) >= U:
        n -= 1
    return n


def pack(U: mpf) -> dict:
    nmax = max_integer_strictly_below(U)
    return {"U": U, "nmax": nmax, "excludes": nmax + 1}


def hps_s3(z: int, rem: mpf) -> mpf:
    t = z13(z)
    return b3() * z + rem * t + mpf("0.0134") + mpf("0.184") / t + mpf("0.0196") / (t * t)


def C1() -> mpf:
    return (
        (mpf(3) ** (mpf(5) / 3))
        * (mpf(5) ** (mpf(5) / 6))
        * ((7 / pi) ** (mpf(1) / 3))
        / (22 * sqrt(11))
    )


def kappa() -> mpf:
    return sqrt(5) * (2 / (9 * pi**2) * mpf("1.456")) ** (mpf(1) / 3)


def lam_s2() -> mpf:
    return (mpf(3) / 8) * (1 / C1()) * kappa()


def a_s2(x: mpf) -> mpf:
    """HPS Prop. 2.4 remainder as a function of x = N/Z."""
    return (1 / beta2()) * lam_s2() * x ** (mpf(-2) / 3) + (1 / beta2()) * (
        (mpf(9) / 2) * beta2()
    ) ** (mpf(1) / 3) * x ** (mpf(1) / 3)


def nam_alpha_prop1(N: int) -> mpf:
    beta = mpf("0.8218")
    rem = 3 * (beta / 6) ** (mpf(1) / 3) * mpf(N) ** (mpf(-2) / 3)
    return mpf(N) / (N - 1) * (beta - rem)


def nam_lemma1_rhs(Z: int, N: int) -> mpf:
    return mpf(Z) * (1 + mpf("0.68") * mpf(N) ** (mpf(-2) / 3))


def hps710_rhs(Z: int, N: int, lam: mpf) -> mpf:
    return (
        mpf(Z)
        + lam * Z * mpf(N) ** (mpf(-2) / 3)
        + ((mpf(9) / 2) * beta2()) ** (mpf(1) / 3) * mpf(N) ** (mpf(1) / 3)
    )


def hps76_lhs(r: mpf, N: int) -> mpf:
    """Left-hand side of HPS (7.6) at a given r>0."""
    g = (r**2 / 3 + 1) / (r**2 + 1)
    return g * N * beta2() - 1 / r


def max_hps76(N: int) -> mpf:
    """Cheap grid + golden max of (7.6) on r in (0.05, 2)."""
    lo, hi = mpf("0.05"), mpf("2")
    phi = (sqrt(5) - 1) / 2
    # coarse grid first
    best = hps76_lhs((lo + hi) / 2, N)
    rbest = (lo + hi) / 2
    k = 80
    for i in range(k + 1):
        r = lo + (hi - lo) * i / k
        val = hps76_lhs(r, N)
        if val > best:
            best, rbest = val, r
    a = rbest - mpf("0.04")
    b = rbest + mpf("0.04")
    if a < lo:
        a = lo
    if b > hi:
        b = hi
    for _ in range(80):
        t1 = b - phi * (b - a)
        t2 = a + phi * (b - a)
        if hps76_lhs(t1, N) < hps76_lhs(t2, N):
            a = t1
        else:
            b = t2
    r = (a + b) / 2
    return hps76_lhs(r, N)


def alpha_s2(pts: list[tuple[float, float, float]]) -> float:
    N = len(pts)
    rs = [math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2) for p in pts]
    den = (N - 1) * sum(rs)
    if den <= 0:
        return float("inf")
    num = 0.0
    for i, a in enumerate(pts):
        for b in pts[i + 1 :]:
            d = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
            if d < 1e-15:
                return float("inf")
            num += (rs[i] ** 2 + (b[0] ** 2 + b[1] ** 2 + b[2] ** 2)) / d
    return num / den


def envelopes() -> list[dict]:
    rows = []
    for z in (2, 3, 4, 5, 6):
        t = z13(z)
        row = {
            "Z": z,
            "lieb": pack(2 * mpf(z) + 1),
            "nam": pack(mpf("1.22") * z + 3 * t),
            "nam_beta_inv": pack(z / mpf("0.8218") + 3 * t),
            "hps_s2_printed": pack(b2() * z + mpf("2.96") * t),
            "hps_s2_q1": pack(b2() * z + mpf("2.953") * t),
            "hps_s3_printed": pack(hps_s3(z, mpf("3.90"))) if z >= 4 else None,
            "hps_s3_q1": pack(hps_s3(z, mpf("3.892"))) if z >= 4 else None,
            "hps_simp_printed": pack(mpf("1.1185") * z + 4 * t) if z >= 4 else None,
            "hps_simp_q1": pack(mpf("1.1185") * z + mpf("3.9781") * t) if z >= 4 else None,
            "bgb": pack(mpf("1.4811") * z + mpf("3.1516") * t),
        }
        # Z-local HPS s=2 remainder: max a(x) on x <= 2+1/Z (increasing).
        x_edge = 2 + mpf(1) / z
        a_loc = a_s2(x_edge)
        row["hps_s2_local"] = pack(b2() * z + a_loc * t)
        row["a_local"] = a_loc
        row["x_edge"] = x_edge
        live = [
            ("lieb", row["lieb"]),
            ("nam", row["nam"]),
            ("hps_s2_printed", row["hps_s2_printed"]),
            ("hps_s2_q1", row["hps_s2_q1"]),
        ]
        if row["hps_s3_printed"] is not None:
            live.append(("hps_s3_printed", row["hps_s3_printed"]))
            live.append(("hps_s3_q1", row["hps_s3_q1"]))
            live.append(("hps_simp_printed", row["hps_simp_printed"]))
            live.append(("hps_simp_q1", row["hps_simp_q1"]))
        best_name, best = min(live, key=lambda kv: kv[1]["U"])
        row["best_real"] = best_name
        row["best_integer_n"] = min(p["nmax"] for _, p in live)
        rows.append(row)
    return rows


def print_envelopes(rows: list[dict]) -> None:
    print("b(2) =", S(b2(), 21))
    print("b(3) =", S(b3(), 21))
    print("λ_s2 =", S(lam_s2(), 21), "  (HPS print ≈ 0.6284)")
    print()
    print(
        f"{'Z':>3} {'source':<22} {'U':>12} {'Nc<=':>5}  excludes"
    )
    keys = (
        "lieb",
        "nam",
        "nam_beta_inv",
        "hps_s2_printed",
        "hps_s2_q1",
        "hps_s2_local",
        "hps_s3_printed",
        "hps_s3_q1",
        "hps_simp_printed",
        "hps_simp_q1",
        "bgb",
    )
    for r in rows:
        z = r["Z"]
        for key in keys:
            p = r[key]
            if p is None:
                print(f"{z:3d} {key:<22} {'(n/a)':>12}")
                continue
            note = ""
            if key == "bgb" and z < 12:
                note = "  (BGB stated only for Z>=12; formula only)"
            if key == "hps_s2_local":
                note = f"  a(2+1/Z)={float(r['a_local']):.6f}"
            print(
                f"{z:3d} {key:<22} {float(p['U']):12.6f} "
                f"{p['nmax']:5d}   N>={p['excludes']}{note}"
            )
        print(
            f"    best real {r['best_real']}; "
            f"best published integer Nc<={r['best_integer_n']}; "
            f"unsettled {list(range(z, r['best_integer_n'] + 1))}"
        )
        print()


def check_known(rows: list[dict]) -> None:
    if not (mpf("1.2071") < b2() < mpf("1.2072")):
        raise SystemExit("b(2) window")
    if not (mpf("1.1184") < b3() < mpf("1.1185")):
        raise SystemExit("b(3) window")
    byz = {r["Z"]: r for r in rows}
    # q2 envelopes.json floats
    if abs(float(byz[2]["nam"]["U"]) - 6.21976314968462) > 1e-12:
        raise SystemExit("Z=2 Nam drifted")
    if abs(float(byz[5]["hps_s2_printed"]["U"]) - 11.097062708095761) > 1e-12:
        raise SystemExit("Z=5 HPS s=2 drifted")
    if abs(float(byz[6]["nam"]["U"]) - 12.77136177849642) > 1e-10:
        raise SystemExit("Z=6 Nam drifted")
    if abs(float(byz[6]["hps_s2_printed"]["U"]) - 12.621317641902419) > 1e-10:
        raise SystemExit("Z=6 HPS s=2 drifted")
    for r in rows:
        if r["lieb"]["nmax"] != 2 * r["Z"]:
            raise SystemExit(f"Lieb integer at Z={r['Z']}")
        if r["best_integer_n"] != 2 * r["Z"]:
            raise SystemExit(f"best integer is not Lieb at Z={r['Z']}")
        if r["nam"]["U"] >= r["lieb"]["U"] and r["Z"] >= 6:
            raise SystemExit("Nam should beat Lieb as reals at Z>=6")
        if r["nam"]["U"] <= r["lieb"]["U"] and r["Z"] <= 5:
            raise SystemExit("Nam should sit above Lieb at Z<=5")
        if r["hps_s2_printed"]["U"] >= r["lieb"]["U"] and r["Z"] >= 6:
            raise SystemExit("HPS s=2 should beat Lieb as reals at Z=6")
        if r["hps_s2_local"]["nmax"] != 2 * r["Z"]:
            raise SystemExit("local HPS still same integer")
        if r["bgb"]["U"] <= r["lieb"]["U"] and r["Z"] <= 6:
            raise SystemExit("BGB formula is worse than Lieb at Z<=6")


def identities() -> None:
    print("HPS (7.10) / (7.6) and Nam Lemma 1 at the Lieb edge N=2Z")
    print(
        f"{'Z':>3} {'N':>4} {'N β2':>10} {'(7.10) rhs':>12} {'(7.6) max':>10} "
        f"{'gap710':>8} {'Nam lhs':>8} {'Nam rhs':>8}"
    )
    any_con = False
    sqrt5_4 = sqrt(5) / 4
    for z in (2, 3, 4, 5, 6):
        N = 2 * z
        lhs710 = N * beta2()
        rhs710 = hps710_rhs(z, N, lam_s2())
        rhs710_print = hps710_rhs(z, N, mpf("0.6284"))
        lhs76 = max_hps76(N)
        kinetic = z + lam_s2() * z * mpf(N) ** (mpf(-2) / 3)
        # (7.6) contradiction if max_r LHS > Z + λ Z N^{-2/3}
        con76 = lhs76 > kinetic
        con710 = lhs710 > rhs710
        lo = max(mpf("0.5"), nam_alpha_prop1(N), sqrt5_4)
        nam_lhs = lo * (N - 1)
        nam_rhs = nam_lemma1_rhs(z, N)
        con_nam = nam_lhs > nam_rhs
        any_con = any_con or con76 or con710 or con_nam
        print(
            f"{z:3d} {N:4d} {float(lhs710):10.6f} {float(rhs710):12.6f} "
            f"{float(lhs76):10.6f} {float(rhs710 - lhs710):8.4f} "
            f"{float(nam_lhs):8.4f} {float(nam_rhs):8.4f}"
            f"{'  CONTRADICTION' if (con76 or con710 or con_nam) else ''}"
        )
        if rhs710_print < lhs710:
            raise SystemExit("printed λ=0.6284 unexpectedly contradicts")
    if any_con:
        raise SystemExit("unexpected contradiction from published identities")
    print("no contradiction at N=2Z for Z=2..6")
    print()


def geometry() -> None:
    print("Pair-geometry configs (s=2). A config is an upper on inf alpha.")
    # Tetrahedron, q2.
    tet = (
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    )
    a_tet = alpha_s2(tet)
    if abs(a_tet - math.sqrt(6.0) / 4.0) > 1e-12:
        raise SystemExit(f"tetra alpha {a_tet}")
    if 54 >= 64:
        raise SystemExit("54<64 failed")
    print(f"  tetra N=4  alpha<=sqrt(6)/4={a_tet:.12f}  3*alpha<2 via 54<64")

    # 5 vertices of the regular octahedron (nucleus at origin).
    five = (
        (1.0, 0.0, 0.0),
        (-1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, 1.0),
    )
    a5 = alpha_s2(five)
    closed5 = (4 * math.sqrt(2.0) + 1.0) / 10.0
    if abs(a5 - closed5) > 1e-12:
        raise SystemExit(f"five-octa alpha {a5} != {closed5}")
    # alpha*4 < 3  <=>  (8 sqrt(2)+2)/5 < 3  <=>  8 sqrt(2) < 13  <=>  128 < 169
    if 128 >= 169:
        raise SystemExit("128<169 failed")
    if Fraction(128, 1) >= Fraction(169, 1):
        raise SystemExit("128<169 fraction failed")
    print(
        f"  5-octa N=5  alpha<=(4 sqrt(2)+1)/10={a5:.12f}  "
        f"4*alpha<3 via 128<169"
    )

    octa = five + ((0.0, 0.0, -1.0),)
    a6 = alpha_s2(octa)
    closed6 = (4 * math.sqrt(2.0) + 1.0) / 10.0
    if abs(a6 - closed6) > 1e-12:
        raise SystemExit(f"octa alpha {a6}")
    # alpha*5 ? 3  <=>  2 sqrt(2)+1/2 ? 3  <=>  8 ? 6.25, and 8>6.25
    if 8 <= Fraction(25, 4):
        raise SystemExit("octa should have 5*alpha > 3")
    print(
        f"  octa  N=6  alpha<=(4 sqrt(2)+1)/10={a6:.12f}  "
        f"5*alpha>3 (8>25/4); no block at Z=3"
    )

    # Centred equally spaced line, N=2Z. Upper on inf.
    print("  centred line (equal spacing):")
    for z in (2, 3, 4, 5, 6):
        N = 2 * z
        # positions ±1/2, ±3/2, ..., ±(N-1)/2
        half = N // 2
        pts = [((k + 0.5), 0.0, 0.0) for k in range(-half, half)]
        a = alpha_s2(pts)
        need = z / (N - 1)
        print(
            f"    N={N:2d} Z={z}  alpha<={a:.6f}  need>{need:.6f} to exclude  "
            f"{'blocks (upper<need)' if a < need else 'no block from this config'}"
        )

    # Triangular prism scan, N=6, Z=3. Need alpha>0.6 to have room.
    print("  triangular prism N=6 (scan h/R):")
    best = None
    for h in (0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0):
        R = 1.0
        z0 = h / 2.0
        pts = []
        for sgn in (-1.0, 1.0):
            for k in range(3):
                ang = 2 * math.pi * k / 3 + (0.0 if sgn < 0 else math.pi / 3)
                pts.append((R * math.cos(ang), R * math.sin(ang), sgn * z0))
        a = alpha_s2(pts)
        if best is None or a < best[0]:
            best = (a, h)
        print(f"    h/R={h:.1f}  alpha<={a:.6f}")
    print(f"  prism best in scan {best[0]:.6f} at h/R={best[1]}  vs need 0.6")
    if best[0] < 0.6:
        print("  prism scan is an obstruction to excluding N=6 at Z=3")
    else:
        print("  prism scan does not sit below 0.6")
    print()


def main() -> None:
    if not (mpf("0.6283") < lam_s2() < mpf("0.6284")):
        raise SystemExit(f"λ_s2={lam_s2()} outside q1 window")
    rows = envelopes()
    check_known(rows)
    print_envelopes(rows)
    identities()
    geometry()
    print(
        "RESIDUE. Best published integer bound at Z=2..6 is still Lieb "
        "Nc<=2Z. Z=6 is the first integer where Nam and HPS s=2 sit "
        "below 2Z+1 as reals; both still have U>12. Local a(2+1/Z) "
        "and (7.10)/(7.6) at N=2Z do not exclude an extra integer. "
        "5-octa blocks N=5 at Z=3 by pair geometry (128<169), same "
        "kind of obstruction as tetra 54<64, not a dent. "
        "Hydrogen uniqueness is Lieb 1984 and is not claimed."
    )


if __name__ == "__main__":
    main()
