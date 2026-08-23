#!/usr/bin/env python3
"""Aggregate the thickc sweep (thick_drive.py output) into one summary.

Reads <outdir>/h*.jsonl (one `tri_done` record per census triangulation
swept) and <outdir>/h*_novel.jsonl (a full certificate for every scheme
the sweep saw that is not in census_schemes.txt).

Anything outside the census is split into
  * schemes already certified in certs/new_schemes.json (the seventeen),
  * genuinely unseen schemes -> written to certs/thick_candidates.json
    in the exact format verify_new.py consumes.

Output: certs/thick_summary.json.

Usage: python3 thick_collect.py [outdir] [maxrank]
"""
import collections
import glob
import json
import os
import sys

from notation import canon, stats


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "thick_out"
    maxrank = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    known = {canon(c["scheme"]) for c in
             json.load(open("certs/new_schemes.json"))}
    scope = [d for d in json.load(open("span_tasks.json"))
             if d["rank"] <= maxrank]

    done, dup = {}, 0
    for fn in sorted(glob.glob(f"{outdir}/h*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for line in open(fn):
            r = json.loads(line)
            if r.get("kind") != "tri_done":
                continue
            if r["cert"] in done:
                dup += 1
                continue
            done[r["cert"]] = r

    novel = {}
    for fn in sorted(glob.glob(f"{outdir}/h*_novel.jsonl")):
        for line in open(fn):
            r = json.loads(line)
            s = canon(r["scheme"])
            novel.setdefault(s, r)

    complete = [r for r in done.values() if r["complete"]]
    ranks = collections.Counter(r["rank"] for r in complete)
    schemes = set()
    for r in done.values():
        schemes.update(r.get("novel", []))

    candidates = sorted(s for s in novel if s not in census and s not in known)
    rediscovered = sorted(s for s in novel if s in known)

    os.makedirs("certs", exist_ok=True)
    cand_path = None
    if candidates:
        cand_path = "certs/thick_candidates.json"
        json.dump([{"scheme": s,
                    "triangles": novel[s]["triangles"],
                    "heights": novel[s]["heights"],
                    "signs": novel[s]["signs"],
                    "source": novel[s]["source"]} for s in candidates],
                  open(cand_path, "w"), indent=1)

    summary = {
        "search": "radius-1 thickening of the WHOLE Haas maximal stratum "
                  "eta + span{delta_S} of a census triangulation: every "
                  "point of the span and all 45 single-coordinate flips "
                  "at each, 46 * 2^rank evaluations per triangulation",
        "driver": "thick_drive.py <w> <nworkers> %d %s" % (maxrank, outdir),
        "engine": "thickc.c (tcore.h), gcc -O3 -march=native",
        "scope": {"census_triangulations_total": 184,
                  "maxrank": maxrank,
                  "in_scope": len(scope),
                  "m22_in_scope": sum(1 for d in scope
                                      if "/o22-" in d["cert"])},
        "triangulations_swept": len(done),
        "triangulations_complete": len(complete),
        "triangulations_truncated": len(done) - len(complete),
        "m22_triangulations_swept": sum(1 for c in done if "/o22-" in c),
        "ranks_completed": {str(k): v for k, v in sorted(ranks.items())},
        "ranks_outstanding": {
            str(k): v for k, v in sorted(collections.Counter(
                d["rank"] for d in scope if d["cert"] not in done).items())},
        "total_evaluations": sum(r["evals"] for r in done.values()),
        "distinct_schemes_seen_per_tri_max":
            max((r["distinct_schemes"] for r in done.values()), default=0),
        "distinct_schemes_seen_per_tri_min":
            min((r["distinct_schemes"] for r in done.values()), default=0),
        "distinct_outside_census": len(novel),
        "outside_census_already_certified": len(rediscovered),
        "outside_census_already_certified_list": rediscovered,
        "NEW_candidates": candidates,
        "NEW_candidates_ovals": {s: stats(s)[0] for s in candidates},
        "candidate_cert_file": cand_path,
        "duplicate_tri_records": dup,
    }
    json.dump(summary, open("certs/thick_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items()
                      if k != "outside_census_already_certified_list"},
                     indent=1))


if __name__ == "__main__":
    main()
