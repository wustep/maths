"""m=0 smoke test: G = L1 - L3, last root (9+√33)/2."""

from ce_laguerre import (
    T,
    build_G,
    build_H,
    analyze_signs,
    last_positive_root_numeric,
    center_density,
    ratio_vs_hex,
    qq,
    laguerre_Q,
)
import sympy as sp


def main():
    L1 = laguerre_Q(1)
    L3 = laguerre_Q(3)
    Gexact = L1 - L3
    print("G =", Gexact.as_expr())
    # G = 2t - 3t^2/2 + t^3/6 = t(t^2 - 9t + 12)/6
    roots = sp.solve(Gexact.as_expr(), T)
    print("roots", roots)
    last = max(r for r in roots if r.is_real and r > 0)
    print("last exact", last, float(last))

    built = build_G(0, [])
    print("build_G", built[0].as_expr() if built else None)
    G, a = built
    print("a_odd", a)
    print("numeric last", last_positive_root_numeric(G))

    # Use a rational R just above the last root
    last_f = float(last)
    for den in (1, 2, 4, 8, 10, 16, 32, 100, 128):
        R = qq(f"{int(last_f * den) + 1}/{den}")
        if float(R) <= last_f:
            continue
        Hpack = build_H(0, [], R, G)
        if Hpack is None:
            print("H fail", R)
            continue
        H, b = Hpack
        signs = analyze_signs(G, H, R)
        print(
            f"R={R}={float(R):.6f}  dens={center_density(R):.6f}  "
            f"ratio={ratio_vs_hex(R):.6f}  ok={signs['theorem32_ok']}  {signs}"
        )
        if signs["theorem32_ok"]:
            print("SMOKE PASS")
            return 0
    print("SMOKE FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
