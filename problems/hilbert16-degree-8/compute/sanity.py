#!/usr/bin/env python3
"""Sanity suite for the T-curve engine against classical facts.

Facts used (all standard, see RESEARCH.md for sources):
  * Harnack's M-curve exists in every degree; component count is
    g+1 = (d-1)(d-2)/2 + 1.
  * Even degree d = 2k: Harnack's curve has scheme
    <(alpha) u 1<beta>> with beta = (d-2)(d-4)/8 nested empty ovals
    (for d=4: <4>), alpha = g - beta.
      d=2: <1>, d=4: <4>, d=6: <9 u 1<1>>, d=8: <18 u 1<3>>.
  * Odd degree: one pseudoline; d=1: <J>; d=3 Harnack: <J u 1>;
    d=5 Harnack: <J u 6>.
  * All-plus signs in degree 2 give ONE oval: the Viro polynomial is
    1 + t(x+y) + t^3(x^2+xy+y^2) (heights i^2+ij+j^2), and on y=0 the
    discriminant t^2(1-4t) is positive for small t, so the conic has
    real points; a nonempty smooth real conic is a single oval.
    (First guess "empty" forgot the t-weights; 1+x+y+x^2+xy+y^2 with
    unit coefficients IS empty, but that is not the Viro polynomial.)
  * Component counts can never exceed Harnack's bound g+1.
"""

import sys

from tcurve import TCurve, check_convexity, validate_triangulation
from standard import (standard_triangulation, standard_heights,
                      harnack_signs, all_plus_signs)

FAIL = 0


def check(name, got, want=None):
    global FAIL
    ok = (want is None) or (got == want)
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}"
          + ("" if ok or want is None else f"   (want {want})"))
    if not ok:
        FAIL += 1


def main():
    # exact convexity certificates for the standard triangulation
    for d in range(1, 9):
        tris = standard_triangulation(d)
        errs = validate_triangulation(d, tris)
        check(f"d={d} standard triangulation valid", errs, [])
        errs = check_convexity(d, tris, standard_heights(d))
        check(f"d={d} standard triangulation convex (exact)", errs, [])

    # Harnack signs
    harnack_expect = {
        1: "<J>", 2: "<1>", 3: "<J u 1>", 4: "<4>", 5: "<J u 6>",
        6: "<9 u 1<1>>", 8: "<18 u 1<3>>",
    }
    for d in range(1, 9):
        tc = TCurve(d, standard_triangulation(d), harnack_signs(d))
        g1 = (d - 1) * (d - 2) // 2 + 1
        c = tc.counts()
        check(f"d={d} Harnack component count", c["components"], g1)
        s = tc.scheme()
        if d in harnack_expect:
            check(f"d={d} Harnack scheme", s, harnack_expect[d])
        else:
            print(f"info d={d} Harnack scheme: {s}")

    # all-plus conic: one oval (see module docstring)
    tc = TCurve(2, standard_triangulation(2), all_plus_signs(2))
    check("d=2 all-plus is one oval", tc.scheme(), "<1>")

    # d=8 all-plus: whatever it is, it must respect Harnack's bound
    tc = TCurve(8, standard_triangulation(8), all_plus_signs(8))
    c = tc.counts()
    check("d=8 all-plus within Harnack bound", c["components"] <= 22, True)
    print(f"info d=8 all-plus scheme: {tc.scheme()}")

    # a broken convexity certificate must be rejected
    tris = standard_triangulation(2)
    bad = standard_heights(2)
    bad[(1, 0)] = bad[(1, 0)] + 10  # lift a used vertex way up
    errs = check_convexity(2, tris, bad)
    check("broken heights rejected", bool(errs), True)

    print()
    if FAIL:
        print(f"{FAIL} sanity checks FAILED")
        sys.exit(1)
    print("all sanity checks passed")


if __name__ == "__main__":
    main()
