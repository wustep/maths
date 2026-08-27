#!/usr/bin/env python3
"""More families that might sit near Shakan’s 2 on the diagonal n ≈ √p.

None of these is a dent by itself. An infinite family with
max_d g ≤ (2+ε)√p would show that 2 cannot be replaced by 2+ε.
"""

from __future__ import annotations

import json
import random

import pathutil
from constructions import (
    equally_spaced,
    geometric,
    jittered_grid,
    nearest_subgroup,
    random_set,
    small_squares,
)
from gaplib import max_gap_dilates, primes_upto, primitive_root, shakan_lower, uniq_mod


def quadratic_ruler(p: int, n: int, c: int = 1) -> list[int]:
    """{ i + c i(i-1)/2 mod p : i = 0..n-1 }."""
    A = []
    seen = set()
    inv2 = pow(2, p - 2, p)
    for i in range(n + p):
        x = (i + c * i * (i - 1) * inv2) % p
        if x not in seen:
            seen.add(x)
            A.append(x)
        if len(A) == n:
            break
    return uniq_mod(A, p)[:n]


def paley_prefix(p: int, n: int) -> list[int]:
    """Least n quadratic residues, including 0."""
    A = [0]
    seen = {0}
    for x in range(1, p):
        y = (x * x) % p
        if y not in seen:
            seen.add(y)
            A.append(y)
        if len(A) == n:
            break
    return uniq_mod(A, p)[:n]


def cyclotomic_coset(p: int, n: int, which: int = 0) -> list[int] | None:
    """A multiplicative coset of the unique subgroup of order n, if n | p-1."""
    if n <= 0 or (p - 1) % n != 0:
        return None
    g = primitive_root(p)
    step = (p - 1) // n
    h = pow(g, step, p)
    start = pow(g, which, p)
    A = []
    x = start
    for _ in range(n):
        A.append(x)
        x = (x * h) % p
    return uniq_mod(A, p)


