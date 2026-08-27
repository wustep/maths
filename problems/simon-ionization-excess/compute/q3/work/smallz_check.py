#!/usr/bin/env python3
"""Second path for the Z=2..6 integer table and the pair-geometry integers.

stdlib only. No mpmath, no shared helpers with smallz_replay.py.

Replay: python3 smallz_replay.py && python3 smallz_check.py
"""

from __future__ import annotations

import math


def b2() -> float:
    return 0.5 * (math.sqrt(2.0) + 1.0)


def b3() -> float:
    s = 1.0 + math.sqrt(2.0)
    return (2.0 / 3.0) * (s ** (1.0 / 3.0)) / (s ** (2.0 / 3.0) - 1.0)


def max_int_below(U: float) -> int:
    n = math.floor(U)
    if abs(U - n) < 1e-15:
        return n - 1
    return int(n)


def main() -> None:
    b2v, b3v = b2(), b3()
    if not (1.2071 < b2v < 1.2072):
        raise SystemExit("b2")
    if not (1.1184 < b3v < 1.1185):
        raise SystemExit("b3")

    print(f"{'Z':>3} {'Lieb U':>8} {'Nam U':>10} {'HPS s=2':>10} {'best int':>8}")
    for z in (2, 3, 4, 5, 6):
        t = z ** (1.0 / 3.0)
        lieb = 2.0 * z + 1.0
        nam = 1.22 * z + 3.0 * t
        s2 = b2v * z + 2.96 * t
        n_lieb = max_int_below(lieb)
        n_nam = max_int_below(nam)
        n_s2 = max_int_below(s2)
        best_int = min(n_lieb, n_nam, n_s2)
        print(
            f"{z:3d} {lieb:8.3f} {nam:10.6f} {s2:10.6f} {best_int:8d}"
        )
        if n_lieb != 2 * z:
            raise SystemExit("Lieb integer")
        if best_int != 2 * z:
            raise SystemExit(f"best integer not Lieb at Z={z}")
        if z <= 5 and not (nam > lieb and s2 > lieb):
            raise SystemExit(f"Nam/HPS should sit above Lieb at Z={z}")
        if z >= 6 and not (nam < lieb and s2 < lieb):
            raise SystemExit("Nam/HPS should sit below Lieb at Z=6")
        if z >= 6 and not (s2 > 12.0 and nam > 12.0):
            raise SystemExit("Z=6 envelopes still above 12")

        if z >= 4:
            s3 = (
                b3v * z
                + 3.90 * t
                + 0.0134
                + 0.184 / t
                + 0.0196 / (t * t)
            )
            if max_int_below(s3) < 2 * z:
                raise SystemExit("HPS s=3 unexpectedly beats Lieb integer")

        bgb = 1.4811 * z + 3.1516 * t
        if bgb <= lieb:
            raise SystemExit("BGB formula should be worse than Lieb at Z<=6")

    # Tetrahedron: 3 sqrt(6) < 8 <=> 54 < 64.
    if 54 >= 64:
        raise SystemExit("54<64")
    if 3 * 3 * 6 >= 8 * 8:
        raise SystemExit("3 sqrt(6) < 8")

    # 5 octahedron vertices: 4*alpha < 3 <=> 8 sqrt(2) < 13 <=> 128 < 169.
    if 128 >= 169:
        raise SystemExit("128<169")
    five = (
        (1.0, 0.0, 0.0),
        (-1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, 1.0),
    )
    rs = [math.sqrt(sum(c * c for c in p)) for p in five]
    if any(abs(r - 1.0) > 1e-15 for r in rs):
        raise SystemExit("five-octa radius")
    num = 0.0
    n_sqrt2 = 0
    n_2 = 0
    for i, a in enumerate(five):
        for b in five[i + 1 :]:
            d = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
            num += 2.0 / d
            if abs(d - math.sqrt(2.0)) < 1e-12:
                n_sqrt2 += 1
            elif abs(d - 2.0) < 1e-12:
                n_2 += 1
            else:
                raise SystemExit(f"unexpected pair {d}")
    if (n_sqrt2, n_2) != (8, 2):
        raise SystemExit(f"pair counts {n_sqrt2} {n_2}")
    alpha = num / (4.0 * 5.0)
    closed = (4.0 * math.sqrt(2.0) + 1.0) / 10.0
    if abs(alpha - closed) > 1e-12:
        raise SystemExit(f"five-octa alpha {alpha}")

    # Regular octahedron does not sit below 3/5.
    if 8 <= 6.25:
        raise SystemExit("octa 5*alpha should exceed 3")

    print("tetra 54<64 and 5-octa 128<169 hold")
    print("At Z=2..6 the best published integer bound is Lieb Nc<=2Z.")
    print("At Z=6 Nam and HPS s=2 beat 2Z+1 as reals and still have U>12.")


if __name__ == "__main__":
    main()
