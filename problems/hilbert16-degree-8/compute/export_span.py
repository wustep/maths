#!/usr/bin/env python3
"""Export a census triangulation's prepared complex + twist basis for zonec.

The C sweeper does not rebuild any geometry: everything it reads here is
produced by the same `fastcx.Complex` constructor and the same
`haas.all_splits()` that the Python sweep used, so the two searches walk
exactly the same affine subspace eta + span{delta_S}.

Format (text, one field per line group):
  npts nv F nedges rank
  vbase[nv]
  vflip[nv]
  rtris[F][3]
  edges[nedges]: t1 t2 cross s1t1 s1t2 s2t1 s2t2 u1 w1
  eta signs[npts]  (+-1, indexed like base_pts)
  basis[rank]      (45-bit masks over base_pts, low bit = point 0)
  points[npts]: x y
"""
import json
import sys
import tarfile

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis


def build(tris):
    tris = [tuple(tuple(v) for v in t) for t in tris]
    cx = Complex(D8, tris)
    pts = cx.base_pts
    E = edgeset(tris)
    S = [s for s in haas.all_splits() if s.edges <= E]
    basis = f2_basis([delta_bits(s, pts) for s in S])
    return cx, pts, basis, len(S)


def emit(cx, pts, basis, path):
    o = []
    o.append(f"{len(pts)} {cx.nv} {cx.F} {len(cx.edges)} {len(basis)}")
    o.append(" ".join(map(str, cx.vbase)))
    o.append(" ".join(map(str, cx.vflip)))
    for t in cx.rtris:
        o.append(" ".join(map(str, t)))
    for (t1, t2, cross, u1, u2, w1, w2) in cx.edges:
        o.append(" ".join(map(str, (
            t1, t2, cross,
            3 * t1 + cx.slot[t1][u1], 3 * t2 + cx.slot[t2][u2],
            3 * t1 + cx.slot[t1][w1], 3 * t2 + cx.slot[t2][w2],
            u1, w1))))
    eta = haas.eta()
    o.append(" ".join("1" if eta[p] == 0 else "-1" for p in pts))
    for b in basis:
        o.append(str(b))
    for p in pts:
        o.append(f"{p[0]} {p[1]}")
    open(path, "w").write("\n".join(o) + "\n")


def main():
    cert, path = sys.argv[1], sys.argv[2]
    tar = tarfile.open(ARCHIVE)
    tris, hfrac, _s, _c = parse_pcom(tar.extractfile(cert).read().decode())
    cx, pts, basis, nsplits = build(tris)
    emit(cx, pts, basis, path)
    print(json.dumps({"cert": cert, "rank": len(basis), "nsplits": nsplits,
                      "F": cx.F, "nv": cx.nv, "nedges": len(cx.edges)}))


if __name__ == "__main__":
    main()