def two_scale(p: int, n: int) -> list[int]:
    """Half an interval of spacing 1, half of spacing ~ p/n."""
    k = n // 2
    A = list(range(k))
    step = max(2, p // max(1, n - k))
    x = k
    while len(A) < n:
        A.append(x % p)
        x += step
    return uniq_mod(A, p)[:n]


def singer_orbit_mod_73() -> list[int]:
    """The <2>-orbit {2^k} in F_73, a (73,9,1) difference set."""
    return sorted({pow(2, k, 73) for k in range(9)})


def multiplier_orbits(p: int, mult: int) -> list[list[int]]:
    seen = set()
    orbits = []
    for x in range(1, p):
        if x in seen:
            continue
        orb = []
        y = x
        while y not in seen:
            seen.add(y)
            orb.append(y)
            y = (mult * y) % p
        orbits.append(sorted(orb))
    return orbits


def is_difference_set(A: list[int], p: int, lam: int = 1) -> bool:
    cnt = [0] * p
    for a in A:
        for b in A:
            if a == b:
                continue
            cnt[(a - b) % p] += 1
    return all(c == lam for c in cnt[1:])


def singer_prime_power_candidates(p: int, n: int) -> list[list[int]]:
    """If p = q^2+q+1 and n = q+1, return multiplier-orbit difference sets."""
    # q^2 + q + 1 - p = 0 ⇒ q ≈ (-1+√(4p-3))/2
    disc = 4 * p - 3
    q = int(disc**0.5)
    if q * q != disc:
        # try nearby integer q
        q = round((-1 + (4 * p - 3) ** 0.5) / 2)
    if q * q + q + 1 != p or n != q + 1:
        return []
    # 2 is the classical Singer multiplier when it has order q+1 or divides
    out = []
    for mult in (2, 3, primitive_root(p)):
        for orb in multiplier_orbits(p, mult):
            if len(orb) == n and is_difference_set(orb, p):
                out.append(orb)
        if out:
            break
    return out


def anneal(p: int, n: int, seed: int = 0, steps: int = 8000) -> tuple[list[int], int]:
    rng = random.Random(seed)
    starts = [
        equally_spaced(p, n),
        small_squares(p, n),
        nearest_subgroup(p, n)[0],
        quadratic_ruler(p, n, c=1),
        paley_prefix(p, n),
        jittered_grid(p, n, rng),
        two_scale(p, n),
        random_set(p, n, rng),
    ]
    H = cyclotomic_coset(p, n)
    if H is not None:
        starts.append(H)
    for S in singer_prime_power_candidates(p, n):
        starts.append(S)

    best_A = None
    best_g = p
    for A0 in starts:
        A = uniq_mod(A0, p)[:n]
        if len(A) < n:
            extra = [x for x in range(p) if x not in A]
            A = A + extra[: n - len(A)]
        Aset = set(A)
        cur_g, _ = max_gap_dilates(A, p)
        idle = 0
        temp = max(1, cur_g // 4)
        for st in range(steps):
            out_el = rng.choice(A)
            ins_el = rng.randrange(p)
            if ins_el in Aset:
                idle += 1
                continue
            Aset.remove(out_el)
            Aset.add(ins_el)
            trial = list(Aset)
            tg, _ = max_gap_dilates(trial, p)
            accept = tg <= cur_g or (temp > 0 and rng.random() < 0.15 * temp / (tg - cur_g + 1))
            if accept:
                A = trial
                cur_g = tg
                idle = 0
            else:
                Aset.remove(ins_el)
                Aset.add(out_el)
                idle += 1
            if idle > 100:
                temp = max(1, temp - 1)
                idle = 0
        if cur_g < best_g:
            best_g = cur_g
            best_A = sorted(A)
    return best_A, best_g


def eval_family(tag: str, A: list[int] | None, p: int) -> dict | None:
    if A is None:
        return None
    A = uniq_mod(A, p)
    g, d = max_gap_dilates(A, p)
    n = len(A)
    sh = shakan_lower(p, n)
    return {
        "tag": tag,
        "p": p,
        "n": n,
        "g": g,
        "d": d,
        "shakan": sh,
        "ratio_mean": g * n / p if n else None,
        "ratio_sqrt": g / (p**0.5),
        "A": A,
    }


def main():
    rows = []
    rng = random.Random(1)
    for p in primes_upto(200):
        if p < 11:
            continue
        n = max(2, int(round(p**0.5)))
        families = [
            ("equal", equally_spaced(p, n)),
            ("squares", small_squares(p, n)),
            ("geom", geometric(p, n)),
            ("sub", nearest_subgroup(p, n)[0]),
            ("qr", paley_prefix(p, n)),
            ("quad1", quadratic_ruler(p, n, 1)),
            ("quad3", quadratic_ruler(p, n, 3)),
            ("twoscale", two_scale(p, n)),
            ("jitter", jittered_grid(p, n, rng)),
        ]
        H = cyclotomic_coset(p, n)
        if H is not None:
            families.append(("cyclo", H))
        for i, S in enumerate(singer_prime_power_candidates(p, n)):
            families.append((f"singer_orb{i}", S))
        if p == 73:
            families.append(("singer73", singer_orbit_mod_73()))
        for tag, A in families:
            rec = eval_family(tag, A, p)
            if rec:
                rows.append(rec)
        A, g = anneal(p, n, seed=p, steps=4000 if p <= 120 else 1500)
        rec = eval_family("anneal", A, p)
        if rec:
            rec["anneal_g"] = g
            rows.append(rec)
        print(
            f"p={p:3d} n={n:2d} anneal={g:3d} sh={shakan_lower(p,n):6.2f} "
            f"ratio={g*n/p:.3f}",
            flush=True,
        )
    dest = pathutil.CERTS / "constructions_q1.jsonl"
    with dest.open("w") as f:
        for rec in rows:
            f.write(json.dumps(rec) + "\n")
    # summary: best ratio per p
    best = {}
    for rec in rows:
        p = rec["p"]
        if p not in best or rec["ratio_mean"] < best[p]["ratio_mean"]:
            best[p] = rec
    dest2 = pathutil.CERTS / "constructions_best.json"
    dest2.write_text(json.dumps(best, indent=2))
    print("wrote", dest, dest2)
    near = [best[p] for p in sorted(best) if best[p]["ratio_mean"] <= 2.4]
    print("ratios <= 2.4:", [(r["p"], r["tag"], round(r["ratio_mean"], 3)) for r in near])


if __name__ == "__main__":
    main()
