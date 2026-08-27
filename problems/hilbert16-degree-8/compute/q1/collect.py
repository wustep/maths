#!/usr/bin/env python3
"""Aggregate every q1 search log into certs/q1_summary.json.

Anything outside census+17 is written to certs/new_schemes.json in the
format verify_new.py consumes.  A stranger then runs

    python3 verify_new.py q1/certs/new_schemes.json
"""
import collections
import glob
import json
import os
import sys

from common import HERE, boot, census_schemes

boot()

from notation import canon, stats


def load_jsonl(pattern):
    rows = []
    for fn in sorted(glob.glob(pattern)):
        for line in open(fn):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def main():
    known = {canon(c["scheme"]) for c in
             json.load(open("certs/new_schemes.json"))}
    census = {canon(s) for s in census_schemes()}
    already = census | known

    novel = {}
    for pattern in (
        os.path.join(HERE, "thick_out", "*_novel.jsonl"),
        os.path.join(HERE, "walk_out", "*_novel.jsonl"),
        os.path.join(HERE, "hole_out", "*_novel.jsonl"),
        os.path.join(HERE, "hot_out", "*_novel.jsonl"),
        os.path.join(HERE, "m2_out", "*_novel.jsonl"),
        os.path.join(HERE, "even_out", "*.jsonl"),
    ):
        for r in load_jsonl(pattern):
            if r.get("kind") not in ("NOVEL", "NEW", "HIT"):
                continue
            if "scheme" not in r or "triangles" not in r:
                continue
            s = canon(r["scheme"])
            if s in already:
                continue
            novel.setdefault(s, r)

    os.makedirs(os.path.join(HERE, "certs"), exist_ok=True)
    cand_path = None
    candidates = sorted(novel)
    if candidates:
        cand_path = os.path.join(HERE, "certs", "new_schemes.json")
        json.dump([{"scheme": s,
                    "triangles": novel[s]["triangles"],
                    "heights": novel[s]["heights"],
                    "signs": novel[s]["signs"],
                    "source": novel[s].get("source", "q1")}
                   for s in candidates],
                  open(cand_path, "w"), indent=1)

    thick = [r for r in load_jsonl(os.path.join(HERE, "thick_out", "h*.jsonl"))
             if r.get("kind") == "tri_done"]
    thick = [r for r in thick if not r.get("_skip")]
    by_cert = {}
    for r in thick:
        by_cert.setdefault((r["cert"], r.get("radius", 1)), r)
    thick = list(by_cert.values())
    complete = [r for r in thick if r.get("complete")]

    even_summ = [r for r in load_jsonl(os.path.join(HERE, "even_out", "*.jsonl"))
                 if r.get("kind") == "summary"]
    even_hits = [r for r in load_jsonl(os.path.join(HERE, "even_out", "*.jsonl"))
                 if r.get("kind") == "HIT"]
    walk = [r for r in load_jsonl(os.path.join(HERE, "walk_out", "k*.jsonl"))
            if r.get("kind") == "tri_done"]
    m2 = [r for r in load_jsonl(os.path.join(HERE, "m2_out", "m*.jsonl"))
          if r.get("kind") == "seed_done"]
    hot = [r for r in load_jsonl(os.path.join(HERE, "hot_out", "t*.jsonl"))
           if r.get("kind") == "seed_done"]
    hole = [r for r in load_jsonl(os.path.join(HERE, "hole_out", "*.jsonl"))
            if r.get("kind") == "seed_done"]

    summary = {
        "search": "q1: leftover whole-stratum thicken (radius 1, rank <= 20), "
                  "even-split walk on the (19,3) row, perturbations of the "
                  "two published deep-nest triangulations, radius-4 balls "
                  "around every 20-oval certificate, and targeted balls at "
                  "the four hole-map targets",
        "thicken": {
            "triangulations_logged": len(thick),
            "triangulations_complete": len(complete),
            "ranks_completed": {str(k): v for k, v in sorted(
                collections.Counter(r["rank"] for r in complete).items())},
            "total_evaluations": sum(r.get("evals", 0) for r in thick),
            "novel_on_thicken": sorted({s for r in thick
                                        for s in r.get("novel", [])
                                        if canon(s) not in already}),
        },
        "even_walk": {
            "summaries": even_summ,
            "hits": [{"scheme": r["scheme"],
                      "regular": r.get("regular", False)}
                     for r in even_hits],
        },
        "nest_walk": {
            "triangulations_swept": len(walk),
            "hits": [r["hits"] for r in walk if r.get("hits")],
            "novel": sorted({s for r in walk for s in r.get("novel", [])
                             if canon(s) not in already}),
        },
        "m2_balls": {
            "seeds_done": len(m2),
            "complete": sum(1 for r in m2 if r.get("complete")),
            "evals": sum(r.get("evals", 0) for r in m2),
            "novel": sorted({s for r in m2 for s in r.get("novel", [])
                             if canon(s) not in already}),
        },
        "hot_holes": {
            "seeds_done": len(hot),
            "novel": sorted({s for r in hot for s in r.get("novel", [])
                             if canon(s) not in already}),
        },
        "hole_balls": {
            "seeds_done": len(hole),
            "novel": sorted({s for r in hole for s in r.get("novel", [])
                             if canon(s) not in already}),
        },
        "NEW_candidates": candidates,
        "NEW_candidates_ovals": {s: stats(s)[0] for s in candidates},
        "candidate_cert_file": cand_path,
    }
    out = os.path.join(HERE, "certs", "q1_summary.json")
    json.dump(summary, open(out, "w"), indent=1)
    print(json.dumps({k: summary[k] for k in summary
                      if k != "even_walk"}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
