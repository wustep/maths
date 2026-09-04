#!/usr/bin/env python3
"""Drive the C enumerator for one fixed-odd even-split component."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import even_walk as ew


def ids_of(seed, sp):
    for name, ids in ew.seed_collections(sp):
        if name == seed:
            return ids
    key = {x.key: i for i, x in enumerate(sp)}
    recs = json.load(open("certs/mcert_collections.json"))
    rec = recs.get(seed)
    if rec is None:
        # accept the paper-style name without spaces
        for claimed, r in recs.items():
            if claimed.replace(" ", "") == seed.replace(" ", ""):
                rec = r
                break
    if rec is None:
        return None
    ids = []
    for p in rec["collection"]:
        t = tuple(tuple(v) for v in p)
        k = t if t[0] < t[-1] else t[::-1]
        if k not in key:
            return None
        ids.append(key[k])
    return sorted(set(ids))


def component_of(seed):
    sp = dn.splits()
    adj = dn.compat_matrix()
    emask = ew.even_mask(sp)
    seed_ids = ids_of(seed, sp)
    if seed_ids is None:
        raise SystemExit(f"missing seed {seed}")
    odd = [i for i in seed_ids if not sp[i].even]
    candidates = emask
    for i in odd:
        candidates &= adj[i]

    sys.setrecursionlimit(10000)

    from functools import lru_cache

    @lru_cache(maxsize=None)
    def count(mask):
        if not mask:
            return 1
        bit = mask & -mask
        v = bit.bit_length() - 1
        rest = mask ^ bit
        return count(rest) + count(rest & adj[v])

    n = count(candidates)
    return odd, candidates.bit_count(), n


def decode_log(path, sp):
    from odd5_collect import decode, rows
    schemes = {}
    summary = None
    for row in rows(path):
        if row.get("kind") == "summary":
            summary = row
            continue
        if row.get("kind") != "WITNESS":
            continue
        scheme = decode(row, sp)
        schemes[scheme] = row["collection"]
    return summary, schemes


def main():
    seed = sys.argv[1] if len(sys.argv) > 1 else "<17v1<2v1<1>>>"
    odd, n_even, expected = component_of(seed)
    import re
    tag = re.sub(r"[^A-Za-z0-9]+", "_", seed).strip("_")
    task = HERE / "work" / "odd5.task"
    if not task.exists():
        subprocess.check_call([sys.executable, str(HERE / "odd5_export.py")])
    bin_path = HERE / "evenc"
    if not bin_path.exists():
        subprocess.check_call([
            "gcc", "-O3", "-std=gnu11", "-Wall", "-Wextra",
            "-Wno-unused-function", "-o", str(bin_path), str(HERE / "evenc.c"),
        ])
    out = HERE / "even_out" / f"evenc_{tag}.jsonl"
    odd_arg = ",".join(str(i) for i in odd)
    print(f"seed={seed} odd={odd} even_candidates={n_even} expected={expected}",
          flush=True)
    subprocess.check_call([
        str(bin_path), str(task), str(out), odd_arg, str(expected),
    ])
    sp = dn.splits()
    summary, schemes = decode_log(out, sp)
    known = ew.known_schemes()
    novel = sorted(s for s in schemes if s not in known)
    hits = sorted(s for s in schemes if s in ew.OPEN)
    cert = {
        "what": ("All compatible even-split subsets with the odd splits "
                 "of a published (19,3) collection held fixed."),
        "seed": seed,
        "odd_splits": odd,
        "compatible_even_splits": n_even,
        "evals": summary["evals"] if summary else None,
        "expected": expected,
        "distinct": len(schemes),
        "new": len(novel),
        "hits": len(hits),
        "complete": bool(summary and summary.get("complete")),
        "seconds": summary.get("seconds") if summary else None,
        "schemes": sorted(schemes),
        "novel": novel,
        "hits_on_open_nests": hits,
    }
    dest = HERE / "certs" / f"even_component_{tag}.json"
    dest.write_text(json.dumps(cert, indent=2) + "\n")
    print(json.dumps(cert, indent=2))
    print("wrote", dest.relative_to(ROOT))
    if not cert["complete"]:
        raise SystemExit("even component incomplete")


if __name__ == "__main__":
    main()
