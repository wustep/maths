"""Exact integer check of an ST26-style witness on a (1,...,k) lift.

Given p, v in (Z/mZ)^k, s, j, reconstruct the unique lift
    u_i = a_i p + i    with    a_i in {0,...,m-1},  u_i ≡ v_i (mod m)
and check
    t = s/m + j/p
satisfies ||t u_i|| >= 1/m for every i, using only integer arithmetic.
"""

from __future__ import annotations

import argparse
import math


def inv_mod(a: int, m: int) -> int:
    return pow(a % m, -1, m)


def reconstruct_u(v: list[int], p: int) -> list[int]:
    k = len(v)
    m = k + 1
    # a_i p + i ≡ v_i (mod m)  =>  a_i ≡ (v_i - i) * p^{-1} (mod m)
    ip = inv_mod(p, m)
    u = []
    for i, vi in enumerate(v, start=1):
        a = ((vi - i) * ip) % m
        u.append(a * p + i)
    return u


def tor_norm(num: int, den: int) -> int:
    """||num/den|| * den  (an integer in 0..den/2)."""
    r = num % den
    return min(r, den - r)


def check(v: list[int], p: int, s: int, j: int) -> dict:
    k = len(v)
    m = k + 1
    u = reconstruct_u(v, p)
    # t = s/m + j/p = (s p + j m)/(m p)
    den = m * p
    num_t = s * p + j * m
    dists = []
    ok = True
    for ui in u:
        d = tor_norm(num_t * ui, den)
        # ||t u|| >= 1/m  iff  d/den >= 1/m  iff  d * m >= den  iff d >= p
        if d < p:
            ok = False
        dists.append((d, den))
    return {"ok": ok, "u": u, "t_num": num_t, "t_den": den, "min_d": min(x[0] for x in dists), "need_d": p}


def find_sj(v: list[int], p: int) -> tuple[int, int] | None:
    k = len(v)
    m = k + 1
    Bs = [[(m * ((i * j) % p)) // p for i in range(1, k + 1)] for j in range(p)]
    for s in range(m):
        for j, B in enumerate(Bs):
            if all(((s * v[i] + B[i]) % m) not in (0, m - 1) for i in range(k)):
                return s, j
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", required=True, help="comma vector")
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--s", type=int, default=-1)
    ap.add_argument("--j", type=int, default=-1)
    args = ap.parse_args()
    v = [int(x) for x in args.v.split(",")]
    s, j = args.s, args.j
    if s < 0 or j < 0:
        w = find_sj(v, args.p)
        if w is None:
            print("NO_WITNESS")
            raise SystemExit(1)
        s, j = w
    r = check(v, args.p, s, j)
    print(f"v={v}")
    print(f"p={args.p} s={s} j={j}")
    print(f"u={r['u']}")
    print(f"t={r['t_num']}/{r['t_den']}")
    print(f"min_d={r['min_d']} need_d>={r['need_d']} ok={r['ok']}")
    raise SystemExit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
