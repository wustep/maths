"""Snapshot leftover thicken certificates from q3/thick_out/*.jsonl.

A triangulation is complete only when evals == 46 * 2^rank.
Incomplete ranks stay residue. Never writes new_schemes.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "thick_out"
CERT_DIR = HERE / "certs"
SPAN = HERE.parent / "span_tasks.json"


def load_span():
    return json.loads(SPAN.read_text())


def expected_evals(rank: int) -> int:
    return 46 * (1 << rank)


def collect_rows():
    rows = []
    for path in sorted(OUT_DIR.glob("*.jsonl")):
        if path.name.endswith("_novel.jsonl"):
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("kind") == "tri_done":
                rows.append(rec)
    return rows


def merge_rows(recs, exp):
    """A leftover triangulation is complete only if evals == 46 * 2^rank.

    Unsharded rows (nshards missing or 1) win when they meet that count.
    Sharded rows complete only when every shard is present and the
    summed evaluation count equals the same expected value.
    """
    unsharded = [r for r in recs if r.get("nshards", 1) == 1]
    for rec in reversed(unsharded):
        ok = bool(rec.get("complete")) and rec.get("evals") == exp
        if ok:
            return {
                "cert": rec["cert"],
                "rank": rec["rank"],
                "evals": rec["evals"],
                "expected": exp,
                "distinct_schemes": rec.get("distinct_schemes"),
                "complete": True,
                "novel": rec.get("novel") or [],
                "seconds": rec.get("seconds"),
            }
    sharded = [r for r in recs if r.get("nshards", 1) > 1]
    if not sharded:
        if unsharded:
            rec = unsharded[-1]
            return {
                "cert": rec["cert"],
                "rank": rec["rank"],
                "evals": rec.get("evals", 0),
                "expected": exp,
                "distinct_schemes": rec.get("distinct_schemes"),
                "complete": False,
                "novel": rec.get("novel") or [],
                "seconds": rec.get("seconds"),
            }
        return None
    nsh = sharded[-1]["nshards"]
    by_shard = {}
    for rec in sharded:
        if rec.get("nshards") != nsh:
            continue
        by_shard[rec.get("shard")] = rec
    if set(by_shard) != set(range(nsh)):
        return None
    evals = sum(r.get("evals", 0) for r in by_shard.values())
    ok = all(r.get("complete") for r in by_shard.values()) and evals == exp
    novel = []
    for r in by_shard.values():
        novel.extend(r.get("novel") or [])
    return {
        "cert": sharded[-1]["cert"],
        "rank": sharded[-1]["rank"],
        "evals": evals,
        "expected": exp,
        "distinct_schemes": sum(r.get("distinct_schemes") or 0
                                for r in by_shard.values()),
        "complete": ok,
        "novel": novel,
        "seconds": sum(r.get("seconds") or 0 for r in by_shard.values()),
        "nshards": nsh,
    }


def main() -> None:
    min_rank = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    max_rank = int(sys.argv[2]) if len(sys.argv) > 2 else 26
    span = [t for t in load_span() if min_rank <= t["rank"] <= max_rank]
    by_cert = {t["cert"]: t for t in span}
    grouped = {}
    for rec in collect_rows():
        cert = rec["cert"]
        if cert not in by_cert:
            continue
        grouped.setdefault(cert, []).append(rec)
    done = {}
    for cert, recs in grouped.items():
        exp = expected_evals(by_cert[cert]["rank"])
        merged = merge_rows(recs, exp)
        if merged is not None:
            done[cert] = merged
    missing = [t["cert"] for t in span if t["cert"] not in done]
    incomplete = [c for c, r in done.items() if not r["complete"]]
    novel = [n for r in done.values() for n in r["novel"]]
    payload = {
        "what": (
            f"Radius-1 thicken of leftover census triangulations of "
            f"twist-rank {min_rank}"
            + ("" if min_rank == max_rank else f"–{max_rank}")
            + ". Complete only when every task has evals == 46 * 2^rank."
        ),
        "kind": "leftover_thicken_r1",
        "radius": 1,
        "min_rank": min_rank,
        "max_rank": max_rank,
        "n_tasks": len(span),
        "n_complete": sum(1 for r in done.values() if r["complete"]),
        "n_incomplete": len(incomplete),
        "n_missing": len(missing),
        "complete": len(missing) == 0 and len(incomplete) == 0,
        "expected_evals": sum(expected_evals(t["rank"]) for t in span),
        "evals": sum(r["evals"] for r in done.values()),
        "novel": novel,
        "missing": missing,
        "incomplete": incomplete,
        "tasks": [done[t["cert"]] for t in span if t["cert"] in done],
    }
    if payload["complete"] and min_rank == max_rank:
        name = f"thick_r1_rank_{min_rank}.json"
    elif payload["complete"]:
        name = f"thick_r1_rank_{min_rank}_{max_rank}.json"
    else:
        name = f"thick_r1_rank_{min_rank}_{max_rank}_prefix.json"
    CERT_DIR.mkdir(exist_ok=True)
    dest = CERT_DIR / name
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "wrote": str(dest.relative_to(HERE.parent)),
        "n_complete": payload["n_complete"],
        "n_tasks": payload["n_tasks"],
        "complete": payload["complete"],
        "novel": novel,
    }))


if __name__ == "__main__":
    main()
