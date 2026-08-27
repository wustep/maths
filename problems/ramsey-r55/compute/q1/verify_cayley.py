#!/usr/bin/env python3
"""Independently rebuild a Cayley graph from a HIT line and run r55lib.is_ramsey."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

Q1 = Path(__file__).resolve().parent
sys.path.insert(0, str(Q1.parent))
sys.path.insert(0, str(Q1))
from r55lib import degrees, fingerprint, is_ramsey  # noqa: E402

from check_groups import mul_c11c4, mul_c2c22, mul_c3c15, mul_d22

MUL = {
    "c2c22": (mul_c2c22, 44),
    "d22": (mul_d22, 44),
    "c11c4": (mul_c11c4, 44),
    "c3c15": (mul_c3c15, 45),
}


def inv_table(mul, n):
    inv = [None] * n
    for a in range(n):
        for b in range(n):
            if mul(a, b) == 0 and mul(b, a) == 0:
                inv[a] = b
                break
    if any(x is None for x in inv):
        raise RuntimeError("missing inverse")
    return inv


def cayley_nbr(mul, n, S):
    inv = inv_table(mul, n)
    nbr = [0] * n
    for g in range(n):
        m = 0
        for s in S:
            h = mul(g, s)
            if h == g:
                raise RuntimeError("loop")
            m |= 1 << h
        nbr[g] = m
    # sanity: undirected
    for i in range(n):
        for j in range(n):
            e = (nbr[i] >> j) & 1
            f = (nbr[j] >> i) & 1
            if e != f:
                raise RuntimeError(f"directed {i,j}")
    return nbr


def parse_hit(line: str):
    # HIT group=c2c22 n=44 deg=20 pairs=1 4 7 inv=11 33
    if not line.startswith("HIT"):
        return None
    parts = line.split()
    rec = {"pairs": [], "inv": []}
    mode = None
    for p in parts:
        if p.startswith("group="):
            rec["group"] = p.split("=", 1)[1]
        elif p.startswith("n="):
            rec["n"] = int(p.split("=", 1)[1])
        elif p.startswith("deg="):
            rec["deg"] = int(p.split("=", 1)[1])
        elif p == "pairs=":
            mode = "pairs"
        elif p.startswith("pairs="):
            mode = "pairs"
            rest = p.split("=", 1)[1]
            if rest:
                rec["pairs"].append(int(rest))
        elif p == "inv=":
            mode = "inv"
        elif p.startswith("inv="):
            mode = "inv"
            rest = p.split("=", 1)[1]
            if rest:
                rec["inv"].append(int(rest))
        elif mode in ("pairs", "inv") and p.lstrip("-").isdigit():
            rec[mode].append(int(p))
        else:
            mode = None
    return rec


def connection_set(rec):
    mul, n = MUL[rec["group"]]
    inv = inv_table(mul, n)
    S = set(rec["inv"])
    for a in rec["pairs"]:
        S.add(a)
        S.add(inv[a])
    return S


def verify_hit(line: str) -> dict:
    rec = parse_hit(line)
    if rec is None:
        raise ValueError(line)
    mul, n = MUL[rec["group"]]
    S = connection_set(rec)
    nbr = cayley_nbr(mul, n, S)
    degs = degrees(nbr)
    ok = is_ramsey(nbr)
    return {
        "line": line.strip(),
        "ok_55": ok,
        "deg_set": sorted(set(degs)),
        "fingerprint": fingerprint(nbr),
        "nS": len(S),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", nargs="?", help="census log containing HIT lines")
    args = ap.parse_args()
    if not args.log:
        print("no HIT log; encoder sanity only")
        return 0
    n_ok = n_bad = 0
    for line in Path(args.log).read_text().splitlines():
        if not line.startswith("HIT"):
            continue
        rec = verify_hit(line)
        print(rec)
        if rec["ok_55"]:
            n_ok += 1
        else:
            n_bad += 1
    print(f"hits_ok={n_ok} hits_not55={n_bad}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
