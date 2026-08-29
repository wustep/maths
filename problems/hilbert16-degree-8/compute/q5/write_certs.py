#!/usr/bin/env python3
"""Write nest certificates from q5 jsonl summaries.

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
        if rec.get("kind") == "NEW" or rec.get("new_scheme"):
            news += 1
    return last, sorted(set(schemes)), hits, news


def write(name, payload):
    CERT.mkdir(exist_ok=True)
    dest = CERT / name
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", dest.relative_to(HERE.parent))


def odd_paths():
    out = HERE / "even_out"
    if not out.exists():
        return []
    return sorted(out.glob("odd_skel5*.jsonl"))


def merge_odd():
    paths = odd_paths()
    if not paths:
        return
    shards = []
    schemes = set()
    hits = news = evals = pn193 = 0
    seconds = 0.0
    n_odds = None
    covered = []
    all_complete = True
    for path in paths:
        summ, sch, h, n = last_summary(path)
        if not summ:
            continue
        schemes.update(sch)
        hits += h
        news += n
        evals += summ.get("evals", 0)
        pn193 += summ.get("pn193", 0)
        seconds += float(summ.get("seconds") or 0)
        n_odds = summ.get("n_odds", n_odds)
        shard = summ.get("shard")
        complete = bool(summ.get("complete"))
        all_complete = all_complete and complete
        if shard:
            covered.append(tuple(shard))
        shards.append({
            "file": path.name,
            "shard": shard,
            "evals": summ.get("evals"),
            "complete": complete,
            "seconds": summ.get("seconds"),
            "distinct": summ.get("distinct"),
        })
    if not shards:
        return
    covered.sort()
    full = False
    if n_odds and covered:
        cur = 0
        ok = True
        for lo, hi in covered:
            if lo > cur:
                ok = False
                break
            cur = max(cur, hi)
        full = ok and cur >= n_odds
    write("odd_skel5.json", {
        "what": ("Compatible odd Harnack-split collections of size 5. "
                 "Sizes at most 4 finished in q3. Complete only if every "
                 "first-index shard finished and the shards cover all "
                 "odd splits."),
        "maxsize": 5,
        "minsize": 5,
        "n_odds": n_odds,
        "evals": evals,
        "pn193_evals": pn193,
        "distinct_schemes": len(schemes),
        "hits_on_open_nests": hits,
        "complete": bool(all_complete and full),
        "shards_cover_all": full,
        "seconds": round(seconds, 1),
        "shards": shards,
        "schemes": sorted(schemes),
        "open_nests_in_scope": hits > 0,
    })


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("even_bfs", "all"):
        summ, schemes, hits, news = last_summary(
            HERE / "even_out" / "bfs.jsonl")
        if summ:
            write("even_bfs.json", {
                "what": ("Pinned even-split BFS remainder after the q4 "
                         "1,200,000-collection prefix. Complete only if "
                         "the queue empties."),
                "pin_odd": True,
                "evals": summ.get("evals"),
                "limit": summ.get("limit"),
                "skip_eval_until": summ.get("skip_eval_until"),
                "prefix_skipped": summ.get("prefix_skipped"),
                "walked": summ.get("walked"),
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
        merge_odd()


if __name__ == "__main__":
    main()
