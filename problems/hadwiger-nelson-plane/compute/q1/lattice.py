#!/usr/bin/env python3
"""Generate candidate vertices from Parts' base lattice and the ρ rotation.

Unrotated vertices of the type-M graphs sit in the Minkowski-sum lattice

    (a + b√33 + i c√3 + i d√11) / 12,   a,b,c,d even,  a-b+c+d ≡ 0 (mod 4).

The small subgraph is then rotated by ρ = exp(i arccos(7/8)), i.e.
cos ρ = 7/8 and sin ρ = √15/8.  New vertices are taken from this exact
set; nothing is invented numerically.
"""

from __future__ import annotations

from udg import F, sqrt_of

S3 = sqrt_of(F.from_int(3))
S5 = sqrt_of(F.from_int(5))
S11 = sqrt_of(F.from_int(11))
S15 = S3 * S5
S33 = S3 * S11
TWELVE = F.from_int(12)
COS_RHO = F.from_int(7) / 8
SIN_RHO = S15 / 8


def lattice_point(a: int, b: int, c: int, d: int) -> tuple[F, F]:
    x = (F.from_int(a) + F.from_int(b) * S33) / TWELVE
    y = (F.from_int(c) * S3 + F.from_int(d) * S11) / TWELVE
    return (x, y)


def rotate_rho(p: tuple[F, F]) -> tuple[F, F]:
    x, y = p
    return (x * COS_RHO - y * SIN_RHO, x * SIN_RHO + y * COS_RHO)


def legal_abcd(a: int, b: int, c: int, d: int) -> bool:
    # Published 509 vertices use both parities (e.g. (-5,1,3,-1)).
    # The congruence is the real lattice constraint from Parts.
    return (a - b + c + d) % 4 == 0


def radius2_times_144(a: int, b: int, c: int, d: int) -> F:
    """12^2 * (x^2+y^2) = (a + b√33)^2 + (c√3 + d√11)^2."""
    # (a^2 + 33 b^2 + 3 c^2 + 11 d^2) + (2ab)√33 + (2cd)√33
    # wait: (c√3)^2 = 3c^2, (d√11)^2 = 11d^2, 2cd √33
    # (a + b√33)^2 = a^2 + 33b^2 + 2ab √33
    rat = a * a + 33 * b * b + 3 * c * c + 11 * d * d
    s33 = 2 * a * b + 2 * c * d
    return F((rat, 0, 0, 0, 0, s33, 0, 0), 1)


def generate_disk(r_max: float = 2.5) -> list[tuple[tuple[int, int, int, int], tuple[F, F]]]:
    """All legal lattice points with Euclidean radius <= r_max."""
    # |a|/12 <= r_max, similarly roughly for others. √33≈5.74 so |b|<=12 r / 5.74
    lim_a = int(12 * r_max) + 2
    lim_b = int(12 * r_max / 5.744) + 2
    lim_c = int(12 * r_max / 1.732) + 2
    lim_d = int(12 * r_max / 3.317) + 2
    r2max = r_max * r_max
    out = []
    for a in range(-lim_a, lim_a + 1):
        for b in range(-lim_b, lim_b + 1):
            for c in range(-lim_c, lim_c + 1):
                for d in range(-lim_d, lim_d + 1):
                    if (a - b + c + d) % 4:
                        continue
                    # float radius gate then accept
                    xf = (a + b * 33**0.5) / 12.0
                    yf = (c * 3**0.5 + d * 11**0.5) / 12.0
                    if xf * xf + yf * yf > r2max + 1e-9:
                        continue
                    out.append(((a, b, c, d), lattice_point(a, b, c, d)))
    return out


def classify_unrotated(pts) -> list[tuple[int, int, int, int] | None]:
    """For each point, recover (a,b,c,d) if it is an unrotated lattice vertex."""
    rec = []
    for x, y in pts:
        # x should be (a + b√33)/12, y (c√3 + d√11)/12
        # so 12x = a + b√33, 12y = c√3 + d√11
        twelved_x = x * 12
        twelved_y = y * 12
        ok = (
            twelved_x.c[1] == 0
            and twelved_x.c[2] == 0
            and twelved_x.c[3] == 0
            and twelved_x.c[4] == 0
            and twelved_x.c[6] == 0
            and twelved_x.c[7] == 0
            and twelved_y.c[0] == 0
            and twelved_y.c[2] == 0
            and twelved_y.c[3] == 0
            and twelved_y.c[5] == 0
            and twelved_y.c[6] == 0
            and twelved_y.c[7] == 0
            and twelved_x.den == 1
            and twelved_y.den == 1
        )
        if not ok:
            rec.append(None)
            continue
        rec.append((twelved_x.c[0], twelved_x.c[5], twelved_y.c[1], twelved_y.c[4]))
    return rec
