#!/usr/bin/env python3
"""Exact, self-contained verification of every claimed NEW T-curve.

Reads certs/new_schemes.json (a list of certificates, each carrying its
own triangulation, integer lifting and sign vector) and, for each one:

  1. validates the triangulation combinatorially (primitive, all 45
     lattice points of T_8 used, edge-manifold)  -- tcurve.validate_,
  2. certifies EXACTLY, in Fraction arithmetic, that the integer
     lifting induces that triangulation as its regular subdivision
     (so Viro's theorem applies and the T-curve is algebraic),
  3. recomputes the real scheme from scratch with tcurve.TCurve
     (reflection, antipodal gluing, S^2 double cover, nesting forest),
  4. checks the recomputed scheme against the claimed one,
  5. checks that the scheme is NOT among the 2,367 of
     arXiv:2602.06888 v3 -- both against census_schemes.txt (our
     replay) and against the paper's own .pcom file names in
     deg8.pcoms.txz when the archive is present.

Exit status is nonzero if anything fails.

Usage: python3 verify_new.py [certs/new_schemes.json]
"""

import json
import os
import sys
import tarfile
from fractions import Fraction

from notation import canon
from tcurve import TCurve, check_convexity, validate_triangulation

D8 = 8


def paper_name(scheme):
    """Our canonical <a u 1<b>> string -> the paper's (av1(b)) file name."""
    s = scheme.strip()
    assert s.startswith("<") and s.endswith(">")
    s = s[1:-1].replace(" u ", "v").replace("<", "(").replace(">", ")")
    return "(" + s + ")"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "certs/new_schemes.json"
    certs = json.load(open(path))
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    assert len(census) == 2367, f"census has {len(census)} schemes"
    arch = "data/deg8.pcoms.txz"
    names = None
    if os.path.exists(arch):
        names = {n for n in tarfile.open(arch).getnames()
                 if n.endswith(".pcom")}
        assert len(names) == 2367, f"archive has {len(names)} certs"
    fails = 0
    for c in certs:
        tag = c["scheme"]
        tris = [tuple(tuple(v) for v in t) for t in c["triangles"]]
        heights = {tuple(int(x) for x in k.split(",")): Fraction(v)
                   for k, v in c["heights"].items()}
        signs = {tuple(int(x) for x in k.split(",")): int(v)
                 for k, v in c["signs"].items()}
        errs = []
        errs += [f"triangulation: {e}"
                 for e in validate_triangulation(D8, tris)]
        errs += [f"convexity: {e}"
                 for e in check_convexity(D8, tris, heights)]
        got = TCurve(D8, tris, signs).scheme()
        if canon(got) != canon(tag):
            errs.append(f"scheme mismatch: recomputed {got}, claimed {tag}")
        if canon(got) in census:
            errs.append("scheme IS in the replayed 2,367-census")
        if names is not None:
            pn = paper_name(canon(got))
            if any(n.endswith("/" + pn + ".pcom") for n in names):
                errs.append(f"paper has a certificate named {pn}.pcom")
        n = TCurve(D8, tris, signs).counts()
        print(f"{'FAIL' if errs else 'PASS'}  {tag}"
              f"  ovals={n['ovals']}  source={c.get('source', '?')}")
        for e in errs:
            print("      " + e)
        fails += bool(errs)
    print(f"\n{len(certs) - fails}/{len(certs)} certificates verified "
          f"as T-curves outside the published census")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
