#!/usr/bin/env python3
"""Replay published examples with two independent LE counters."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from posetlib import (
    Poset,
    T_poset,
    antichain,
    balance,
    chain,
    chen_poset,
    count_le_ideals,
    count_le_mins,
    delta_frac,
    hook_rectangle,
    linear_sum,
    pair_counts_by_adding,
    pair_counts_fb,
    product_of_chains,
    young_diagram,
)


def check_counters(P: Poset, name: str) -> int:
    e1 = count_le_ideals(P)
    e2 = count_le_mins(P)
    if e1 != e2:
        raise AssertionError(f"{name}: ideals {e1} != mins {e2}")
    return e1


def check_pairs(P: Poset, name: str, expect_delta=None):
    e_fb, C_fb = pair_counts_fb(P)
    e_add, C_add = pair_counts_by_adding(P)
    if e_fb != e_add:
        raise AssertionError(f"{name}: e_fb {e_fb} != e_add {e_add}")
    n = P.n
    for x in range(n):
        for y in range(n):
            if C_fb[x][y] != C_add[x][y]:
                raise AssertionError(
                    f"{name}: C[{x},{y}] fb={C_fb[x][y]} add={C_add[x][y]}"
                )
    num, den, e, pair, _ = balance(P, C_fb, e_fb)
    g = _gcd(num, den)
    frac = (num // g, den // g)
    print(
        f"  {name}: n={n} e={e} δ={frac[0]}/{frac[1]}"
        f" pair={pair}"
    )
    if expect_delta is not None:
        if frac != expect_delta:
            raise AssertionError(f"{name}: got {frac} expected {expect_delta}")
    return {
        "name": name,
        "n": n,
        "e": e,
        "delta": [frac[0], frac[1]],
        "pair": list(pair) if pair else None,
    }


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def find_saks_M7():
    """Enumerate naturally labelled 7-element posets of width 3; list δ=14/39."""
    # Recursively add a new maximal element whose down-set is an ideal.
    from posetlib import downsets_from_succ

    found = []

    def ideals_of(down):
        n = len(down)
        out = [0]
        for mask in range(1, 1 << n):
            ok = True
            m = mask
            while m:
                lsb = m & -m
                i = lsb.bit_length() - 1
                if down[i] & ~mask:
                    ok = False
                    break
                m ^= lsb
            if ok:
                out.append(mask)
        return out

    def rec(down):
        n = len(down)
        if n == 7:
            P = Poset(7, down)
            # width: skip if no 3-antichain
            w = P.width_lower()
            if w < 3:
                return
            e, C = pair_counts_fb(P)
            num, den, _, pair, _ = balance(P, C, e)
            if num * 39 == den * 14:
                covers = []
                for i in range(7):
                    for j in range(7):
                        if (P.succ[i] >> j) & 1:
                            # cover? no k with i < k < j
                            is_cover = True
                            for k in range(7):
                                if k == i or k == j:
                                    continue
                                if ((P.succ[i] >> k) & 1) and ((P.succ[k] >> j) & 1):
                                    is_cover = False
                                    break
                            if is_cover:
                                covers.append((i, j))
                found.append(
                    {
                        "down": down[:],
                        "e": e,
                        "pair": pair,
                        "covers": covers,
                        "width": w,
                    }
                )
            return
        for I in ideals_of(down):
            rec(down + [I])

    rec([])
    return found


def find_olson_C():
    """Width-2 posets on 9 elements are many; reconstruct Fig. 13 C by
    two-chain search: partitions 5+4, enumerate Ferrers crosses, match 37/106.
    """
    # left chain 0<1<2<3<4, right 5<6<7<8
    # A relation a_i < b_j (i=0..4, j=0..3) is a top-right Ferrers:
    #   a_i < b_j iff j >= s[i], s weakly increasing in {0..4}
    # B relation b_j < a_i iff i >= v[j], v weakly increasing in {0..5}
    # nonoverlap: not (j >= s[i] and i >= v[j])
    from itertools import combinations_with_replacement

    hits = []

    def incr_seq(length, lo, hi):
        # weakly increasing sequences of given length with values in [lo, hi]
        # hi is exclusive? values in lo..hi inclusive
        # equivalent to combinations with replacement then sort
        vals = range(lo, hi + 1)
        for comb_ in combinations_with_replacement(vals, length):
            yield comb_

    for s in incr_seq(5, 0, 4):
        for v in incr_seq(4, 0, 5):
            ok = True
            for i in range(5):
                for j in range(4):
                    if j >= s[i] and i >= v[j]:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            covers = [(i, i + 1) for i in range(4)] + [
                (5 + j, 6 + j) for j in range(3)
            ]
            for i in range(5):
                for j in range(4):
                    if j >= s[i]:
                        covers.append((i, 5 + j))
                    if i >= v[j]:
                        covers.append((5 + j, i))
            P = Poset.from_covers(9, covers)
            e, C = pair_counts_fb(P)
            num, den, _, pair, _ = balance(P, C, e)
            if num * 106 == den * 37:
                hits.append(
                    {
                        "s": list(s),
                        "v": list(v),
                        "e": e,
                        "pair": pair,
                        "covers": covers,
                    }
                )
    return hits


def main():
    out = {"checks": []}

    print("=== unit: two counters on tiny posets ===")
    for name, P, exp_e in [
        ("chain3", chain(3), 1),
        ("antichain3", antichain(3), 6),
        ("T", T_poset(), 3),
        ("C2xC2", product_of_chains((2, 2)), 2),
        ("C2xC3", product_of_chains((2, 3)), hook_rectangle(2, 3)),
        ("Y(3,2,1)", young_diagram([3, 2, 1]), None),
    ]:
        e = check_counters(P, name)
        if exp_e is not None and e != exp_e:
            raise AssertionError(f"{name}: e={e} expected {exp_e}")
        print(f"  {name}: e={e} OK")

    print("=== published δ values ===")
    out["checks"].append(check_pairs(T_poset(), "T", (1, 3)))
    Aig = linear_sum(T_poset(), chain(1))
    Aig = linear_sum(Aig, T_poset())
    out["checks"].append(
        check_pairs(Aig, "T ⊕ 1 ⊕ T (Aigner type)", (1, 3))
    )
    out["checks"].append(
        check_pairs(product_of_chains((2, 3)), "C2xC3", None)
    )
    out["checks"].append(
        check_pairs(young_diagram([4, 4, 2]), "Y(4,4,2)", None)
    )

    print("=== Chen P(m,n) small table vs arXiv:1709.05753 Appendix ===")
    # Chen E(m,n) for the poset itself (not δ). Check a few bold admissible pairs.
    chen_E = {
        (1, 1): 2,
        (2, 2): 5,
        (3, 3): 14,
        (4, 4): 37,
        (5, 5): 106,
        (5, 4): 69,
        (5, 3): 32,
    }
    for (m, n), exp in chen_E.items():
        P = chen_poset(m, n)
        e = check_counters(P, f"Chen({m},{n})")
        if e != exp:
            raise AssertionError(f"Chen({m},{n}): e={e} expected {exp}")
        print(f"  Chen({m},{n}): e={e} OK")
    out["chen_E_ok"] = True

    print("=== hunt Saks M7 (δ=14/39, width 3, n=7) ===")
    found = find_saks_M7()
    print(f"  hits: {len(found)}")
    # unique up to the natural-labelling multiplicity
    cover_sets = []
    for h in found:
        key = tuple(sorted(h["covers"]))
        if key not in cover_sets:
            cover_sets.append(key)
            print(f"  covers={h['covers']} e={h['e']} pair={h['pair']}")
    out["M7_hits"] = len(found)
    out["M7_iso_types"] = [list(k) for k in cover_sets]
    if found:
        out["M7_example_covers"] = found[0]["covers"]
        out["M7_e"] = found[0]["e"]

    print("=== hunt Olson C (δ=37/106, width 2, 5+4 chains) ===")
    chits = find_olson_C()
    print(f"  hits: {len(chits)}")
    for h in chits[:5]:
        print(f"  s={h['s']} v={h['v']} e={h['e']} pair={h['pair']}")
    out["olsonC_hits"] = len(chits)
    if chits:
        out["olsonC_example"] = {
            "s": chits[0]["s"],
            "v": chits[0]["v"],
            "e": chits[0]["e"],
            "covers": chits[0]["covers"],
            "pair": list(chits[0]["pair"]) if chits[0]["pair"] else None,
        }

    path = Path(__file__).resolve().parent / "known.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
