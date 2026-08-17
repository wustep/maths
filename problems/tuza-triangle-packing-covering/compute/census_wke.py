#!/usr/bin/env python3
"""WKE census on n-vertex graphs via nauty geng (unlabelled) or labelled scan.

Replays Gupta Lemma 4.5 at n=7 and produces the n=8 degree-profile lemma.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from wke import (
    degrees_from_mask,
    edges_to_mask,
    is_connected_mask,
    is_wke_mask,
    parse_g6,
)

HERE = Path(__file__).resolve().parent
GENG = Path(__file__).resolve().parent / "bin" / "geng"
OUT = HERE / "certs"


def require(cond, msg):
    if not cond:
        raise SystemExit(f"FAIL {msg}")
    print(f"PASS {msg}", flush=True)


def geng_graphs(n, connected=False):
    args = [str(GENG), "-q"]
    if connected:
        args.append("-c")
    args.append(str(n))
    proc = subprocess.run(args, capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        parsed = parse_g6(line)
        if parsed:
            yield parsed[0], parsed[1], line.strip()


def profile_graph(n, edges):
    gmask = edges_to_mask(n, edges)
    wke = is_wke_mask(n, gmask)
    conn = is_connected_mask(n, gmask)
    deg = degrees_from_mask(n, gmask)
    n_ge4 = sum(1 for d in deg if d >= 4)
    n_ge5 = sum(1 for d in deg if d >= 5)
    n_ge6 = sum(1 for d in deg if d >= 6)
    return {
        "wke": wke,
        "connected": conn,
        "deg": deg,
        "delta": max(deg) if deg else 0,
        "n_ge4": n_ge4,
        "n_ge5": n_ge5,
        "n_ge6": n_ge6,
        "n_edges": len(edges),
    }


def census_unlabelled(n):
    rows = []
    for nv, edges, g6 in geng_graphs(n, connected=False):
        info = profile_graph(nv, edges)
        info["g6"] = g6
        rows.append(info)
    return rows


def summarise(rows, n):
    total = len(rows)
    connected = [r for r in rows if r["connected"]]
    nonwke = [r for r in rows if not r["wke"]]
    conn_nonwke = [r for r in rows if r["connected"] and not r["wke"]]
    disc_nonwke = [r for r in rows if (not r["connected"]) and not r["wke"]]

    def min_stat(lst, key):
        return min((r[key] for r in lst), default=None)

    summary = {
        "n": n,
        "unlabelled_total": total,
        "unlabelled_connected": len(connected),
        "unlabelled_nonwke": len(nonwke),
        "unlabelled_connected_nonwke": len(conn_nonwke),
        "unlabelled_disconnected_nonwke": len(disc_nonwke),
        "conn_nonwke_min_n_ge4": min_stat(conn_nonwke, "n_ge4"),
        "conn_nonwke_min_n_ge5": min_stat(conn_nonwke, "n_ge5"),
        "conn_nonwke_min_n_ge6": min_stat(conn_nonwke, "n_ge6"),
        "conn_nonwke_min_delta": min_stat(conn_nonwke, "delta"),
        "n_ge4_hist": dict(Counter(r["n_ge4"] for r in conn_nonwke)),
        "n_ge5_hist": dict(Counter(r["n_ge5"] for r in conn_nonwke)),
        "n_ge6_hist": dict(Counter(r["n_ge6"] for r in conn_nonwke)),
        "delta_hist": dict(Counter(r["delta"] for r in conn_nonwke)),
        # witnesses of the weakest degree profiles
        "min_delta_examples": [
            {"g6": r["g6"], "deg": r["deg"], "n_ge4": r["n_ge4"], "n_ge5": r["n_ge5"]}
            for r in conn_nonwke
            if r["delta"] == min_stat(conn_nonwke, "delta")
        ][:8],
        "few_ge5_examples": [
            {"g6": r["g6"], "deg": r["deg"], "n_ge4": r["n_ge4"], "n_ge5": r["n_ge5"]}
            for r in conn_nonwke
            if r["n_ge5"] == min_stat(conn_nonwke, "n_ge5")
        ][:8],
    }
    return summary, conn_nonwke


def labelled_n7():
    """Replay Gupta's labelled 2^21 scan."""
    n = 7
    n_edges = n * (n - 1) // 2
    nonwke = 0
    conn_nonwke = 0
    few = 0
    exactly3 = 0
    disc_nonwke_few = 0
    for gmask in range(1 << n_edges):
        if is_wke_mask(n, gmask):
            continue
        nonwke += 1
        deg = degrees_from_mask(n, gmask)
        n_ge4 = sum(1 for d in deg if d >= 4)
        conn = is_connected_mask(n, gmask)
        if conn:
            conn_nonwke += 1
            if n_ge4 < 3:
                few += 1
            if n_ge4 == 3:
                exactly3 += 1
        else:
            if n_ge4 < 3:
                disc_nonwke_few += 1
    return {
        "labelled_total": 1 << n_edges,
        "labelled_nonwke": nonwke,
        "labelled_connected_nonwke": conn_nonwke,
        "labelled_connected_nonwke_n_ge4_lt3": few,
        "labelled_connected_nonwke_n_ge4_eq3": exactly3,
        "labelled_disconnected_nonwke_n_ge4_lt3": disc_nonwke_few,
    }


def main():
    OUT.mkdir(exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    do_labelled = "--labelled" in sys.argv
    ns = [int(x) for x in args] or [5, 6, 7, 8]
    all_summ = {}
    for n in ns:
        print(f"=== unlabelled n={n} ===", flush=True)
        rows = census_unlabelled(n)
        summary, _ = summarise(rows, n)
        all_summ[str(n)] = summary
        print(json.dumps({k: summary[k] for k in summary if "examples" not in k}, indent=2), flush=True)
        if n == 7:
            # Gupta: every connected non-WKE 7-vertex graph has >=3 verts of deg>=4
            require(summary["conn_nonwke_min_n_ge4"] >= 3, "n=7 connected non-WKE => >=3 verts deg>=4")
        if n == 8:
            print(
                "n=8 connected non-WKE: min n_ge4="
                f"{summary['conn_nonwke_min_n_ge4']} min n_ge5="
                f"{summary['conn_nonwke_min_n_ge5']} min delta="
                f"{summary['conn_nonwke_min_delta']}",
                flush=True,
            )
    path = OUT / "wke_unlabelled.json"
    if path.exists():
        prev = json.loads(path.read_text())
        prev.update(all_summ)
        all_summ = prev
    path.write_text(json.dumps(all_summ, indent=2) + "\n")
    print(f"wrote {path}")

    if 7 in ns and do_labelled:
        print("=== labelled n=7 replay ===", flush=True)
        lab = labelled_n7()
        print(json.dumps(lab, indent=2), flush=True)
        require(lab["labelled_nonwke"] == 167871, "Gupta labelled non-WKE 167871")
        require(lab["labelled_connected_nonwke"] == 166793, "Gupta labelled connected non-WKE 166793")
        require(lab["labelled_connected_nonwke_n_ge4_lt3"] == 0, "Gupta: no connected non-WKE with <3 deg>=4")
        require(lab["labelled_connected_nonwke_n_ge4_eq3"] == 4620, "Gupta: 4620 attain exactly 3")
        (OUT / "wke_labelled_n7.json").write_text(json.dumps(lab, indent=2) + "\n")


if __name__ == "__main__":
    main()
