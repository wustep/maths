#!/usr/bin/env python3
"""Replay published (nu, tau) values for named tight / reference graphs."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from tuza import complete_edges, nu_tau

HERE = Path(__file__).resolve().parent
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)


def Kn(n):
    return complete_edges(range(n)), list(range(n))


def block_path_k4(k):
    """k copies of K4 glued along cut-vertices in a path."""
    # vertices: 0, then each block adds 3 new verts sharing the previous cut
    edges = set()
    # first K4 on 0,1,2,3
    edges |= complete_edges([0, 1, 2, 3])
    last = 3
    nxt = 4
    for _ in range(k - 1):
        a, b, c = nxt, nxt + 1, nxt + 2
        edges |= complete_edges([last, a, b, c])
        last = c
        nxt += 3
    verts = list(range(nxt))
    return edges, verts


def k4_plus_pendant():
    edges = complete_edges([0, 1, 2, 3])
    edges.add((0, 4))
    return edges, list(range(5))


def k5_plus_pendant():
    edges = complete_edges([0, 1, 2, 3, 4])
    edges.add((0, 5))
    return edges, list(range(6))


def two_k4_share_vertex():
    edges = complete_edges([0, 1, 2, 3]) | complete_edges([0, 4, 5, 6])
    return edges, list(range(7))


def main():
    cases = {
        "K3": Kn(3),
        "K4": Kn(4),
        "K5": Kn(5),
        "K6": Kn(6),
        "K7": Kn(7),
        "K8": Kn(8),
        "K4_pendant": k4_plus_pendant(),
        "K5_pendant": k5_plus_pendant(),
        "K4_path_3": block_path_k4(3),
        "two_K4_share_vertex": two_k4_share_vertex(),
    }
    expected = {
        "K3": (1, 1),
        "K4": (1, 2),
        "K5": (2, 4),
        "K6": (4, 6),
        "K7": (7, 9),
        "K8": (8, 12),
        "K4_pendant": (1, 2),
        "K5_pendant": (2, 4),
        "K4_path_3": (3, 6),
        "two_K4_share_vertex": (2, 4),
    }
    results = {}
    for name, (edges, verts) in cases.items():
        nu, tau = nu_tau(edges, verts)
        results[name] = {"nu": nu, "tau": tau, "ratio": None if nu == 0 else tau / nu}
        exp = expected[name]
        ok = (nu, tau) == exp
        status = "PASS" if ok else "FAIL"
        print(f"{status} {name}: ({nu},{tau}) expected {exp}", flush=True)
        if not ok:
            raise SystemExit(1)
    (OUT / "replay_known.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
