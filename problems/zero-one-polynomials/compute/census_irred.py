#!/usr/bin/env python3
"""
Exact census of monic 0/1-polynomials of degree n with constant term 1.

P_n has 2^{n-1} elements. For each we record:
  - irreducible over Z
  - divisible by x+1
  - min irreducible factor degree
  - whether the non-reciprocal part is 1, irreducible, or reducible
    (Filaseta–Kalogirou remainder)

Borst et al. published exact reducibility through degree 20. We recompute
that range with a richer factor-type table and write a machine-readable
certificate (each n: counts + a SHA256 of the list of reducible bitmasks
for independent checking).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

from sympy import Poly, ZZ, cyclotomic_poly, symbols, gcd as sgcd

x = symbols("x")


def is_reciprocal_poly(p: Poly) -> bool:
    c = p.all_coeffs()  # highest first
    # ignore trailing zeros (shouldn't exist)
    return c == list(reversed(c)) or c == [-a for a in reversed(c)]


def analyze(mask: int, n: int) -> dict:
    coeffs = [(mask >> i) & 1 for i in range(n + 1)]  # const first
    p = Poly.from_list(list(reversed(coeffs)), x, domain=ZZ)
    content, facs = p.factor_list()
    degrees = []
    rec_deg = 0
    nonrec = []
    for f, e in facs:
        d = int(f.degree())
        degrees.extend([d] * e)
        if is_reciprocal_poly(f):
            rec_deg += d * e
        else:
            nonrec.append((d, e, str(f.as_expr())))
    degrees.sort()
    irred = len(facs) == 1 and facs[0][1] == 1
    # non-reciprocal part
    nr_factors = sum(e for _, e, _ in nonrec)
    if nr_factors == 0:
        nr_status = "one"  # identically 1 (purely reciprocal)
    elif nr_factors == 1 and nonrec[0][1] == 1:
        nr_status = "irreducible"
    else:
        nr_status = "reducible"
    has_x1 = any(str(f.as_expr()) in ("x + 1", "x+1") for f, _ in facs)
    return {
        "irred": irred,
        "has_x1": has_x1,
        "min_deg": degrees[0] if degrees else n,
        "nr_status": nr_status,
        "nfactors": len(degrees),
    }


def census_n(n: int) -> dict:
    t0 = time.time()
    total = 1 << (n - 1)
    n_irred = 0
    n_x1 = 0
    n_nr_one = 0
    n_nr_irred = 0
    n_nr_red = 0
    min_deg_hist = {}
    # hash of reducible masks for a verifier
    h = hashlib.sha256()
    # only store masks when n is small
    reducible_masks = [] if n <= 16 else None
    for free in range(total):
        mask = 1 | (free << 1) | (1 << n)
        info = analyze(mask, n)
        if info["irred"]:
            n_irred += 1
        else:
            h.update(mask.to_bytes((n // 8) + 1, "little"))
            if reducible_masks is not None:
                reducible_masks.append(mask)
        if info["has_x1"]:
            n_x1 += 1
        if info["nr_status"] == "one":
            n_nr_one += 1
        elif info["nr_status"] == "irreducible":
            n_nr_irred += 1
        else:
            n_nr_red += 1
        md = info["min_deg"]
        min_deg_hist[str(md)] = min_deg_hist.get(str(md), 0) + 1
    dt = time.time() - t0
    return {
        "n": n,
        "total": total,
        "irreducible": n_irred,
        "reducible": total - n_irred,
        "p_irred": n_irred / total,
        "div_by_x_plus_1": n_x1,
        "nonrecip_part_is_1": n_nr_one,
        "nonrecip_part_irreducible": n_nr_irred,
        "nonrecip_part_reducible": n_nr_red,
        "min_factor_degree": min_deg_hist,
        "reducible_sha256": h.hexdigest(),
        "seconds": round(dt, 3),
    }


def main():
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "census.json")
    rows = []
    if os.path.exists(out_path):
        with open(out_path) as f:
            prev = json.load(f)
        rows = prev.get("rows", [])
    done = {r["n"] for r in rows}
    print(f"census n={nmin}..{nmax}  already have {sorted(done)}", flush=True)
    for n in range(nmin, nmax + 1):
        if n in done:
            print(f"n={n} skip (cached)", flush=True)
            continue
        print(f"n={n} start  total={1<<(n-1)}", flush=True)
        row = census_n(n)
        rows.append(row)
        rows.sort(key=lambda r: r["n"])
        with open(out_path, "w") as f:
            json.dump({"rows": rows}, f, indent=2)
            f.write("\n")
        print(
            f"n={n}  irred={row['irreducible']}/{row['total']}  "
            f"p={row['p_irred']:.6f}  x+1={row['div_by_x_plus_1']}  "
            f"nr_red={row['nonrecip_part_reducible']}  "
            f"{row['seconds']}s",
            flush=True,
        )


if __name__ == "__main__":
    main()
