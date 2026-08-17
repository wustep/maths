#!/usr/bin/env python3
"""Independent replay of the elementary Bambah–Chowla bound.

For every n in [1, N]:
    u = floor(sqrt(n)), v = ceil(sqrt(n-u^2))
    0 <= u^2+v^2 - n < 2*sqrt(2)*n^{1/4} + 1

Uses integer comparisons:  (u^2+v^2-n)^4 < 64 n   is not quite right
because of the +1. We check the exact integer identity from the
standard proof:

    leftover = 2*v - r    where r = (n-u^2) wait no.

Proof we replay, exactly:
    rem = n - u^2 >= 0
    v = ceil(sqrt(rem)) so rem <= v^2 < rem + 2*sqrt(rem) + 1
    hence 0 <= u^2+v^2-n < 2*sqrt(rem)+1
    rem <= n - (isqrt(n))^2 <= 2*isqrt(n)     (since (u+1)^2-1-u^2 = 2u)
    and if n is a square rem=0 leftover=0.
    2*sqrt(rem)+1 <= 2*sqrt(2*u)+1
    and 2*sqrt(2*u)+1 <= 2*sqrt(2)*n^{1/4}+1 because u <= sqrt(n).

We also check Jameson's a=2 against the same BC leftover plus the
competitor (u+1)^2, for every n in range: min(h_BC, (u+1)^2-n) < Phi-2
is the published claim we must not over-claim; we just measure how
often a=3 already holds from these two points alone.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import bc_point, isqrt, phi_bc  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=200_000)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    two_sqrt2 = 2.0 * math.sqrt(2.0)
    worst_over = 0.0
    worst_n = 1
    fail_plus1 = 0
    fail_a2_two_pts = 0
    fail_a3_two_pts = []
    max_ratio = 0.0
    max_ratio_n = 1

    for n in range(1, args.N + 1):
        u, v, s = bc_point(n)
        h = s - n
        if h < 0:
            raise RuntimeError(f"BC point below n at {n}")
        rem = n - u * u
        # integer proof of leftover < 2*sqrt(rem)+1
        # v^2 - rem < 2*v  because v^2 - (v-1)^2 = 2v-1, and rem > (v-1)^2
        # so leftover = v^2-rem <= 2v-1
        if rem == 0:
            leftover_int_bound = 0
        else:
            leftover_int_bound = 2 * v - 1
        if h > leftover_int_bound:
            raise RuntimeError(f"leftover {h} > 2v-1={leftover_int_bound} at n={n}")
        phi = two_sqrt2 * n ** 0.25
        if h >= phi + 1:
            fail_plus1 += 1
        ratio = h / (n ** 0.25)
        if ratio > max_ratio:
            max_ratio = ratio
            max_ratio_n = n
        over = h - phi
        if over > worst_over:
            worst_over = over
            worst_n = n

        next_sq = (u + 1) * (u + 1)
        h2 = next_sq - n
        m2 = min(h, h2)
        if m2 >= phi - 2:
            fail_a2_two_pts += 1
        if m2 >= phi - 3:
            fail_a3_two_pts.append(
                {"n": n, "u": u, "v": v, "h_bc": h, "h_nextsq": h2, "phi": phi}
            )

    summary = {
        "N": args.N,
        "fail_plus1": fail_plus1,
        "fail_a2_two_pts": fail_a2_two_pts,
        "n_fail_a3_two_pts": len(fail_a3_two_pts),
        "fail_a3_two_pts_head": fail_a3_two_pts[:30],
        "fail_a3_two_pts_tail": fail_a3_two_pts[-10:],
        "max_BC_ratio": {"n": max_ratio_n, "ratio": max_ratio},
        "worst_h_minus_phi": {"n": worst_n, "over": worst_over},
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: summary[k] for k in summary if "head" not in k and "tail" not in k}, indent=2))
    print("n_fail_a3_sample", [r["n"] for r in fail_a3_two_pts[:20]])


if __name__ == "__main__":
    main()
