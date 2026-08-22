#!/usr/bin/env python3
"""Cross-check zonec against the Python sweep on one triangulation.

Enumerates the whole affine subspace in Python (fastcx) and compares the set
of scheme strings with the set zonec's witnesses decode to.  A pass means the
C fingerprint is exactly as fine as the real scheme on this triangulation, so
the C sweep loses nothing.
"""
import json
import subprocess
import sys
import tarfile

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span
import zone_collect


def python_span(cert):
    tar = tarfile.open(ARCHIVE)
    tris, _h, _s, _c = parse_pcom(tar.extractfile(cert).read().decode())
    cx, pts, basis, _n = export_span.build(tris)
    eta = haas.eta()
    base = [1 if eta[p] == 0 else -1 for p in pts]
    seen, nmax, nval = {}, 0, 0
    for m in range(1 << len(basis)):
        acc = 0
        for i in range(len(basis)):
            if m >> i & 1:
                acc ^= basis[i]
        signs = [(-base[j] if acc >> j & 1 else base[j]) for j in range(len(pts))]
        nc, sch = cx.eval(signs)
        if sch is None:
            continue
        nval += 1
        if nc == 22:
            nmax += 1
        seen.setdefault(sch, nc)
    return seen, nval, nmax, len(basis)


def main():
    cert = sys.argv[1]
    task = "/tmp/val_task.txt"
    subprocess.run([sys.executable, "export_span.py", cert, task], check=True)
    subprocess.run(["./zonec", task, "0", "1", "/tmp/val.jsonl"], check=True)
    got, summ = zone_collect.schemes_for(cert, ["/tmp/val.jsonl"])
    py, nval, nmax, rank = python_span(cert)
    ok = set(got) == set(py)
    print(json.dumps({"cert": cert, "rank": rank,
                      "python_schemes": len(py), "c_schemes": len(got),
                      "python_valid": nval, "c_valid": summ[0]["valid"],
                      "python_maximal": nmax, "c_maximal": summ[0]["maximal"],
                      "sets_equal": ok,
                      "only_python": sorted(set(py) - set(got)),
                      "only_c": sorted(set(got) - set(py))}))
    sys.exit(0 if ok and nval == summ[0]["valid"] and nmax == summ[0]["maximal"] else 1)


if __name__ == "__main__":
    main()
