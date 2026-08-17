#!/usr/bin/env python3
"""Exact G(y) = first n not in S_y + S_y, via word bitset coverage.

For y <= 61 this is a few seconds. Larger y should use g_of_y.c.
A hole-free prefix is not an asymptotic bound.
"""

from __future__ import annotations

import argparse
import array
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smooth_lib import primes_upto, smooth_upto

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "g_of_y.json"

# Published A062241 / July-report values, to be independently reproduced.
# Keyed by y = smoothness bound.
PUBLISHED_G = {
    1: 3,
    2: 7,
    3: 23,
    5: 71,
    7: 311,
    11: 479,
    13: 1559,
    17: 5711,
    19: 10559,
    23: 18191,
    29: 31391,
    31: 118271,
    37: 366791,
    41: 366791,
    43: 2155919,
    47: 2155919,
    53: 2155919,
    59: 6077111,
    61: 6077111,
}


def bitset_from_list(values: list[int], limit: int) -> array.array:
    nwords = (limit >> 6) + 1
    bits = array.array("Q", [0]) * nwords
    for v in values:
        if 0 <= v <= limit:
            bits[v >> 6] |= 1 << (v & 63)
    return bits


def shift_or(dst: array.array, src: array.array, shift: int, limit: int) -> None:
    """dst |= src << shift, bits above limit ignored."""
    nwords = (limit >> 6) + 1
    aw = shift >> 6
    ab = shift & 63
    mask = (1 << 64) - 1
    if ab == 0:
        for i in range(nwords - aw):
            dst[i + aw] |= src[i]
    else:
        for i in range(nwords - aw):
            dst[i + aw] |= (src[i] << ab) & mask
            if i + aw + 1 < nwords:
                dst[i + aw + 1] |= src[i] >> (64 - ab)
    # Clear bits > limit in the last word.
    extra = (nwords << 6) - 1 - limit
    if extra > 0:
        dst[-1] &= mask >> extra


def first_missing(bits: array.array, limit: int, start: int = 2) -> int | None:
    for n in range(start, limit + 1):
        if ((bits[n >> 6] >> (n & 63)) & 1) == 0:
            return n
    return None


def two_pointer_has_sum(smooth: list[int], target: int) -> bool:
    i, j = 0, len(smooth) - 1
    while i <= j:
        s = smooth[i] + smooth[j]
        if s == target:
            return True
        if s < target:
            i += 1
        else:
            j -= 1
    return False


def compute_G(y: int, search_limit: int, small_bound: int) -> dict:
    smooth = smooth_upto(search_limit, y)
    # 1 is included; we need positive summands, 1 is allowed.
    src = bitset_from_list(smooth, search_limit)
    covered = array.array("Q", [0]) * ((search_limit >> 6) + 1)
    small = [s for s in smooth if 1 <= s <= small_bound]
    for a in small:
        shift_or(covered, src, a, search_limit)
    hole = first_missing(covered, search_limit, 2)
    return {
        "y": y,
        "search_limit": search_limit,
        "small_bound": small_bound,
        "n_smooth": len(smooth),
        "n_small": len(small),
        "first_uncovered": hole,
        "published": PUBLISHED_G.get(y),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--y-max", type=int, default=61)
    ap.add_argument("--y", type=int, default=None)
    args = ap.parse_args()

    ys = [args.y] if args.y is not None else [y for y in PUBLISHED_G if y <= args.y_max]
    rows = []
    mismatches = []
    for y in ys:
        pub = PUBLISHED_G.get(y)
        if pub is None:
            print(f"no published G({y}) in table; skip")
            continue
        # Search a little past the published value so a smaller hole would show.
        limit = pub
        # One summand at most 2*y*log(limit)^2 is plenty once average gaps are
        # smaller than that; we take a conservative fraction of the limit.
        small_bound = min(limit, max(10_000, limit // 20))
        rec = compute_G(y, limit, small_bound)
        # The published G(y) itself must be uncovered, and nothing smaller.
        rec["matches_published"] = rec["first_uncovered"] == pub
        S = smooth_upto(pub, y)
        rec["published_has_representation"] = two_pointer_has_sum(S, pub)
        rec["uncovered_is_false_hole"] = False
        if rec["first_uncovered"] is not None and rec["first_uncovered"] < pub:
            rec["uncovered_is_false_hole"] = two_pointer_has_sum(
                [s for s in S if s < rec["first_uncovered"]], rec["first_uncovered"]
            )
        rec["G_certified"] = rec["matches_published"] and not rec["published_has_representation"]
        if not rec["G_certified"]:
            mismatches.append(rec)
        rows.append(rec)
        print(
            f"y={y:3d} G_pub={pub:10d} first_uncovered={rec['first_uncovered']} "
            f"n_smooth={rec['n_smooth']} cert={rec['G_certified']}"
        )

    out = {
        "rows": rows,
        "mismatches": mismatches,
        "is_dent": False,
        "reason": "Finite G(y) table. Search residue, not an exponent.",
    }
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {CERT}")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
