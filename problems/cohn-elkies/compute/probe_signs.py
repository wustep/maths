"""Numerical + Descartes probe of F and hatF for Table 4 reconstruction."""

import time
import numpy as np
import sympy as sp

from ce_laguerre import build_G, build_H, qq, T, hex_R, last_odd_positive_root_numeric


def descartes(coeffs):
    signs = []
    for c in coeffs:
        if c == 0:
            continue
        s = 1 if c > 0 else -1
        if not signs or signs[-1] != s:
            signs.append(s)
    return max(0, len(signs) - 1)


def main():
    ts = [qq(s) for s in ["2177/100", "2902/100", "5079/100", "6534/100", "9019/100"]]
    print("building G", flush=True)
    G, a = build_G(5, ts)
    last = last_odd_positive_root_numeric(G)
    print("last odd", last, "hex", hex_R(), flush=True)
    R = qq("72552/10000")
    print("building H", flush=True)
    H, b = build_H(5, ts, R, G)
    F = sp.Poly(-G + H, T, domain=sp.QQ)
    hatF = sp.Poly(G + H, T, domain=sp.QQ)
    print("deg F,hatF", F.degree(), hatF.degree(), flush=True)
    print("F(0)", F.eval(0), "hatF(0)", hatF.eval(0), flush=True)
    print("F(R)", F.eval(R), "hatF(R)", hatF.eval(R), "hatF'(R)", hatF.diff(T).eval(R), flush=True)
    print("LC F", F.LC(), "LC hatF", hatF.LC(), flush=True)

    # primitive integer hatF
    hatZ = hatF.primitive()[1].set_domain(sp.ZZ)
    FZ = F.primitive()[1].set_domain(sp.ZZ)
    print("descartes hatF", descartes(hatZ.all_coeffs()), "descartes F", descartes(FZ.all_coeffs()), flush=True)
    print("coeff bits hatF", max(int(abs(c)).bit_length() for c in hatZ.all_coeffs()), flush=True)

    # divide out (t-R)^2
    linear = sp.Poly(T - R, T, domain=sp.QQ)
    Q, rem = sp.div(hatF, linear**2, domain=sp.QQ)
    print("div rem", rem, "deg Q", Q.degree(), flush=True)
    QZ = Q.primitive()[1].set_domain(sp.ZZ)
    print("descartes Q", descartes(QZ.all_coeffs()), "Q(0)", Q.eval(0), "LC Q", Q.LC(), flush=True)

    # numeric samples
    print("\nnumeric samples (mpmath via float of exact):", flush=True)
    xs = [0, 0.5, 1, 2, 4, 6, 7, 7.2552, 8, 10, 15, 21.77, 29.02, 40, 50.79, 65, 90, 120, 200]
    for x in xs:
        xr = qq(str(x)) if not isinstance(x, str) else qq(x)
        # use float of exact
        try:
            fv = float(F.eval(xr))
            hv = float(hatF.eval(xr))
        except Exception as e:
            fv, hv = str(e), ""
        print(f"  t={float(xr):8.3f}  F={fv: .4e}  hatF={hv: .4e}", flush=True)

    print("\ntry sympy count_roots on Q (timeout-sensitive)", flush=True)
    t0 = time.time()
    try:
        npos = QZ.count_roots(0, sp.oo)
        print("count_roots Q on (0,oo)", npos, f"in {time.time()-t0:.2f}s", flush=True)
    except Exception as e:
        print("count_roots failed", e, f"after {time.time()-t0:.2f}s", flush=True)

    print("try real_roots Q", flush=True)
    t0 = time.time()
    try:
        rts = sp.real_roots(Q)
        print("n real_roots", len(rts), f"in {time.time()-t0:.2f}s", flush=True)
        for r in rts:
            print(" ", r, float(r), flush=True)
    except Exception as e:
        print("real_roots failed", e, f"after {time.time()-t0:.2f}s", flush=True)


if __name__ == "__main__":
    main()
