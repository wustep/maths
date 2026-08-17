#!/usr/bin/env python3
"""Exact exceptions to F(n) <= n^{p/q} via integer comparison F^q > n^p."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from covering_search import lpf_sieve

ROOT = Path(__file__).resolve().parent


def F_sieve(P, n: int) -> tuple[int, int]:
    best = n
    best_a = 1
    half = n // 2
    for a in range(1, half + 1):
        v = P[a] if P[a] > P[n - a] else P[n - a]
        if v < best:
            best = v
            best_a = a
            if best <= 2:
                break
    return best, best_a


def exceptions(P, X: int, p: int, q: int) -> list[dict]:
    rows = []
    for n in range(2, X + 1):
        F, a = F_sieve(P, n)
        if F**q > n**p:
            rows.append({"n": n, "F": F, "a": a, "b": n - a})
    return rows


def main() -> int:
    X = 200_000
    P = lpf_sieve(X)
    out = {}
    for p, q, name in ((1, 2, "1/2"), (2, 5, "2/5"), (1, 3, "1/3")):
        rows = exceptions(P, X, p, q)
        out[name] = {
            "test": f"F^{q} > n^{p}",
            "X": X,
            "n_exceptions": len(rows),
            "exceptions": rows,
            "last": rows[-1]["n"] if rows else None,
        }
        print(name, "count", len(rows), "last", out[name]["last"], "ns", [r["n"] for r in rows[:40]], "...")

    # Push 2/5 a bit further with the already-built C float list as a candidate
    # filter: recheck those 16 plus a sweep is already in `rows` for X=2e5.
    cert = ROOT / "certs" / "f_exceptions_exact.json"
    payload = {
        "X": X,
        "results": out,
        "is_dent": False,
        "reason": (
            "Exact finite exception lists for F(n)<=n^{2/5} and F(n)<=n^{1/3} "
            "on [2,X]. Not an infinite covering and does not beat Balog 1989."
        ),
    }
    cert.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", cert)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
