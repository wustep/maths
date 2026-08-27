#!/usr/bin/env python3
"""Aggregate every q2 search log into certs/q2_summary.json.

Anything outside census+17 is written to certs/new_schemes.json in the
format verify_new.py consumes.  A stranger then runs

    python3 verify_new.py q2/certs/new_schemes.json
"""
import collections
import glob
import json
import os

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
        os.path.join(HERE, "even_out", "*.jsonl"),
        os.path.join(HERE, "dn_out", "*.jsonl"),
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
                    "source": novel[s].get("source", "q2")}
                   for s in candidates],
                  open(cand_path, "w"), indent=1)

    thick = [r for r in load_jsonl(os.path.join(HERE, "thick_out", "h*.jsonl"))
             if r.get("kind") == "tri_done" and not r.get("_skip")]
    by_cert = {}
    for r in thick:
        by_cert.setdefault((r["cert"], r.get("radius", 1)), r)
    thick = list(by_cert.values())
    complete = [r for r in thick if r.get("complete")]

    even_rows = load_jsonl(os.path.join(HERE, "even_out", "*.jsonl"))
    even_summ = [r for r in even_rows if r.get("kind") == "summary"]
    even_hits = [r for r in even_rows if r.get("kind") == "HIT"]
    dn_rows = load_jsonl(os.path.join(HERE, "dn_out", "*.jsonl"))
    dn_summ = [r for r in dn_rows if r.get("kind") == "summary"]
    dn_new = [r for r in dn_rows if r.get("kind") in ("NEW", "HIT")]

    summary = {
        "search": "q2: radius-1 thicken of census triangulations of "
                  "twist-rank 21-26, three-split ladder on the (19,3) "
                  "row, odd skeletons of size 4, and a longer pinned "
                  "even-split BFS",
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
        "dn_sweep": {
            "summaries": dn_summ,
            "new_or_hit": [{"kind": r.get("kind"), "scheme": r.get("scheme")}
                           for r in dn_new],
        },
        "NEW_candidates": candidates,
        "NEW_candidates_ovals": {s: stats(s)[0] for s in candidates},
        "candidate_cert_file": cand_path,
    }
    out = os.path.join(HERE, "certs", "q2_summary.json")
    json.dump(summary, open(out, "w"), indent=1)
    print(json.dumps({k: summary[k] for k in summary
                      if k != "even_walk"}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
