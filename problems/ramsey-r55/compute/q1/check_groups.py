#!/usr/bin/env python3
"""Identity, inverses, and full associativity for the q1 Cayley groups."""

from __future__ import annotations

import json
from pathlib import Path


def check(name, mul, n):
    inv = {}
    for a in range(n):
        if mul(a, 0) != a or mul(0, a) != a:
            return {"name": name, "ok": False, "reason": f"id fail {a}"}
        found = None
        for b in range(n):
            if mul(a, b) == 0 and mul(b, a) == 0:
                found = b
                break
        if found is None:
            return {"name": name, "ok": False, "reason": f"no inv {a}"}
        inv[a] = found
    for a in range(n):
        for b in range(n):
            for c in range(n):
                if mul(mul(a, b), c) != mul(a, mul(b, c)):
                    return {"name": name, "ok": False, "reason": f"assoc {a,b,c}"}
    ninv = sum(1 for a in range(1, n) if inv[a] == a)
    return {"name": name, "ok": True, "n": n, "ninv": ninv}


def mul_c2c22(a, b):
    return 22 * (((a // 22) + (b // 22)) & 1) + ((a % 22 + b % 22) % 22)


def mul_d22(a, b):
    ak, as_, bk, bs = a % 22, a // 22, b % 22, b // 22
    if as_ == 0:
        return ((ak + bk) % 22) + 22 * bs
    return ((ak - bk + 22) % 22) + 22 * (1 - bs)


def mul_c11c4(x, y):
    a1, b1 = x % 11, x // 11
    a2, b2 = y % 11, y // 11
    a = (a1 + a2) % 11 if (b1 % 2 == 0) else (a1 - a2 + 11) % 11
    return 11 * ((b1 + b2) % 4) + a


def mul_c3c15(a, b):
    return 15 * (((a // 15) + (b // 15)) % 3) + ((a % 15 + b % 15) % 15)


def mul_c3c3c5(a, b):
    # pack 15*x + 5*y + z, x,y in Z/3, z in Z/5 — isomorphic to C3 x C15
    x1, r1 = divmod(a, 15)
    y1, z1 = divmod(r1, 5)
    x2, r2 = divmod(b, 15)
    y2, z2 = divmod(r2, 5)
    x = (x1 + x2) % 3
    y = (y1 + y2) % 3
    z = (z1 + z2) % 5
    return 15 * x + 5 * y + z


def main() -> int:
    rows = [
        check("C2xC22", mul_c2c22, 44),
        check("D22", mul_d22, 44),
        check("C11rtimesC4", mul_c11c4, 44),
        check("C3xC15", mul_c3c15, 45),
        check("C3xC3xC5", mul_c3c3c5, 45),
    ]
    out = Path(__file__).resolve().parent / "certs" / "group_laws.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"rows": rows, "all_ok": all(r["ok"] for r in rows)}
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for r in rows:
        print(r)
    print("wrote", out)
    return 0 if payload["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
