#!/usr/bin/env python3
"""Write nest certificates from q4 jsonl summaries.

Does not write new_schemes.json. A collection-space HIT is not a
T-curve until verify_new.py accepts a stored certificate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = HERE / "certs"


def last_summary(path: Path):
    last = None
    schemes = []
    hits = 0
    news = 0
    if not path.exists():
        return None, [], 0, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("kind") == "summary":
            last = rec
        if rec.get("kind") in ("scheme", "NEW", "HIT", "pn193"):
            if rec.get("scheme"):
                schemes.append(rec["scheme"])
        if rec.get("kind") == "HIT":
            hits += 1
        if rec.get("kind") == "NEW":
            news += 1
    return last, sorted(set(schemes)), hits, news


def write(name, payload):
    CERT.mkdir(exist_ok=True)
    dest = CERT / name
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", dest.relative_to(HERE.parent))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("ladder3_193", "all"):
        summ, schemes, hits, news = last_summary(
            HERE / "dn_out" / "ladder3_193.jsonl")
        if summ:
            write("ladder3_193.json", {
                "what": ("Three-split moves around the five published "
                         "(19,3) M-collections. Complete only if every "
                         "seed finished."),
                "which": "193",
                "evals": summ.get("evals"),
                "distinct_schemes": summ.get("distinct"),
                "new": summ.get("new", news),
                "hits_on_open_nests": summ.get("hits", hits),
                "best_score": summ.get("best_score"),
                "best_scheme": summ.get("best_scheme"),
                "seeds": summ.get("seeds"),
                "finished_seeds": summ.get("finished_seeds"),
                "complete": bool(summ.get("complete")),
                "seconds": summ.get("seconds"),
                "schemes": schemes,
                "open_nests_in_scope": hits > 0,
            })
    if which in ("ladder3_depth3", "all"):
        summ, schemes, hits, news = last_summary(
            HERE / "dn_out" / "ladder3_depth3.jsonl")
        if summ:
            write("ladder3_depth3.json", {
                "what": ("Three-split moves around published depth-3 "
                         "M-collections. Complete only if every seed "
                         "finished."),
                "which": "depth3",
                "evals": summ.get("evals"),
                "distinct_schemes": summ.get("distinct"),
                "new": summ.get("new", news),
                "hits_on_open_nests": summ.get("hits", hits),
                "best_score": summ.get("best_score"),
                "best_scheme": summ.get("best_scheme"),
                "seeds": summ.get("seeds"),
                "finished_seeds": summ.get("finished_seeds"),
                "complete": bool(summ.get("complete")),
                "seconds": summ.get("seconds"),
                "schemes": schemes,
                "open_nests_in_scope": hits > 0,
            })
    if which in ("even_bfs", "all"):
        summ, schemes, hits, news = last_summary(
            HERE / "even_out" / "bfs.jsonl")
        if summ:
            write("even_bfs.json", {
                "what": ("Pinned even-split BFS from the published "
                         "(19,3) collections. Complete only if the "
                         "queue empties."),
                "pin_odd": True,
                "evals": summ.get("evals"),
                "limit": summ.get("limit"),
                "queue_left": summ.get("queue_left"),
                "distinct_schemes": summ.get("distinct"),
                "new": summ.get("new", news),
                "hits": summ.get("hits", hits),
                "best_score": summ.get("best_score"),
                "best_scheme": summ.get("best_scheme"),
                "complete": summ.get("queue_left") == 0,
                "schemes": schemes,
                "open_nests_in_scope": hits > 0,
            })
    if which in ("odd_skel5", "all"):
        summ, schemes, hits, news = last_summary(
            HERE / "even_out" / "odd_skel5.jsonl")
        if summ:
            write("odd_skel5.json", {
                "what": ("Compatible odd Harnack-split collections "
                         "through size 5. Complete only if the size-5 "
                         "enumeration finished."),
                "maxsize": summ.get("maxsize", 5),
                "evals": summ.get("evals"),
                "pn193_evals": summ.get("pn193"),
                "distinct_schemes": summ.get("distinct"),
                "hits_on_open_nests": summ.get("hits", hits),
                "complete": bool(summ.get("complete")),
                "seconds": summ.get("seconds"),
                "schemes": schemes,
                "open_nests_in_scope": hits > 0,
            })


if __name__ == "__main__":
    main()
