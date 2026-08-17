#!/usr/bin/env python3
"""Emit BEL k=2 sum-cover certificates for q ≡ 1 (mod 6)."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bel import pick_r, generators, covered_count, embed

BEL = math.sqrt(8 / 3)


def main():
    outdir = Path("compute/certs")
    outdir.mkdir(parents=True, exist_ok=True)
    index = []
    for q in [7, 13, 19, 31, 37, 43, 61]:
        rs = pick_r(q)
        if rs is None:
            print(f"skip q={q}")
            continue
        r1, r2 = rs
        X, co, cu = generators(r1, r2)
        cov, n, Apts = covered_count(X, r1, r2)
        A = sorted({embed(p, r1, r2) for p in Apts})
        rec = {
            "family": "bel-k2",
            "source": "Bevan-Erskine-Lewis arXiv:1506.04962 Thm 10(a) / Cor 18",
            "q": q,
            "r1": r1,
            "r2": r2,
            "w": 6,
            "n": n,
            "m": len(A),
            "co": co,
            "cu": cu,
            "product_covered": cov,
            "product_ok": cov == n,
            "ratio": len(A) / math.sqrt(n),
            "bel_const": BEL,
            "A": A,
        }
        path = outdir / f"bel_q{q}.json"
        path.write_text(json.dumps(rec, indent=2))
        print(
            f"q={q} n={n} m={len(A)} ratio={rec['ratio']:.5f} "
            f"prod_ok={rec['product_ok']} -> {path}",
            flush=True,
        )
        rec2 = dict(rec)
        rec2.pop("A")
        index.append(rec2)
    Path("compute/bel_index.json").write_text(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
