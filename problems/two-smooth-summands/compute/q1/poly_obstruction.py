"""Polynomial-value templates cannot beat the square covering by size.

If the first summand is P(k) for a fixed polynomial P of degree d >= 2
with positive leading coefficient, and k is maximal with P(k) < n, then
the remainder n - P(k) is at most P(k+1) - P(k) - 1 ~ d k^{d-1}. In n
this is << n^{1-1/d}. Since 1-1/d >= 1/2, bounding the remainder by its
size only recovers F(n) << n^{1-1/d}, which is no better than the square
template (d=2) and is worse for d>=3.

This does not forbid a remainder of size n^{1-1/d} from happening to be
n^ε-smooth. That is the square-adjustment search already run on
[2, 80000], which left holes.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "poly_obstruction.json"


def eval_poly(name: str, k: int) -> int:
    if name == "x^2":
        return k * k
    if name == "x^3":
        return k * k * k
    if name == "x(x+1)":
        return k * (k + 1)
    if name == "x(x+1)/2":
        return k * (k + 1) // 2
    if name == "x^2+x+1":
        return k * k + k + 1
    if name == "x(x+1)(x+2)/6":
        return k * (k + 1) * (k + 2) // 6
    raise KeyError(name)


POLYS = [
    ("x^2", 2),
    ("x^3", 3),
    ("x(x+1)", 2),
    ("x(x+1)/2", 2),
    ("x^2+x+1", 2),
    ("x(x+1)(x+2)/6", 3),
]


def gap_ratio(name: str, degree: int, k: int) -> dict:
    pk = eval_poly(name, k)
    pk1 = eval_poly(name, k + 1)
    gap = pk1 - pk
    # n just below P(k+1) has remainder gap-1, and n ~ P(k+1) ~ k^d.
    n = pk1 - 1
    # Compare gap to n^{1-1/d} = n^{(d-1)/d}. Use integers: gap^d vs n^{d-1}.
    return {
        "k": k,
        "P_k": pk,
        "gap": gap,
        "n_at_max_remainder": n,
        "max_remainder": gap - 1,
        "gap_d": pow(gap, degree),
        "n_d_minus_1": pow(n, degree - 1),
        "gap_beats_half_window": 2 * (gap - 1) >= gap,  # tautological audit
    }


def main() -> int:
    rows = []
    ok = True
    for name, deg in POLYS:
        # Leading-term check on a handful of large k.
        samples = []
        for k in (20, 50, 100, 200, 400):
            rec = gap_ratio(name, deg, k)
            samples.append(rec)
            # gap ~ deg * k^{deg-1}, n ~ k^deg, so gap^d / n^{d-1} -> deg^d.
            # We only need the weaker size lower bound gap-1 >= k^{deg-1}/2
            # for large k, which forces remainder exponent 1-1/d.
            if rec["max_remainder"] < (k ** (deg - 1)) // 2:
                ok = False
        rows.append(
            {
                "poly": name,
                "degree": deg,
                "remainder_exponent": f"1-1/{deg}",
                "beats_square_by_size": deg < 2,
                "samples": samples,
            }
        )
    out = {
        "statement": (
            "A fixed polynomial of degree d>=2 produces remainder windows "
            "of exponent 1-1/d >= 1/2. Size-of-remainder covering therefore "
            "cannot beat the square template."
        ),
        "polys": rows,
        "is_dent": False,
        "size_lower_bound_holds": ok,
    }
    CERT.parent.mkdir(parents=True, exist_ok=True)
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"poly size lower bound ok={ok}")
    print(f"wrote {CERT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
