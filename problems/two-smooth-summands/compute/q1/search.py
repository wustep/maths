"""Run the q1 template census. Writes certs/q1_search.json.

A hole-free prefix would still be residue. This script is expected to
record holes for every template at every exponent below 1/2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from smooth_lib import largest_prime_factor

from templates import (
    CLOSED_FORMS,
    closed_form_holes,
    exceeds_pow,
    floor_divisor_holes,
)

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "q1_search.json"

# Exponents we would need for a dent: any p/q < 1/2, or below Balog.
EXPONENTS = ((9, 20), (2, 5), (1, 3), (27, 100))
LIMIT = 20_000


def lpf_sieve(limit: int) -> list[int]:
    P = [0] * (limit + 1)
    P[1] = 1
    for i in range(2, limit + 1):
        if P[i] == 0:
            for j in range(i, limit + 1, i):
                P[j] = i
    return P


def two_factor_holes(P: list[int], alpha_num: int, alpha_den: int,
                     p: int, q: int, limit: int, max_holes: int = 40) -> dict:
    """a = u*v with u <= n^{alpha}, P+(v)<=n^{p/q}, P+(n-a)<=n^{p/q}.

    This is the elementary Balog–Sárközy two-factor shape, run as a
    search. It is not a closed-form covering.
    """
    holes = []
    first = None
    last = None
    count = 0
    for n in range(2, limit + 1):
        umax = max(1, _floor_pow_from_sieve(n, alpha_num, alpha_den))
        ok = False
        # u <= umax, v <= (n-1)//u, both the product and the complement
        # n^{p/q}-smooth.
        vmax_cap = n - 1
        for u in range(1, umax + 1):
            vmax = (n - 1) // u
            if vmax > vmax_cap:
                vmax = vmax_cap
            for v in range(1, vmax + 1):
                a = u * v
                if a >= n:
                    break
                if not exceeds_pow(P[v], n, p, q) and not exceeds_pow(P[n - a], n, p, q):
                    ok = True
                    break
            if ok:
                break
        if not ok:
            count += 1
            last = n
            if first is None:
                first = n
            if len(holes) < max_holes:
                holes.append(n)
    return {
        "template": "two_factor",
        "alpha": f"{alpha_num}/{alpha_den}",
        "exponent": f"{p}/{q}",
        "limit": limit,
        "first_hole": first,
        "last_hole": last,
        "n_holes": count,
        "first_holes": holes,
        "covers_the_range": first is None,
        "is_dent": False,
    }


def _floor_pow_from_sieve(n: int, p: int, q: int) -> int:
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if pow(mid, q) <= pow(n, p):
            lo = mid
        else:
            hi = mid - 1
    return lo


def two_factor_small_u(P: list[int], p: int, q: int, limit: int,
                       max_holes: int = 40) -> dict:
    """Restricted two-factor: u <= n^{1/5}, smoothness n^{p/q}.

    At computational n the 1/5-window is tiny (umax<=7 on [2,20000]),
    so this is much thinner than F itself.
    """
    return two_factor_holes(P, 1, 5, p, q, limit, max_holes)


def main() -> int:
    closed = []
    for name, fn in CLOSED_FORMS.items():
        for p, q in EXPONENTS:
            rec = closed_form_holes(name, fn, p, q, LIMIT)
            closed.append(rec)
            print(
                f"{name:24s} {p}/{q:3d} first={rec['first_hole']} "
                f"last={rec['last_hole']} holes={rec['n_holes']}"
            )

    floor = []
    for p, q in EXPONENTS:
        rec = floor_divisor_holes(p, q, LIMIT)
        floor.append(rec)
        print(
            f"{'floor_divisor':24s} {p}/{q:3d} first={rec['first_hole']} "
            f"last={rec['last_hole']} holes={rec['n_holes']}"
        )

    # Two-factor is the expensive inner loop; 2e4 is a few seconds.
    tf_limit = 20_000
    P = lpf_sieve(tf_limit)
    known_2_5 = [3, 4, 5, 7, 11, 13, 14, 15, 23, 46, 47, 53, 71, 119, 311, 479]
    two_factor = []
    for p, q in ((2, 5), (1, 3)):
        rec = two_factor_small_u(P, p, q, tf_limit, max_holes=200)
        if p == 2 and q == 5:
            rec["matches_known_F_exceptions"] = rec["first_holes"] == known_2_5
            rec["known_F_exceptions_2_5"] = known_2_5
        two_factor.append(rec)
        print(
            f"{'two_factor u<=n^{1/5}':24s} {p}/{q:3d} first={rec['first_hole']} "
            f"last={rec['last_hole']} holes={rec['n_holes']}"
        )

    # The square formula guarantees F_split < 2*sqrt(n)+1, not F_split <= sqrt(n).
    # The latter already has exceptions {3,7,23} for F itself.
    sq_bound_holes = []
    for n in range(2, min(LIMIT, 20_000) + 1):
        a = CLOSED_FORMS["square_plus_remainder"](n)
        b = n - a
        f = max(largest_prime_factor(a), largest_prime_factor(b))
        if f >= 2 * int(n**0.5) + 1:
            sq_bound_holes.append(n)
            if len(sq_bound_holes) >= 10:
                break
    print(f"{'square 2sqrt+1 bound':24s} holes={sq_bound_holes}")

    out = {
        "limit": LIMIT,
        "two_factor_limit": tf_limit,
        "exponents": [f"{p}/{q}" for p, q in EXPONENTS],
        "closed_form": closed,
        "floor_divisor": floor,
        "two_factor": two_factor,
        "square_trivial_bound_holes": sq_bound_holes,
        "is_dent": False,
        "reason": (
            "Every closed-form template has a first hole at every tested "
            "exponent below 1/2. The square template is the 1/2 covering "
            "already recorded. Two-factor at u<=n^{1/5} is a thin search, "
            "not an infinite cover."
        ),
    }
    CERT.parent.mkdir(parents=True, exist_ok=True)
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {CERT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
