#!/usr/bin/env python3
"""Residue factor-sieve for n^2+1: primes, Iwaniec P2s, Bateman–Horn check.

Odd n>1 make n^2+1 even and composite. Only n=1 and even n are live.
For every even n <= n_max we divide out all primes q ≡ 1 (mod 4) with q <= n_max
that divide n^2+1. The leftover then has all prime factors > n_max, so it is
1, a prime, or a product of two primes (n^2+1 is never a square for n>=1).
That classifies Ω completely. Leftover composites are split by Pollard rho
only to write an explicit factorization.

This does not prove infinitude.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from array import array
from pathlib import Path

from n2p1_lib import (
    C_Q,
    WOLF_PI_Q,
    bateman_horn_integral,
    even_index,
    factor_int,
    landau_shanks_product,
    miller_rabin,
    n_from_index,
    pollard_rho,
    primes_upto,
    sqrt_minus_one,
    wolf_prediction_li,
)

HERE = Path(__file__).resolve().parent


def sha256_text(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def factor_sieve(n_max: int) -> tuple[array, array, array, list[int]]:
    """Return (remaining, Omega_small, omega_small, primes_used).

    remaining[i] is (n^2+1) after dividing out every prime q<=n_max,
    n = 2*(i+1). Omega_small / omega_small are Ω and ω of that smooth part.
    """
    size = n_max // 2
    remaining = array("Q", (0,)) * size
    big_omega = array("B", (0,)) * size
    little_omega = array("B", (0,)) * size
    for i in range(size):
        n = n_from_index(i)
        remaining[i] = n * n + 1

    primes = primes_upto(n_max)
    for q in primes:
        if q == 2 or q % 4 != 1:
            continue
        r = sqrt_minus_one(q)
        if (r * r + 1) % q != 0:
            raise RuntimeError(f"bad sqrt(-1) mod {q}: {r}")
        for residue in (r, q - r):
            start = residue
            if start & 1:
                start += q
            if start == 0:
                start = 2 * q
            if start < 2:
                start += 2 * q
            step = 2 * q
            for n in range(start, n_max + 1, step):
                i = even_index(n)
                m = remaining[i]
                if m % q:
                    continue
                e = 0
                while m % q == 0:
                    m //= q
                    e += 1
                remaining[i] = m
                big_omega[i] = big_omega[i] + e
                little_omega[i] = little_omega[i] + 1
    return remaining, big_omega, little_omega, primes


def classify(
    n_max: int,
    remaining: array,
    big_omega_small: array,
    little_omega_small: array,
    primes: list[int],
) -> dict:
    prime_n = [1] if n_max >= 1 and miller_rabin(2) else []
    p2: list[tuple[int, list[int]]] = []
    omega_hist: dict[int, int] = {}
    omega_hist[1] = len(prime_n)
    w_le2_composite = 0
    unsplit = 0

    size = n_max // 2
    for i in range(size):
        n = n_from_index(i)
        rem = int(remaining[i])
        om = int(big_omega_small[i])
        w = int(little_omega_small[i])
        leftover: list[int] = []
        if rem > 1:
            if miller_rabin(rem):
                leftover = [rem]
                om += 1
                w += 1
            else:
                d = pollard_rho(rem)
                q, rco = d, rem // d
                if q > rco:
                    q, rco = rco, q
                if not (miller_rabin(q) and miller_rabin(rco) and q * rco == rem):
                    leftover = factor_int(rem, primes)
                    unsplit += 1
                else:
                    leftover = [q, rco] if q <= rco else [rco, q]
                om += len(leftover)
                w += len(set(leftover))
        omega_hist[om] = omega_hist.get(om, 0) + 1
        if om == 1:
            prime_n.append(n)
            continue
        if w <= 2:
            w_le2_composite += 1
        if om != 2:
            continue
        m = n * n + 1
        if rem > 1 and leftover and math.prod(leftover) == rem:
            other = m // rem
            if other == 1:
                fs = leftover
            else:
                fs = sorted(leftover + [other])
        else:
            fs = factor_int(m, primes)
        if math.prod(fs) != m or len(fs) != 2:
            unsplit += 1
        p2.append((n, fs))

    return {
        "prime_n": prime_n,
        "p2": p2,
        "omega_hist": {str(k): v for k, v in sorted(omega_hist.items()) if v},
        "w_le2_composite": w_le2_composite,
        "unsplit": unsplit,
    }


def pi_q_from_primes(prime_n: list[int], x: int) -> int:
    """Number of n with n^2+1 < x."""
    # n < sqrt(x-1) approximately; scan is fine at our sizes.
    lim = math.isqrt(x - 1)
    # if lim^2 + 1 >= x, drop. isqrt(x-1)^2 + 1 <= x always, equality only
    # when x-1 is square and we want strict <.
    # n^2+1 < x ⇔ n^2 < x-1 ⇔ n <= isqrt(x-2) for x>=2.
    if x <= 2:
        return 0
    n_cut = math.isqrt(x - 2)
    return sum(1 for n in prime_n if n <= n_cut)


def checkpoints(prime_n: list[int], n_max: int) -> list[dict]:
    rows = []
    for k, published in sorted(WOLF_PI_Q.items()):
        x = 10**k
        if x - 1 > n_max * n_max + 1:
            continue
        got = pi_q_from_primes(prime_n, x)
        rows.append(
            {
                "x": x,
                "pi_q": got,
                "wolf": published,
                "match": got == published,
            }
        )
    return rows


def write_lists(prime_n: list[int], p2: list[tuple[int, list[int]]], here: Path) -> dict:
    p_path = here / "prime_n.txt"
    p2_path = here / "p2_omega2.txt"
    with p_path.open("w") as f:
        f.write("# n such that n^2+1 is prime, n <= n_max, including n=1\n")
        for n in prime_n:
            f.write(f"{n}\n")
    with p2_path.open("w") as f:
        f.write("# Iwaniec P2 composites: n  p  q   with n^2+1 = p*q, Ω=2, p<=q\n")
        for n, fs in p2:
            f.write(f"{n} " + " ".join(str(p) for p in fs) + "\n")
    return {
        "prime_n_txt": str(p_path.name),
        "p2_txt": str(p2_path.name),
        "prime_n_sha256": sha256_text(p_path),
        "p2_sha256": sha256_text(p2_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-max", type=int, default=1_000_000)
    parser.add_argument("--out", type=Path, default=HERE / "n2p1.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return

    n_max = args.n_max
    t0 = time.perf_counter()
    remaining, big_omega_small, little_omega_small, primes = factor_sieve(n_max)
    t1 = time.perf_counter()
    cls = classify(n_max, remaining, big_omega_small, little_omega_small, primes)
    t2 = time.perf_counter()

    prime_n: list[int] = cls["prime_n"]
    p2: list[tuple[int, list[int]]] = cls["p2"]
    hashes = write_lists(prime_n, p2, HERE)

    bh_int = bateman_horn_integral(n_max)
    bh = C_Q * bh_int
    wolf_li = wolf_prediction_li(n_max)
    cprod = landau_shanks_product(primes_upto(min(n_max, 2_000_000)))

    wolf_rows = checkpoints(prime_n, n_max)
    iwaniec_p2 = len(prime_n) + len(p2)

    payload = {
        "n_max": n_max,
        "count_prime": len(prime_n),
        "count_p2_omega_eq_2_composite": len(p2),
        "count_iwaniec_p2": iwaniec_p2,
        "count_omega_le2_composite_diagnostic": cls["w_le2_composite"],
        "unsplit": cls["unsplit"],
        "omega_hist": cls["omega_hist"],
        "first_prime_n": prime_n[:30],
        "first_prime_values": [n * n + 1 for n in prime_n[:30]],
        "last_prime_n": prime_n[-8:],
        "last_prime_values": [n * n + 1 for n in prime_n[-8:]],
        "first_p2_n": [n for n, _ in p2[:12]],
        "C_q_published": C_Q,
        "C_q_truncated_product": cprod,
        "bateman_horn_integral": bh_int,
        "bateman_horn_prediction": bh,
        "wolf_li_prediction": wolf_li,
        "prime_over_bh": (len(prime_n) / bh) if bh else None,
        "prime_over_wolf_li": (len(prime_n) / wolf_li) if wolf_li else None,
        "iwaniec_shape_N_over_logN_3_2": n_max / (math.log(n_max) ** 1.5),
        "wolf_A083844": wolf_rows,
        "seconds_sieve": t1 - t0,
        "seconds_classify": t2 - t1,
        "note": (
            "prime_n: n=1 and even n with n^2+1 prime by 64-bit MR. "
            "Iwaniec P2 means Ω(n^2+1)<=2 (multiplicity). "
            "n^2+1 is never a square for n>=1, so Ω=2 means a product of two primes. "
            "P2 list is complete on 1<=n<=n_max. Not a proof of infinitude. "
            "Did not beat Wolf/Grantham published complete lists."
        ),
        **hashes,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"n_max={n_max} primes={len(prime_n)} p2_Omega2={len(p2)} "
        f"iwaniec_P2={iwaniec_p2} ω<=2_comp={cls['w_le2_composite']} "
        f"unsplit={cls['unsplit']}"
    )
    print(f"BH={bh:.3f} count/BH={payload['prime_over_bh']:.6f} wolf_li={wolf_li:.3f}")
    print("wolf rows", wolf_rows)
    print("first primes", payload["first_prime_values"][:12])
    print(f"wrote {args.out} in {t2 - t0:.2f}s (sieve {t1 - t0:.2f}s)")


def _self_test() -> None:
    assert sqrt_minus_one(5) ** 2 % 5 == 4
    assert sqrt_minus_one(13) ** 2 % 13 == 12
    assert sqrt_minus_one(17) ** 2 % 17 == 16
    assert sqrt_minus_one(29) ** 2 % 29 == 28
    assert miller_rabin(2) and miller_rabin(5) and not miller_rabin(65)
    assert factor_int(325) == [5, 5, 13]
    assert factor_int(65) == [5, 13]
    assert factor_int(2) == [2]
    # 18^2+1 is not Iwaniec P2.
    assert len(factor_int(18 * 18 + 1)) == 3
    print("self-test OK")


if __name__ == "__main__":
    main()
