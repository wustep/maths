#!/usr/bin/env python3
"""Verify an independent set in C7^{⊠5}.

A line is either five digits (e.g. 02020) or five 0–6 integers.
Distinct vertices must have circular distance > 1 in some coordinate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from c7_common import DIM, N, adjacent, encode, format_word


def load_set(path: Path) -> list[int]:
    words: list[int] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "," in line:
            parts = [p.strip() for p in line.split(",") if p.strip()]
            for p in parts:
                if len(p) == DIM and p.isdigit():
                    words.append(encode(int(ch) for ch in p))
                else:
                    raise ValueError(f"bad token {p!r} in {path}")
            continue
        toks = line.split()
        if len(toks) == 1 and len(toks[0]) == DIM and toks[0].isdigit():
            words.append(encode(int(ch) for ch in toks[0]))
        elif len(toks) == DIM and all(t.isdigit() for t in toks):
            words.append(encode(int(t) for t in toks))
        else:
            raise ValueError(f"bad line {line!r} in {path}")
    return words


def first_conflict(words: list[int]) -> tuple[int, int] | None:
    n = len(words)
    for i in range(n):
        for j in range(i + 1, n):
            if adjacent(words[i], words[j]):
                return words[i], words[j]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--min-size", type=int, default=0)
    args = ap.parse_args()
    words = load_set(args.path)
    uniq = set(words)
    print(f"file={args.path}")
    print(f"size={len(words)} unique={len(uniq)}")
    if len(words) != len(uniq):
        print("FAIL: duplicate vertices")
        return 1
    for w in words:
        if not (0 <= w < N**DIM):
            print(f"FAIL: out of range {w}")
            return 1
    conflict = first_conflict(words)
    if conflict is not None:
        a, b = conflict
        print(f"FAIL: adjacent pair {format_word(a)} {format_word(b)}")
        return 1
    if args.min_size and len(words) < args.min_size:
        print(f"FAIL: size {len(words)} < {args.min_size}")
        return 1
    print("OK: independent in C7^{box5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
