#!/usr/bin/env python3
"""Turn zonec witnesses into scheme strings, and check them against the census.

zonec only decides which sign vectors are worth looking at (one per distinct
canonical fingerprint).  The scheme of record is recomputed here on the exact
Python complex, and anything outside the paper's 2,367 is written out for the
full Fraction-arithmetic verifier (verify_new.py) to certify.
"""
import json
import sys
import tarfile

from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE

D8 = 8


def schemes_for(cert, witness_files):
    tar = tarfile.open(ARCHIVE)
    tris, hfrac, _s, _c = parse_pcom(tar.extractfile(cert).read().decode())
    tris = [tuple(tuple(v) for v in t) for t in tris]
    cx = Complex(D8, tris)
    pts = cx.base_pts
    out, summ = {}, []
    for wf in witness_files:
        for line in open(wf):
            d = json.loads(line)
            if d["kind"] == "summary":
                summ.append(d)
                continue
            signs = d["signs"]
            nc, sch = cx.eval(signs)
            if sch is None:
                continue
            assert nc == d["ncomp"], (nc, d["ncomp"])
            out.setdefault(sch, {"scheme": sch, "ncomp": nc, "cert": cert,
                                 "sweep_index": d["sweep_index"],
                                 "signs": {f"{pts[j][0]},{pts[j][1]}": signs[j]
                                           for j in range(len(pts))},
                                 "triangles": [[list(v) for v in t] for t in tris],
                                 "heights": {f"{p[0]},{p[1]}": int(v)
                                             for p, v in hfrac.items()}})
    return out, summ


def main():
    cert = sys.argv[1]
    files = sys.argv[2:-1]
    dest = sys.argv[-1]
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    got, summ = schemes_for(cert, files)
    evals = sum(s["evals"] for s in summ)
    exhaustive = (sum(s["hi"] - s["lo"] for s in summ) ==
                  (1 << summ[0]["rank"]) if summ else False)
    novel = [r for s, r in sorted(got.items()) if s not in census]
    rec = {"cert": cert, "rank": summ[0]["rank"] if summ else None,
           "evals": evals, "exhaustive": exhaustive,
           "distinct_schemes": len(got),
           "maximal": sum(s["maximal"] for s in summ),
           "schemes": sorted(got),
           "novel": [r["scheme"] for r in novel]}
    with open(dest, "w") as f:
        f.write(json.dumps(rec) + "\n")
        for r in novel:
            f.write(json.dumps({"kind": "NOVEL", **r}) + "\n")
    print(json.dumps({k: rec[k] for k in
                      ("cert", "rank", "evals", "exhaustive",
                       "distinct_schemes", "novel")}))


if __name__ == "__main__":
    main()
