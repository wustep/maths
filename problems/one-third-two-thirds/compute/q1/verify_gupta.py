#!/usr/bin/env python3
"""Independently recompute Gupta v2 named witnesses.

Witness strings are the published encodings from
https://github.com/agupta/gold-partition-conjecture/blob/main/data/census-n14.txt
(opened 2026-08-27). Counting uses this notebook's posetlib, not Gupta's
scripts.
"""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(HERE))

from posetlib import (  # noqa: E402
    Poset,
    W10,
    balance,
    pair_counts_by_adding,
    pair_counts_fb,
)
from ladders import ladder_poset, n_ordinal_summands  # noqa: E402


def decode_up(text: str) -> list[int]:
    n_s, hexpart = text.split(":")
    n = int(n_s)
    if len(hexpart) != 4 * n:
        raise ValueError(text)
    return [int(hexpart[4 * i : 4 * i + 4], 16) for i in range(n)]


def poset_from_up(up: list[int]) -> Poset:
    n = len(up)
    down = [0] * n
    for i, mask in enumerate(up):
        m = mask
        while m:
            lsb = m & -m
            j = lsb.bit_length() - 1
            down[j] |= 1 << i
            m ^= lsb
    return Poset(n, down)


def check(name: str, P: Poset, expect_delta, expect_e=None, expect_width=None):
    e1, C1 = pair_counts_fb(P)
    if P.n <= 12:
        e2, C2 = pair_counts_by_adding(P)
        if e1 != e2:
            raise AssertionError(f"{name} e {e1} vs {e2}")
        for x in range(P.n):
            for y in range(P.n):
                if C1[x][y] != C2[x][y]:
                    raise AssertionError(f"{name} C[{x},{y}]")
    num, den, e, pair, _ = balance(P, C1, e1)
    g = gcd(num, den)
    frac = (num // g, den // g)
    if frac != tuple(expect_delta):
        raise AssertionError(f"{name} δ={frac} want {expect_delta}")
    if expect_e is not None and e != expect_e:
        raise AssertionError(f"{name} e={e} want {expect_e}")
    width = P.width_lower() if P.n <= 16 else None
    if expect_width is not None and width != expect_width:
        raise AssertionError(f"{name} width={width} want {expect_width}")
    print(f"  {name} δ={frac[0]}/{frac[1]} e={e} width={width} pair={pair}")
    return {
        "delta": list(frac),
        "e": e,
        "width": width,
        "pair": list(pair) if pair else None,
        "n_summands": n_ordinal_summands(P),
    }


def main():
    out = {}

    print("W10 (this notebook)")
    out["W10"] = check("W10", W10(), (6, 17), 187, 3)

    print("L_14,1,9 from the Peczarski definition")
    out["L14_1_9_constructed"] = check(
        "L14,1,9 constructed", ladder_poset(14, (1, 9)), (254, 725), 725, 2
    )

    print("Gupta published encodings")
    # minimum above 1/3: 37/106, width 2, e=318 (L_10,1,5 padded)
    P = poset_from_up(decode_up("14:0000000000010007000f000f003f001f00ff009f03ff02ff0fff0aff"))
    out["gupta_37_106"] = check("Gupta 37/106", P, (37, 106), 318, 2)

    # non-sum minimum: 254/725
    P = poset_from_up(decode_up("14:0000000000030001000f0009003f002f00ff00bf03ff02ff0fff0aff"))
    out["gupta_254_725"] = check("Gupta 254/725", P, (254, 725), 725, 2)

    # width-3 6/17 row (ordinal sum; 29 classes)
    P = poset_from_up(decode_up("14:0000000000010007000f000f001f001f007f00bf017f057f05ff0fff"))
    out["gupta_6_17_width3"] = check("Gupta 6/17 width-3", P, (6, 17), None, 3)
    if out["gupta_6_17_width3"]["n_summands"] < 2:
        raise AssertionError("expected an ordinal sum on the 6/17 width-3 row")

    print("L_10,1,5 and L_9,1,2,3,4")
    out["L10_1_5"] = check("L10,1,5", ladder_poset(10, (1, 5)), (37, 106), 106, 2)
    out["L9_1_2_3_4"] = check("L9,1,2,3,4", ladder_poset(9, (1, 2, 3, 4)), (6, 17), None, 2)

    path = HERE / "gupta_verify.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path}")
    print("GUPTA WITNESSES OK")


if __name__ == "__main__":
    main()
