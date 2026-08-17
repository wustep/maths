"""Two arithmetic progressions of difference 3 (two residue classes).

S = 3A ∪ (r + 3B) with r ∈ {1,2} and A, B intervals.
This is the natural infinite family that is unbalanced mod 3.

We also allow A, B to be arbitrary small sets (exact) and
interval-pairs with a shift, at large n.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import interval_t, t_count  # noqa: E402


def two_ap(a: int, b: int, shift: int, r: int = 1) -> list[int]:
    """A = [0,a), B = [shift, shift+b), S = 3A ∪ (r+3B)."""
    s = [3 * i for i in range(a)]
    s += [r + 3 * (shift + j) for j in range(b)]
    return s


def scan_two_ap(nmax: int) -> list[dict]:
    rows = []
    for n in range(3, nmax + 1):
        best = {"T": interval_t(n), "desc": "interval", "n": n}
        for a in range(1, n):
            b = n - a
            # shift of B relative to A
            for sh in range(-2 * n, 2 * n + 1):
                for r in (1, 2):
                    s = two_ap(a, b, sh, r)
                    t = t_count(s)
                    if t > best["T"]:
                        best = {
                            "T": t,
                            "n": n,
                            "a": a,
                            "b": b,
                            "shift": sh,
                            "r": r,
                            "T_interval": interval_t(n),
                            "ratio": t / (n * n),
                            "S": s,
                            "desc": f"a={a} b={b} sh={sh} r={r}",
                        }
        rows.append(best)
        print(
            f"n={n:2d} T={best['T']:4d} I={interval_t(n):4d} "
            f"{best['desc']} ratio={best['T']/(n*n):.5f}",
            flush=True,
        )
    return rows


def large_grid(N: int) -> dict:
    """Optimize length ratios and shift at a single large n = N."""
    best = {"T": interval_t(N), "desc": "interval"}
    # a from 1 to N-1 step max(1, N//40)
    step = max(1, N // 50)
    sh_step = max(1, N // 40)
    for a in range(step, N, step):
        b = N - a
        for sh in range(-N, N + 1, sh_step):
            for r in (1, 2):
                s = two_ap(a, b, sh, r)
                t = t_count(s)
                if t > best["T"]:
                    best = {
                        "T": t,
                        "n": N,
                        "a": a,
                        "b": b,
                        "shift": sh,
                        "r": r,
                        "T_interval": interval_t(N),
                        "ratio": t / (N * N),
                        "desc": f"a={a} b={b} sh={sh} r={r}",
                    }
    return best


def three_ap(a: int, b: int, c: int, sb: int, sc: int) -> list[int]:
    s = [3 * i for i in range(a)]
    s += [1 + 3 * (sb + j) for j in range(b)]
    s += [2 + 3 * (sc + k) for k in range(c)]
    return s


def scan_three_ap(nmax: int) -> list[dict]:
    rows = []
    for n in range(3, nmax + 1):
        best = {"T": interval_t(n), "desc": "interval", "n": n}
        for a in range(0, n + 1):
            for b in range(0, n - a + 1):
                c = n - a - b
                if c < 0:
                    continue
                # skip the balanced-interval-like default later; search shifts
                for sb in range(-n, n + 1, max(1, n // 6)):
                    for sc in range(-n, n + 1, max(1, n // 6)):
                        s = three_ap(a, b, c, sb, sc)
                        t = t_count(s)
                        if t > best["T"]:
                            best = {
                                "T": t,
                                "n": n,
                                "a": a,
                                "b": b,
                                "c": c,
                                "sb": sb,
                                "sc": sc,
                                "T_interval": interval_t(n),
                                "ratio": t / (n * n),
                                "desc": f"a,b,c={a},{b},{c} sb={sb} sc={sc}",
                            }
        rows.append(best)
        print(
            f"3AP n={n:2d} T={best['T']:4d} I={interval_t(n):4d} "
            f"{best['desc']} ratio={best['T']/(n*n):.5f}",
            flush=True,
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=16)
    ap.add_argument("--large", type=int, default=60)
    ap.add_argument("--three-max", type=int, default=12)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    print("=== two AP difference 3 ===", flush=True)
    two = scan_two_ap(args.nmax)
    print("=== large two-AP grid ===", flush=True)
    large = large_grid(args.large)
    print("large", large, flush=True)
    print("=== three AP ===", flush=True)
    three = scan_three_ap(args.three_max)

    if args.out:
        Path(args.out).write_text(
            json.dumps({"two": two, "large": large, "three": three}, indent=2)
            + "\n"
        )


if __name__ == "__main__":
    main()
