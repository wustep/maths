#!/usr/bin/env python3
"""Aggregate every q7 search log into certs/q7_summary.json.

Anything outside census+17 with triangles+heights+signs is written
to certs/new_schemes.json in the format verify_new.py consumes.
"""
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


def load_json(pattern):
    rows = []
    for fn in sorted(glob.glob(pattern)):
        try:
            rows.append(json.load(open(fn)))
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
        os.path.join(HERE, "even_out", "*.jsonl"),
        os.path.join(HERE, "certs", "new_schemes.json"),
    ):
        if pattern.endswith(".json"):
            if os.path.exists(pattern):
                for r in json.load(open(pattern)):
                    if "scheme" in r and "triangles" in r:
                        s = canon(r["scheme"])
                        if s not in already:
                            novel.setdefault(s, r)
            continue
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
                    "source": novel[s].get("source", "q7")}
                   for s in candidates],
                  open(cand_path, "w"), indent=1)

    odd = None
    odd_path = os.path.join(HERE, "certs", "odd_skel5.json")
    if os.path.exists(odd_path):
        odd = json.load(open(odd_path))
    even_certs = load_json(os.path.join(HERE, "certs", "even_component_*.json"))
    even_comp = None
    even_path = os.path.join(HERE, "certs", "even_components.json")
    if os.path.exists(even_path):
        even_comp = json.load(open(even_path))

    summary = {
        "search": "q7: leftover odd size-5 and tractable even components",
        "odd_skel5": {
            "evals": None if odd is None else odd.get("evals"),
            "complete": None if odd is None else odd.get("complete"),
            "hits": None if odd is None else odd.get("hits_on_open_nests"),
            "schemes": None if odd is None else odd.get("schemes"),
        },
        "even_components": even_comp,
        "even_enumerated": even_certs,
        "NEW_candidates": candidates,
        "NEW_candidates_ovals": {s: stats(s)[0] for s in candidates},
        "candidate_cert_file": cand_path,
    }
    out = os.path.join(HERE, "certs", "q7_summary.json")
    json.dump(summary, out if False else open(out, "w"), indent=1)
    print(json.dumps({k: summary[k] for k in
                      ("search", "NEW_candidates", "candidate_cert_file")},
                     indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
