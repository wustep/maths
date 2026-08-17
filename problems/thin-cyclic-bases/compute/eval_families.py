#!/usr/bin/env python3
"""Evaluate named constructions on a range of n / prime powers."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, is_sum_cover
from constructions import two_ap, three_ap, mrose, bel_product, bose_set

BEL = math.sqrt(8 / 3)
SQRT3 = math.sqrt(3)
SQRT2 = math.sqrt(2)


def eval_two_ap(ns):
    rows = []
    for n in ns:
        A = two_ap(n)
        st = cover_stats(A, n)
        st["family"] = "two_ap"
        rows.append(st)
        assert st["ok"], f"two_ap failed at n={n}"
    return rows


def eval_mrose(ts):
    rows = []
    for t in ts:
        n, A = mrose(t)
        st = cover_stats(A, n)
        st["family"] = "mrose"
        st["t"] = t
        rows.append(st)
        # Mrose is an interval basis: S+S covers [0, 14t^2+10t-1],
        # so as a cyclic cover of Z/nZ with n = 14t^2+10t it must include n-1.
        # We set n = 14t^2+10t so the last covered integer is n-1.
    return rows


def eval_bel(qs):
    rows = []
    for q in qs:
        got = bel_product(q)
        if got is None:
            rows.append({"family": "bel", "q": q, "ok": False, "error": "params"})
            continue
        n, A = got
        st = cover_stats(A, n)
        st["family"] = "bel"
        st["q"] = q
        rows.append(st)
        print(
            f"BEL q={q} n={n} m={st['m']} ratio={st['ratio']:.5f} "
            f"ok={st['ok']} bel={BEL:.5f}",
            flush=True,
        )
    return rows


def eval_three_ap_grid(ns, ells=None):
    """Brute a few (d,e) near the √3 regime."""
    rows = []
    for n in ns:
        ell = math.ceil(math.sqrt(n / 3))
        best = None
        for d in (ell, ell + 1, 2 * ell, 2 * ell + 1, 3 * ell, n // 3):
            for e in (2 * ell, 2 * ell + 1, 3 * ell, 3 * ell + 1, d + 1, n // 2):
                if e % n == d % n:
                    continue
                A = three_ap(n, d, e, ell)
                st = cover_stats(A, n)
                st["family"] = "three_ap"
                st["d"] = d
                st["e"] = e
                st["ell"] = ell
                if best is None or (st["covered"], -st["m"]) > (
                    best["covered"],
                    -best["m"],
                ):
                    best = st
                if st["ok"] and st["ratio"] < BEL:
                    rows.append(st)
                    break
            else:
                continue
            break
        if best and not (best["ok"] and best["ratio"] < BEL):
            rows.append(best)
    return rows


def main():
    out = {}
    print("== two_ap ==")
    out["two_ap"] = eval_two_ap([10, 25, 50, 100, 200, 400])
    print("== mrose ==")
    out["mrose"] = eval_mrose([2, 3, 4, 5, 8])
    for r in out["mrose"]:
        print(
            f"  t={r['t']} n={r['n']} m={r['m']} ok={r['ok']} "
            f"covered={r['covered']} ratio={r['ratio']:.4f}"
        )
    print("== bel ==")
    out["bel"] = eval_bel([7, 13, 19, 25, 31])
    print("== three_ap sample ==")
    out["three_ap"] = eval_three_ap_grid([12, 27, 48, 75, 108])
    for r in out["three_ap"]:
        print(
            f"  n={r['n']} m={r['m']} ok={r['ok']} covered={r['covered']} "
            f"ratio={r['ratio']:.4f} d={r.get('d')} e={r.get('e')}"
        )
    Path("compute/family_eval.json").write_text(json.dumps(out, indent=2))
    print("wrote compute/family_eval.json")


if __name__ == "__main__":
    main()
