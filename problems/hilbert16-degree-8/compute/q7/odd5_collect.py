#!/usr/bin/env python3
"""Independently decode C witnesses and certify the odd size-5 sweep."""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import even_walk as ew
from notation import canon, parse, stats

MASK = (1 << 64) - 1
TARGETS = {"<4 u 1<2 u 1<14>>>", "<14 u 1<2 u 1<4>>>"}
EXPECTED = 37_632_123


def mix64(x):
    x &= MASK
    x ^= x >> 33
    x = (x * 0xFF51AFD7ED558CCD) & MASK
    x ^= x >> 33
    x = (x * 0xC4CEB9FE1A85EC53) & MASK
    x ^= x >> 33
    return x & MASK


def fold(children):
    children = sorted(children)
    a, b = 0x243F6A8885A308D3, 0x13198A2E03707344
    for ca, cb in children:
        a = mix64(a ^ mix64(ca + 0x9E3779B97F4A7C15))
        b = mix64(((b * 0x100000001B3) & MASK) ^ cb)
    a = mix64(a + len(children))
    b = mix64(b + len(children) * 0x9E3779B97F4A7C15)
    return a, b


def scheme_fp(scheme):
    forest, has_j = parse(scheme)
    if has_j:
        raise ValueError("odd5 sweep is degree 8 and cannot contain J")

    def enc(oval):
        return fold([enc(child) for child in oval])

    a, b = fold([enc(oval) for oval in forest])
    return f"{a:016x}{b:016x}"


def rows(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def decode(row, sp):
    ids = row["collection"]
    nc, scheme = dn.evaluate([sp[i] for i in ids])[:2]
    if scheme is None:
        raise AssertionError((row, "Python decoder returned no scheme"))
    if nc != row["ncomp"] or scheme_fp(scheme) != row["fp"]:
        raise AssertionError((row, nc, scheme, scheme_fp(scheme)))
    return canon(scheme)


def validate_one(path):
    sp = dn.splits()
    checked = 0
    schemes = set()
    for row in rows(path):
        if row.get("kind") == "summary":
            continue
        schemes.add(decode(row, sp))
        checked += 1
    print(f"validated {checked} C evaluations against Python: "
          f"{len(schemes)} schemes")


def interval_cover(intervals, end=189):
    intervals = sorted(tuple(x) for x in intervals)
    if not intervals or intervals[0][0] != 0:
        return False
    cur = 0
    for lo, hi in intervals:
        if lo > cur:
            return False
        cur = max(cur, hi)
    return cur >= end


def regular_record(sp, scheme, witnesses):
    for ids in witnesses:
        coll = [sp[i] for i in ids]
        reg = ew.try_regularize(coll, tries=64)
        if reg is None:
            continue
        tris, heights = reg
        return {
            "scheme": scheme,
            "triangles": [[list(v) for v in t] for t in tris],
            "heights": {f"{p[0]},{p[1]}": int(v)
                        for p, v in heights.items()},
            "signs": {f"{p[0]},{p[1]}": int(s)
                      for p, s in dn.signs_of(coll).items()},
            "source": "q7 exhaustive odd size-5 collection sweep",
        }
    return None


def aggregate():
    paths = sorted(glob.glob(str(HERE / "even_out" / "odd5c_*.jsonl")))
    if not paths:
        raise SystemExit("no q7 odd5c logs")
    sp = dn.splits()
    summaries = []
    schemes = set()
    witnesses = {}
    intervals = []
    evals = 0
    seconds = 0.0
    for path in paths:
        summary = None
        for row in rows(path):
            if row.get("kind") == "summary":
                summary = row
                continue
            if row.get("kind") != "WITNESS":
                continue
            scheme = decode(row, sp)
            schemes.add(scheme)
            witnesses.setdefault(scheme, []).append(row["collection"])
        if summary is None:
            raise AssertionError(f"no summary in {path}")
        if not summary["complete"] or summary["bad"] or \
                summary["evals"] != summary["expected"]:
            raise AssertionError((path, summary))
        interval = [summary["lo"], summary["hi"]]
        intervals.append(interval)
        evals += summary["evals"]
        seconds += summary["seconds"]
        summaries.append({"file": Path(path).name, **summary})

    complete = evals == EXPECTED and interval_cover(intervals)
    census = {canon(s.strip()) for s in open("census_schemes.txt") if s.strip()}
    prior = {canon(r["scheme"]) for r in json.load(open("certs/new_schemes.json"))}
    novel = sorted(schemes - census - prior)
    hits = sorted(schemes & TARGETS)
    certs = []
    uncertified = []
    for scheme in novel:
        rec = regular_record(sp, scheme, witnesses.get(scheme, []))
        if rec is None:
            uncertified.append(scheme)
        else:
            certs.append(rec)
    if certs:
        (HERE / "certs" / "new_schemes.json").write_text(
            json.dumps(certs, indent=2) + "\n")

    result = {
        "what": ("All compatible collections of five odd Harnack splits, "
                 "evaluated in C and independently decoded in Python."),
        "odd_splits": 189,
        "size": 5,
        "evals": evals,
        "expected": EXPECTED,
        "distinct_schemes": len(schemes),
        "schemes": sorted(schemes),
        "hits_on_open_nests": hits,
        "novel_vs_census_and_prior_17": novel,
        "regular_certificates_written": len(certs),
        "unregularized_novel_collections": uncertified,
        "complete": bool(complete),
        "intervals_cover_all_first_indices": interval_cover(intervals),
        "cpu_seconds_sum": round(seconds, 3),
        "shards": summaries,
    }
    dest = HERE / "certs" / "odd_skel5.json"
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in result if k != "shards"}, indent=2))
    print("wrote", dest.relative_to(ROOT))
    if not complete:
        raise SystemExit("odd size-5 sweep is incomplete")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--validate-log":
        validate_one(sys.argv[2])
    elif len(sys.argv) == 1:
        aggregate()
    else:
        raise SystemExit("usage: odd5_collect.py [--validate-log LOG]")


if __name__ == "__main__":
    main()
