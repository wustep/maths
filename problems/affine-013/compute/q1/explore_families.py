"""Infinite-family candidates and fibre-richness census.

A family is interesting only if limsup T/n^2 > 1/3, or if it suggests
a uniform fibre bound below 1/2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count import interval_t, t_count  # noqa: E402


def t_ratio(s: list[int]) -> tuple[int, int, float]:
    n = len(s)
    t = t_count(s)
    return t, interval_t(n), t / (n * n) if n else 0.0


def almost_interval(n: int) -> list[int]:
    return list(range(n - 1)) + [n]


def e_km(k: int, m: int) -> list[int]:
    # Green–Sisask E(k,m)
    left = list(range(-k - 2 * m, -k + 1, 2))  # -k-2m .. -k step 2
    mid = list(range(-k, k + 1))
    right = list(range(k + 2, k + 2 * m + 1, 2))
    return sorted(set(left + mid + right))


def f_km(k: int, m: int) -> list[int]:
    left = list(range(-k - 2 * m + 2, -k + 1, 2))
    mid = list(range(-k, k + 1))
    right = list(range(k + 2, k + 2 * m + 1, 2))
    return sorted(set(left + mid + right))


def two_intervals_ratio(a: int, b: int, gap: int) -> list[int]:
    return list(range(a)) + list(range(a + gap, a + gap + b))


def int_plus_3tail(m: int) -> list[int]:
    return sorted(set(range(m + 1)) | {3 * k for k in range(1, m + 1)})


def double_gp(L: int) -> list[int]:
    """Centre 0, left -2^k, right +2^k."""
    s = {0}
    for k in range(L):
        s.add(-(1 << k))
        s.add(1 << (k + 1))
    return sorted(s)


def beatty(n: int, alpha: float) -> list[int]:
    return [int(i * alpha) for i in range(n)]


def fibre_stats(pts: list[int]) -> dict:
    a = sorted(pts)
    n = len(a)
    present = set(a)
    rich_15 = 0
    rich_12 = 0
    max_ratio = 0.0
    t = 0
    for j, z in enumerate(a):
        left = a[:j]
        right = a[j + 1 :]
        L, R = len(left), len(right)
        lam = mu = 0
        for y in a:
            x = 3 * z - 2 * y
            if x in present:
                t += 1
                if y < z:
                    lam += 1
                elif y > z:
                    mu += 1
        m = min(L, R)
        ratio = (lam + mu) / m if m else 0.0
        if ratio > max_ratio:
            max_ratio = ratio
        if m >= max(1, n // 6) and ratio >= 1.5 - 1e-12:
            rich_15 += 1
        if m >= max(1, n // 6) and ratio >= 1.2 - 1e-12:
            rich_12 += 1
    return {
        "n": n,
        "T": t,
        "rich_15": rich_15,
        "rich_12": rich_12,
        "max_fibre_ratio": max_ratio,
    }


def main() -> None:
    rows = []

    print("=== almost-interval n=3m ===")
    for m in range(1, 21):
        n = 3 * m
        s = almost_interval(n)
        t, ti, r = t_ratio(s)
        rows.append({"fam": "almost", "n": n, "T": t, "I": ti, "ratio": r})
        if m in (1, 2, 5, 10, 20):
            print(f"  n={n} T={t} I={ti} T-I={t-ti} ratio={r:.6f}")

    print("=== Green-Sisask E(k,m) / F(k,m) ===")
    for k in range(0, 8):
        for m in range(0, 8):
            for name, fn in (("E", e_km), ("F", f_km)):
                s = fn(k, m)
                if len(s) < 3:
                    continue
                t, ti, r = t_ratio(s)
                rows.append(
                    {
                        "fam": f"{name}_{k}_{m}",
                        "n": len(s),
                        "T": t,
                        "I": ti,
                        "ratio": r,
                    }
                )
                if r > ti / (len(s) ** 2) + 1e-12 and r > 0.34:
                    print(
                        f"  {name}({k},{m}) n={len(s)} T={t} I={ti} ratio={r:.6f}"
                    )

    print("=== two intervals, selected ratios ===")
    best_two = {"ratio": 0.0}
    for a in range(4, 25):
        for b in range(4, 25):
            for gap in (1, 2, 3, a, b, 2 * a, 3 * a):
                s = two_intervals_ratio(a, b, gap)
                t, ti, r = t_ratio(s)
                rec = {
                    "fam": f"two_{a}_{b}_{gap}",
                    "n": len(s),
                    "T": t,
                    "I": ti,
                    "ratio": r,
                }
                rows.append(rec)
                if r > best_two["ratio"]:
                    best_two = rec
    print("  best two-int", best_two)

    print("=== interval + 3-tail ===")
    for m in range(2, 25):
        s = int_plus_3tail(m)
        t, ti, r = t_ratio(s)
        rows.append({"fam": f"3tail_{m}", "n": len(s), "T": t, "I": ti, "ratio": r})
        if m in (2, 6, 12, 24):
            print(f"  m={m} n={len(s)} T={t} I={ti} ratio={r:.6f}")

    print("=== double GP ===")
    for L in range(2, 12):
        s = double_gp(L)
        t, ti, r = t_ratio(s)
        fs = fibre_stats(s)
        print(
            f"  L={L} n={len(s)} T={t} I={ti} ratio={r:.6f} "
            f"rich15={fs['rich_15']} maxfr={fs['max_fibre_ratio']:.3f}"
        )
        rows.append({"fam": f"gp_{L}", "n": len(s), "T": t, "I": ti, "ratio": r})

    print("=== Beatty ===")
    for alpha in (1.5, (1 + 5**0.5) / 2, 2.5, 4 / 3, 5 / 3):
        s = beatty(40, alpha)
        t, ti, r = t_ratio(s)
        print(f"  alpha={alpha:.4f} n=40 T={t} I={ti} ratio={r:.6f}")
        rows.append({"fam": f"beatty_{alpha}", "n": 40, "T": t, "I": ti, "ratio": r})

    print("=== fibre stats on named ===")
    named = {
        "interval_30": list(range(30)),
        "almost_30": almost_interval(30),
        "n7": [0, 3, 6, 8, 9, 12, 18],
        "E22": e_km(4, 4),
    }
    fibre_rows = []
    for name, s in named.items():
        fs = fibre_stats(s)
        fs["name"] = name
        fibre_rows.append(fs)
        print(f"  {name} {fs}")

    above = [r for r in rows if r["n"] >= 12 and r["ratio"] > 1 / 3 + 0.01]
    above.sort(key=lambda r: -r["ratio"])
    print("families with n>=12 and ratio > 0.3433:", len(above))
    for r in above[:12]:
        print(" ", r)

    Path(__file__).resolve().parent.joinpath("certs/families.json").write_text(
        json.dumps(
            {
                "n_rows": len(rows),
                "best_two": best_two,
                "above_third": above[:30],
                "fibre": fibre_rows,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
