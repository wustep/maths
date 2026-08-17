#!/usr/bin/env python3
"""Summarise extra homometric classes: non-reciprocal factor degrees."""

from __future__ import annotations

import json
import os
import re
from collections import Counter


def parse_deg(s: str) -> int:
    # 'x**5 - x**3 + 1' or 'x + 1' or 'x**2 + 1'
    if s.strip() in ("x + 1", "x+1"):
        return 1
    m = re.search(r"x\*\*(\d+)", s)
    if m:
        return int(m.group(1))
    if s.strip().startswith("x"):
        return 1
    return 0


def is_recip_expr(s: str) -> bool:
    """Crude: cyclotomic-looking or palindromic coefficient list.

    We rely on the stored factor lists from sympy; mark known reciprocals
    by comparing a member to another member's factors in the same class.
    Here just detect obvious reciprocal cyclotomics.
    """
    s = s.replace(" ", "")
    obvious = {
        "x+1",
        "x**2+1",
        "x**2+x+1",
        "x**2-x+1",
        "x**4+x**3+x**2+x+1",
        "x**4+1",
        "x**6+x**3+1",
    }
    return s in obvious


def main() -> None:
    path = os.path.join(os.path.dirname(__file__), "homometric_pairs.json")
    with open(path) as f:
        data = json.load(f)
    print("n  classes  members  min_nr_deg_hist")
    for n_s, extras in data["extras"].items():
        n = int(n_s)
        min_hist = Counter()
        members = 0
        for ex in extras:
            facs = ex.get("factorizations")
            if not facs:
                continue
            # take first member
            degs = []
            for expr, _e in facs[0]:
                if not is_recip_expr(expr):
                    degs.append(parse_deg(expr))
            if degs:
                min_hist[min(degs)] += 1
            members += len(ex["members"])
        hist = " ".join(f"{d}:{c}" for d, c in sorted(min_hist.items()))
        print(f"{n:2d}  {len(extras):4d}  {members:5d}  {hist}")


if __name__ == "__main__":
    main()
