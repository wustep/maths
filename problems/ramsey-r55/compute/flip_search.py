#!/usr/bin/env python3
"""Single-edge flip neighbourhood of the 656 known (5,5,42)-graphs.

Deleting uv creates an independent 5 iff some 3-set in the common
non-neighbourhood of {u,v} is independent and independent from both.
Adding uv creates a K5 iff N(u)∩N(v) contains a triangle.
"""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

from r55lib import (
    alpha_at_least,
    complement,
    dump_json,
    n_edges,
    omega_at_least,
    parse_graph6,
    to_graph6,
    triangles,
)

ROOT = Path(__file__).resolve().parent
G6_PATH = ROOT / "refs" / "r55_42some.g6"
OUT = ROOT / "certs" / "flip_search.json"


def has_triangle_in_mask(nbr: list[int], mask: int) -> bool:
    m = mask
    while m:
        ubit = m & -m
        u = ubit.bit_length() - 1
        rest = m ^ ubit
        if (nbr[u] & rest).bit_count() >= 2:
            # some two neighbours of u inside rest: check they are adjacent
            r = nbr[u] & rest
            while r:
                vbit = r & -r
                v = vbit.bit_length() - 1
                if nbr[v] & r:
                    return True
                r ^= vbit
        m ^= ubit
    return False


def add_creates_k5(nbr: list[int], u: int, v: int) -> bool:
    common = nbr[u] & nbr[v]
    return has_triangle_in_mask(nbr, common)


def del_creates_ind5(nbr: list[int], u: int, v: int, n: int) -> bool:
    full = (1 << n) - 1
    # vertices adjacent to neither (except u,v themselves)
    common_non = full ^ (nbr[u] | nbr[v] | (1 << u) | (1 << v))
    # independent 3-set in the complement, inside common_non
    c_nbr = [(~nbr[i]) & full & ~(1 << i) for i in range(n)]
    return has_triangle_in_mask(c_nbr, common_non)


def all_graphs():
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    for i, line in enumerate(lines):
        n, nbr = parse_graph6(line)
        yield i, "stored", n, nbr
        yield i, "complement", n, complement(nbr)


def main() -> int:
    t0 = time.time()
    n_surviving = 0
    n_tried = 0
    survivors = []
    per_graph = []
    known = set()
    # fingerprints of known graphs via graph6 in file labeling plus complements
    # (not iso-invariant). Surviving flips are checked for (5,5) and recorded.
    for i, side, n, nbr in all_graphs():
        add_ok = 0
        del_ok = 0
        add_block = 0
        del_block = 0
        for u in range(n):
            for v in range(u + 1, n):
                n_tried += 1
                is_edge = (nbr[u] >> v) & 1
                if is_edge:
                    if del_creates_ind5(nbr, u, v, n):
                        del_block += 1
                    else:
                        del_ok += 1
                        n_surviving += 1
                        # confirm
                        nbr[u] ^= 1 << v
                        nbr[v] ^= 1 << u
                        ok = (not omega_at_least(nbr, 5)) and (not alpha_at_least(nbr, 5))
                        rec = {
                            "src": i,
                            "side": side,
                            "op": "del",
                            "uv": [u, v],
                            "ok_55": ok,
                            "edges": n_edges(nbr),
                            "triangles": triangles(nbr),
                            "g6": to_graph6(nbr),
                        }
                        if ok:
                            survivors.append(rec)
                        nbr[u] ^= 1 << v
                        nbr[v] ^= 1 << u
                        if not ok:
                            # should not happen if the local test is correct
                            print("LOCAL/GLOBAL MISMATCH del", rec, flush=True)
                else:
                    if add_creates_k5(nbr, u, v):
                        add_block += 1
                    else:
                        add_ok += 1
                        n_surviving += 1
                        nbr[u] ^= 1 << v
                        nbr[v] ^= 1 << u
                        ok = (not omega_at_least(nbr, 5)) and (not alpha_at_least(nbr, 5))
                        rec = {
                            "src": i,
                            "side": side,
                            "op": "add",
                            "uv": [u, v],
                            "ok_55": ok,
                            "edges": n_edges(nbr),
                            "triangles": triangles(nbr),
                            "g6": to_graph6(nbr),
                        }
                        if ok:
                            survivors.append(rec)
                        nbr[u] ^= 1 << v
                        nbr[v] ^= 1 << u
                        if not ok:
                            print("LOCAL/GLOBAL MISMATCH add", rec, flush=True)
        per_graph.append(
            {
                "i": i,
                "side": side,
                "add_ok": add_ok,
                "del_ok": del_ok,
                "add_block": add_block,
                "del_block": del_block,
            }
        )
        if ((i + 1) % 20 == 0) and side == "stored":
            print(f"progress stored {i+1}/328 survivors={len(survivors)}", flush=True)

    # How many surviving g6 strings already appear as a stored/complement labeling?
    file_g6 = set()
    lines = [ln.strip() for ln in G6_PATH.read_text().splitlines() if ln.strip()]
    for line in lines:
        file_g6.add(line)
        n, nbr = parse_graph6(line)
        file_g6.add(to_graph6(complement(nbr)))

    new_labelings = [s for s in survivors if s["g6"] not in file_g6]
    summary = {
        "n_graphs": 656,
        "n_tried_flips": n_tried,
        "n_local_surviving": n_surviving,
        "n_confirmed_55": len(survivors),
        "n_new_labelings": len(new_labelings),
        "seconds": round(time.time() - t0, 3),
        "per_graph_head": per_graph[:8],
        "n_per_graph": len(per_graph),
        "add_ok_total": sum(p["add_ok"] for p in per_graph),
        "del_ok_total": sum(p["del_ok"] for p in per_graph),
        "new_labelings_sample": new_labelings[:20],
        "note": (
            "new_labelings are (5,5,42) graphs obtained by one flip, in the "
            "parent's vertex labeling. They may still be isomorphic to one of "
            "the 656. A zero count of local survivors means the 656 are "
            "1-flip isolated among (5,5,42)-graphs."
        ),
    }
    dump_json(str(OUT), summary)
    print(
        f"tried={n_tried} local_ok={n_surviving} confirmed={len(survivors)} "
        f"new_labelings={len(new_labelings)} sec={summary['seconds']}"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
