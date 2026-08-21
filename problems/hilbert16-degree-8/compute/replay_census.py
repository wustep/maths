#!/usr/bin/env python3
"""Independent replay of the degree-8 T-curve census of
dmg-lab/CombinatorialPatchworking (arXiv:2602.06888 v3, Section 5.3
and Appendix B): 2,367 patchwork certificates, one per claimed real
scheme.

For every .pcom certificate we
  1. parse POINTS / MIN_WEIGHTS / MAXIMAL_CELLS / SIGNS / TYPE,
  2. validate the triangulation combinatorially (primitive, all 45
     lattice points of T_8 used, edge-manifold),
  3. certify convexity EXACTLY from their integer MIN_WEIGHTS
     (every non-vertex lattice point strictly above each cell plane),
  4. recompute the real scheme with our independent engine
     (tcurve.TCurve: reflection, antipodal gluing, double cover,
     nesting forest), and
  5. compare against the claimed TYPE and the o/p/n counts encoded
     in the directory name.
Also cross-checks the fast evaluator (fastcx) against the exact
engine on every certificate.

Output: replay_census.json with per-file results and a summary,
and census_schemes.txt with the 2,367 canonical scheme strings
(the diff target for the search).
"""

import json
import os
import subprocess
import tarfile
import time

from fractions import Fraction

from tcurve import TCurve, validate_triangulation, check_convexity, \
    lattice_points
from fastcx import Complex
from notation import canon, stats

D = 8
ARCHIVE = "data/deg8.pcoms.txz"


def parse_pcom(raw):
    data = json.loads(raw)
    sub = data["DUAL_SUBDIVISION"]
    pts = []
    for p in sub["POINTS"]:
        assert p[0] == 1 and len(p) == 3
        pts.append((p[1], p[2]))
    weights = sub["MIN_WEIGHTS"]
    cells = sub["MAXIMAL_CELLS"]
    pws = data["PATCHWORK"]
    assert len(pws) == 1
    signs_bool = pws[0]["SIGNS"]
    claimed = pws[0]["TYPE"]
    tris = [tuple(pts[i] for i in c) for c in cells]
    heights = {pts[k]: Fraction(weights[k]) for k in range(len(pts))}
    signs = {pts[k]: (-1 if signs_bool[k] else 1) for k in range(len(pts))}
    return tris, heights, signs, claimed


URL = ("https://raw.githubusercontent.com/dmg-lab/"
       "CombinatorialPatchworking/main/deg8.pcoms.txz")


def main():
    if not os.path.exists(ARCHIVE):
        os.makedirs("data", exist_ok=True)
        print(f"downloading {URL}")
        subprocess.run(["curl", "-sL", "-o", ARCHIVE, URL], check=True)
    tar = tarfile.open(ARCHIVE)
    names = sorted(n for n in tar.getnames() if n.endswith(".pcom"))
    print(f"{len(names)} certificates")
    results = []
    n_ok = n_fail = 0
    schemes = set()
    fast_mismatch = 0
    t0 = time.time()
    lp = set(lattice_points(D))
    for k, name in enumerate(names):
        raw = tar.extractfile(name).read().decode()
        tris, heights, signs, claimed = parse_pcom(raw)
        entry = {"file": name, "claimed": claimed}
        try:
            assert set(heights) == lp, "points are not the T_8 lattice"
            errs = validate_triangulation(D, tris)
            assert not errs, f"triangulation: {errs[:3]}"
            errs = check_convexity(D, tris, heights)
            assert not errs, f"convexity: {errs[:3]}"
            tc = TCurve(D, tris, signs)
            got = tc.scheme()
            want = canon(claimed)
            entry["computed"] = got
            # o/p/n from the directory name
            dirpart = name.split("/")[1]           # e.g. o22-p19-n03
            o, p, n = (int(x[1:]) for x in dirpart.split("-"))
            go, gp, gn = stats(got)
            assert got == want, f"scheme {got} != claimed {want}"
            assert (go, gp, gn) == (o, p, n), \
                f"stats {(go, gp, gn)} != dir {(o, p, n)}"
            # cross-check the fast evaluator
            base_pts = sorted(lp)
            cx = Complex(D, tris)
            svec = [signs[p2] for p2 in cx.base_pts]
            nc, fs = cx.eval(svec)
            if fs != got or nc != go:
                fast_mismatch += 1
                entry["fastcx"] = fs
            entry["ok"] = True
            n_ok += 1
            schemes.add(got)
        except AssertionError as e:
            entry["ok"] = False
            entry["error"] = str(e)
            n_fail += 1
        results.append(entry)
        if (k + 1) % 400 == 0:
            print(f"  {k+1}/{len(names)} ({time.time()-t0:.0f}s)")
    dt = time.time() - t0
    print(f"PASS {n_ok} / FAIL {n_fail} of {len(names)} in {dt:.0f}s; "
          f"{len(schemes)} distinct schemes; "
          f"fastcx mismatches: {fast_mismatch}")
    with open("replay_census.json", "w") as f:
        json.dump({"pass": n_ok, "fail": n_fail,
                   "distinct_schemes": len(schemes),
                   "fastcx_mismatches": fast_mismatch,
                   "failures": [r for r in results if not r["ok"]]},
                  f, indent=1)
    with open("census_schemes.txt", "w") as f:
        for s in sorted(schemes):
            f.write(s + "\n")
    print("wrote replay_census.json, census_schemes.txt")


if __name__ == "__main__":
    main()
