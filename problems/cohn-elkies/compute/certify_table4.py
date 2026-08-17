"""Exact certificate attempt from CE 2003 Table 4 d=2 roots."""

import json
import time
from pathlib import Path

from ce_laguerre import (
    build_G,
    build_H,
    analyze_signs,
    last_odd_positive_root_numeric,
    qq,
    center_density,
    ratio_vs_hex,
    hex_R,
    T,
)
import sympy as sp


CE_T = ["2177/100", "2902/100", "5079/100", "6534/100", "9019/100"]


def main():
    ts = [qq(s) for s in CE_T]
    print("hex R", hex_R(), flush=True)
    t0 = time.time()
    built = build_G(5, ts)
    print(f"build_G {time.time()-t0:.3f}s", flush=True)
    G, a = built
    last = last_odd_positive_root_numeric(G)
    print("last odd root of G", last, flush=True)

    # R must sit strictly after that last sign change
    candidates = [
        "72552/10000",  # CE printed 7.25520
        "181381/25000",
        "72553/10000",
        "14511/2000",
        "363/50",
        "73/10",
    ]
    if last is not None:
        for den in (10000, 20000, 50000, 100000, 25000, 12500):
            num = int(last * den) + 1
            candidates.append(f"{num}/{den}")

    best = None
    for Rs in dict.fromkeys(candidates):
        R = qq(Rs)
        if last is not None and float(R) <= last:
            print(f"skip R={Rs} <= last", flush=True)
            continue
        print(f"\n--- trying R={Rs} = {float(R):.10f} ---", flush=True)
        t0 = time.time()
        Hpack = build_H(5, ts, R, G)
        print(f"build_H {time.time()-t0:.3f}s ok={Hpack is not None}", flush=True)
        if Hpack is None:
            continue
        H, b = Hpack
        t0 = time.time()
        signs = analyze_signs(G, H, R)
        print(f"analyze {time.time()-t0:.3f}s", flush=True)
        print("signs", signs, flush=True)
        print(
            f"dens={center_density(R):.12f} ratio={ratio_vs_hex(R):.12f}",
            flush=True,
        )
        if signs["theorem32_ok"]:
            rec = {
                "source": "CE2003 Table 4 two-decimal roots, exact Q reconstruction",
                "m": 5,
                "t_roots": CE_T,
                "R": Rs,
                "R_float": float(R),
                "last_odd_G": last,
                "hex_R": hex_R(),
                "center_density": center_density(R),
                "ratio_vs_hex": ratio_vs_hex(R),
                "a_odd": [str(c) for c in a],
                "b_even": [str(c) for c in b],
                "G_monomial": [str(c) for c in G.all_coeffs()],
                "H_monomial": [str(c) for c in H.all_coeffs()],
                "F_monomial": [str(c) for c in sp.Poly(-G + H, T, domain=sp.QQ).all_coeffs()],
                "hatF_monomial": [str(c) for c in sp.Poly(G + H, T, domain=sp.QQ).all_coeffs()],
                "signs": signs,
                "published_CE_table3_center_density": 0.28868,
                "published_CE_table4_R": 7.25520,
            }
            out = Path("certs/ce_table4.json")
            out.parent.mkdir(exist_ok=True)
            out.write_text(json.dumps(rec, indent=2))
            print("WROTE", out, flush=True)
            best = rec
            break
    return 0 if best else 2


if __name__ == "__main__":
    raise SystemExit(main())
