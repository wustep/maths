#!/usr/bin/env python3
"""Aggregate the Haas zone-decomposition sweeps against the record.

Reads runs3/*.jsonl (gitignored) and reports, against Table 1 of
arXiv:2602.06888 v3 as stored in record.py:

  * how many certified regular triangulations were swept exhaustively
    (a `tri_done` record means the FULL affine subspace
    eta + span{delta_S} of that triangulation was evaluated, i.e. the
    complete maximal-T-curve stratum it supports),
  * which of the 89 M-schemes were realized, split into the paper's
    38 T-realized / 39 undecided / 12 impossible classes,
  * any scheme at all that is missing from the 2,367-census.
"""

import glob
import json
import sys

from notation import canon
from record import M_SCHEMES, SIX_OPEN


def main():
    pats = sys.argv[1:] or ["runs3/*.jsonl"]
    files = [f for p in pats for f in glob.glob(p)]
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    hit, tri_done, evals, new = set(), [], 0, {}
    for f in files:
        if "pilot" in f or "spantest" in f:
            continue
        for line in open(f):
            r = json.loads(line)
            k = r.get("kind")
            if k == "tri_done":
                tri_done.append(r)
                evals += r["evals"]
            elif k == "summary":
                pass
            elif k in ("MAX", "NEW"):
                hit.add(r["scheme"])
                if r["scheme"] not in census:
                    new.setdefault(r["scheme"], r)
    tre = {s for s, v in M_SCHEMES.items() if v}
    unk = {s for s, v in M_SCHEMES.items() if not v and s in census} 
    print(f"triangulations swept exhaustively : {len(tri_done)}")
    print(f"sign distributions evaluated      : {evals:,}")
    print(f"distinct schemes logged           : {len(hit)}")
    maxhit = {s for s in hit if canon(s) in M_SCHEMES}
    print(f"M-schemes (of the 89) realized    : {len(maxhit)}")
    print(f"  of the paper's 38 T-realized    : "
          f"{len(maxhit & tre)} / {len(tre)}")
    other = maxhit - tre
    print(f"  outside the paper's 38          : {len(other)}"
          + (f"  {sorted(other)}" if other else ""))
    print(f"  among the six algebraically open: "
          f"{len(maxhit & set(SIX_OPEN))}")
    print(f"schemes missing from the 2,367    : {len(new)}")
    for s in sorted(new):
        print(f"    {s}   ({new[s].get('ncomp')} ovals)")
    if tri_done:
        rk = sorted(r["rank"] for r in tri_done)
        print(f"twist-rank of swept triangulations: min {rk[0]}, "
              f"median {rk[len(rk)//2]}, max {rk[-1]}")


if __name__ == "__main__":
    main()
