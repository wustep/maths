#!/usr/bin/env python3
"""Independently recompute deck SHA-256s using nauty labelg, not deckrecon.

Each input line is:
    full_sha set_sha graph6
or the longer emit format:
    full_sha set_sha dmin dmax nred graph6

labelg canonically labels every vertex-deleted card. The sorted (resp. uniqued)
graph6 strings are SHA-256 hashed. Exit status 0 iff every line matches.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

LABELG = Path(__file__).resolve().parent / "bin" / "labelg"
if not LABELG.exists():
    for cand in ("/tmp/nauty2_9_1/labelg", "/usr/bin/labelg"):
        if Path(cand).exists():
            LABELG = Path(cand)
            break


def graph6_n(g6: str) -> int:
    b = g6[0]
    if b == "~":
        raise ValueError("large graph6 not supported")
    return ord(b) - 63


def graph6_edges(g6: str) -> list[tuple[int, int]]:
    n = graph6_n(g6)
    bits = []
    for ch in g6[1:]:
        v = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return edges


def write_graph6(n: int, edges: list[tuple[int, int]]) -> str:
    bits = []
    eset = set(edges)
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in eset or (j, i) in eset else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(63 + n)]
    for t in range(0, len(bits), 6):
        v = 0
        for b in bits[t : t + 6]:
            v = (v << 1) | b
        out.append(chr(63 + v))
    return "".join(out)


def delete_vertex(g6: str, v: int) -> str:
    n = graph6_n(g6)
    edges = graph6_edges(g6)
    new_e = []
    for a, b in edges:
        if a == v or b == v:
            continue
        na = a if a < v else a - 1
        nb = b if b < v else b - 1
        if na > nb:
            na, nb = nb, na
        new_e.append((na, nb))
    return write_graph6(n - 1, new_e)


def labelg_many(g6_list: list[str]) -> list[str]:
    proc = subprocess.run(
        [str(LABELG), "-q"],
        input="".join(s + "\n" for s in g6_list),
        text=True,
        capture_output=True,
        check=True,
    )
    out = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip() and ln[0] != ">"]
    if len(out) != len(g6_list):
        raise RuntimeError(f"labelg returned {len(out)} lines for {len(g6_list)} cards")
    return out


def deck_hashes(g6: str) -> tuple[str, str]:
    n = graph6_n(g6)
    cards = [delete_vertex(g6, v) for v in range(n)]
    canons = labelg_many(cards)
    canons_sorted = sorted(canons)
    full = hashlib.sha256(("\n".join(canons_sorted) + "\n").encode()).hexdigest()
    uniq = []
    for c in canons_sorted:
        if not uniq or uniq[-1] != c:
            uniq.append(c)
    red = hashlib.sha256(("\n".join(uniq) + "\n").encode()).hexdigest()
    return full, red


def parse_line(line: str) -> tuple[str, str, str] | None:
    line = line.strip()
    if not line or line[0] == "#" or line.startswith("read="):
        return None
    parts = line.split()
    if len(parts) < 3:
        return None
    # last field is graph6 (starts with a graph6 header byte)
    g6 = parts[-1]
    return parts[0], parts[1], g6


def main(argv: list[str]) -> int:
    paths = argv[1:] or ["-"]
    bad = 0
    seen = 0
    for path in paths:
        fh = sys.stdin if path == "-" else open(path)
        with fh:
            for ln, line in enumerate(fh, 1):
                parsed = parse_line(line)
                if parsed is None:
                    continue
                full, red, g6 = parsed
                got_full, got_red = deck_hashes(g6)
                seen += 1
                if got_full != full or got_red != red:
                    bad += 1
                    print(f"MISMATCH {path}:{ln} g6={g6}", file=sys.stderr)
                    print(f"  claimed full={full}", file=sys.stderr)
                    print(f"  labelg  full={got_full}", file=sys.stderr)
                    print(f"  claimed set ={red}", file=sys.stderr)
                    print(f"  labelg  set ={got_red}", file=sys.stderr)
    print(f"checked={seen} mismatches={bad} labelg={LABELG}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
