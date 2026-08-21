#!/usr/bin/env python3
"""Aggregate search output, re-verify every witness EXACTLY, and diff
against the published record.

Reads runs/*.jsonl (search_m8.py output).  For every distinct scheme:
re-run the full exact pipeline (validate_triangulation,
check_convexity with Fraction heights, TCurve scheme) on its stored
witness.  A scheme counts only if the exact pipeline agrees.

Diffs:
  * vs census_schemes.txt (the replayed 2,367 of arXiv:2602.06888 v3):
    anything NOT in the census is a NEW-SCHEME CANDIDATE (dent C).
  * 22-oval schemes vs record.py tables:
      - in SIX_OPEN        -> ALGEBRAIC-REALIZATION CANDIDATE (dent A)
      - in UNDECIDED_T     -> NEW T-CURVE M-SCHEME CANDIDATE (dent C)
      - in IMPOSSIBLE_T    -> BUG (violates their Theorem 21)
      - in T_REALIZED      -> replay of a known realization
Candidates get their full certificates written to certs/ for
independent replay via `python3 tcurve.py verify <cert>`.

Output: found_schemes.json (summary) and certs/*.json.
"""

import glob
import json
import os

from fractions import Fraction

from tcurve import TCurve, validate_triangulation, check_convexity
from notation import stats
import record

D = 8


def load_runs(pattern="runs/run_*.jsonl"):
    witnesses = {}   # scheme -> (triangles, heights, signs, src)
    summaries = []
    for path in sorted(glob.glob(pattern)):
        tris_by_id = {}
        with open(path) as f:
            for line in f:
                rec = json.loads(line)
                if rec["kind"] == "tri":
                    tris_by_id[rec["id"]] = rec
                elif rec["kind"] == "scheme":
                    s = rec["scheme"]
                    if s in witnesses:
                        continue
                    tri = tris_by_id[rec["tri"]]
                    witnesses[s] = (tri["triangles"], tri["heights"],
                                    rec["signs"], path)
                elif rec["kind"] == "summary":
                    summaries.append(rec)
    return witnesses, summaries


def main():
    witnesses, summaries = load_runs()
    print(f"{len(witnesses)} distinct schemes from "
          f"{len(summaries)} completed workers")
    total_evals = sum(s.get("evals", 0) for s in summaries)
    total_tris = sum(s.get("triangulations", 0) for s in summaries)

    census = {line.strip() for line in open("census_schemes.txt")}

    verified = []
    broken = []
    for scheme, (tris_j, hts_j, signs_j, src) in sorted(witnesses.items()):
        tris = [tuple(tuple(v) for v in t) for t in tris_j]
        heights = {}
        for k, v in hts_j.items():
            i, j = (int(x) for x in k.split(","))
            heights[(i, j)] = Fraction(v)
        signs = {}
        for k, v in signs_j.items():
            i, j = (int(x) for x in k.split(","))
            signs[(i, j)] = v
        errs = validate_triangulation(D, tris)
        errs += check_convexity(D, tris, heights)
        got = None
        if not errs:
            got = TCurve(D, tris, signs).scheme()
            if got != scheme:
                errs.append(f"exact scheme {got} != recorded {scheme}")
        if errs:
            broken.append({"scheme": scheme, "src": src,
                           "errors": errs[:3]})
        else:
            verified.append(scheme)

    by_ovals = {}
    for s in verified:
        by_ovals.setdefault(stats(s)[0], []).append(s)

    new_schemes = sorted(s for s in verified if s not in census)
    m_found = sorted(by_ovals.get(22, []))
    hits_open = [s for s in m_found if s in record.SIX_OPEN]
    hits_undecided = [s for s in m_found if s in record.UNDECIDED_T]
    hits_impossible = [s for s in m_found if s in record.IMPOSSIBLE_T]
    hits_known = [s for s in m_found if s in record.T_REALIZED]
    m_unknown = [s for s in m_found if s not in record.M_SCHEMES]

    os.makedirs("certs", exist_ok=True)
    ncert = 0
    for s in new_schemes + hits_open + hits_undecided + hits_impossible:
        tris_j, hts_j, signs_j, src = witnesses[s]
        name = "certs/candidate_%03d.json" % ncert
        with open(name, "w") as f:
            json.dump({"d": D, "claimed_scheme": s,
                       "triangles": tris_j, "heights": hts_j,
                       "signs": {k: v for k, v in signs_j.items()},
                       "source": src}, f)
        ncert += 1

    summary = {
        "workers": len(summaries),
        "total_evals": total_evals,
        "total_triangulations": total_tris,
        "distinct_schemes_seen": len(witnesses),
        "verified_exactly": len(verified),
        "broken_witnesses": broken,
        "schemes_by_oval_count": {k: len(v)
                                  for k, v in sorted(by_ovals.items())},
        "in_census": len(verified) - len(new_schemes),
        "NEW_not_in_census": new_schemes,
        "m_schemes_found": m_found,
        "m_hits_known_T": len(hits_known),
        "m_hits_SIX_OPEN": hits_open,
        "m_hits_undecided_T": hits_undecided,
        "m_hits_impossible_T_BUG_IF_NONEMPTY": hits_impossible,
        "m_not_in_orevkov_table_BUG_IF_NONEMPTY": m_unknown,
    }
    with open("found_schemes.json", "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("NEW_not_in_census", "m_schemes_found")},
                     indent=1))
    print(f"new schemes not in census: {len(new_schemes)}")
    for s in new_schemes[:20]:
        print("  NEW:", s)
    print(f"M-schemes found: {len(m_found)} "
          f"(known T: {len(hits_known)}, open-six: {len(hits_open)}, "
          f"undecided: {len(hits_undecided)}, "
          f"impossible(BUG): {len(hits_impossible)})")
    print("wrote found_schemes.json"
          + (f" and {ncert} candidate certs" if ncert else ""))


if __name__ == "__main__":
    main()
