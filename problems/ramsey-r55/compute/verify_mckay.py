#!/usr/bin/env python3
"""Independently verify McKay's 328+(complements) (5,5,42)-graphs."""

from __future__ import annotations

import hashlib
import sys
import time
from collections import Counter
from pathlib import Path

from r55lib import (
    alpha_at_least,
    complement,
    degrees,
    dump_json,
    fingerprint,
    n_edges,
    omega_at_least,
    parse_graph6,
    to_graph6,
    triangles,
)

ROOT = Path(__file__).resolve().parent
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = ROOT / "certs" / "mckay42_verify.json"


def main() -> int:
    t0 = time.time()
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    recs = []
    bad = []
    fps = []
    g6_set = set()
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        if n != 42:
            bad.append({"i": i, "reason": f"n={n}"})
            continue
        degs = degrees(nbr)
        om5 = omega_at_least(nbr, 5)
        al5 = alpha_at_least(nbr, 5)
        rec = {
            "i": i,
            "n": n,
            "edges": n_edges(nbr),
            "min_deg": min(degs),
            "max_deg": max(degs),
            "deg_hist": dict(Counter(degs)),
            "triangles": triangles(nbr),
            "omega_ge5": om5,
            "alpha_ge5": al5,
            "ok": (not om5) and (not al5) and 17 <= min(degs) and max(degs) <= 24,
            "g6_sha256": hashlib.sha256(line.encode()).hexdigest(),
        }
        recs.append(rec)
        if not rec["ok"]:
            bad.append({"i": i, "reason": "not (5,5,42) or illegal degree", "rec": rec})
        fps.append(
            (
                rec["edges"],
                rec["min_deg"],
                rec["max_deg"],
                rec["triangles"],
                tuple(sorted(degs)),
            )
        )
        g6_set.add(line)

    # Complements: rebuild and check they are also (5,5) and not already in the file
    # (McKay's convention: file stores one from each complementary pair).
    comp_in_file = 0
    self_comp = 0
    comp_ok = 0
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        c = complement(nbr)
        cg6 = to_graph6(c)
        if cg6 == line:
            self_comp += 1
        if cg6 in g6_set:
            comp_in_file += 1
        if (not omega_at_least(c, 5)) and (not alpha_at_least(c, 5)):
            comp_ok += 1

    # Distinctness of the 328
    unique_g6 = len(g6_set)
    unique_fp = len(set(fps))

    summary = {
        "source": str(G6_PATH),
        "source_sha256": hashlib.sha256(G6_PATH.read_bytes()).hexdigest(),
        "n_lines": len(lines),
        "n_ok": sum(1 for r in recs if r["ok"]),
        "n_bad": len(bad),
        "unique_g6": unique_g6,
        "unique_fingerprints": unique_fp,
        "complements_also_55": comp_ok,
        "complements_already_in_file": comp_in_file,
        "self_complementary": self_comp,
        "edge_counts": dict(Counter(r["edges"] for r in recs)),
        "regular_counts": dict(
            Counter(r["min_deg"] for r in recs if r["min_deg"] == r["max_deg"])
        ),
        "min_deg_global": min(r["min_deg"] for r in recs) if recs else None,
        "max_deg_global": max(r["max_deg"] for r in recs) if recs else None,
        "seconds": round(time.time() - t0, 3),
        "bad": bad,
        "records": recs,
    }
    dump_json(str(OUT), summary)
    print(
        f"lines={len(lines)} ok={summary['n_ok']} bad={len(bad)} "
        f"unique_g6={unique_g6} unique_fp={unique_fp} "
        f"comp_ok={comp_ok} comp_in_file={comp_in_file} self_comp={self_comp} "
        f"sec={summary['seconds']}"
    )
    print("edge_counts", summary["edge_counts"])
    print("regular_counts", summary["regular_counts"])
    print("wrote", OUT)
    return 0 if not bad and comp_ok == len(lines) else 1


if __name__ == "__main__":
    sys.exit(main())
