#!/usr/bin/env python3
"""Independent checks for a family of order-12 Latin squares.

Checks, all exact:
  - each square is Latin
  - each pair is orthogonal
  - the involution L[r+6][c] == (L[r][c] + 6) % 12
  - optional: first-row identity, first-column of square 0 identity

Does not trust the SAT encoder.  Squares may be given as full 12x12
JSON, or reconstructed from a kissat model of encode_involution_mols.py.
"""

from __future__ import annotations

import argparse
import json
import sys

from encode_involution_mols import model_to_squares, parse_model_lits


N = 12
HALF = 6


def is_latin(L: list[list[int]]) -> tuple[bool, str]:
    if len(L) != N or any(len(row) != N for row in L):
        return False, "not 12x12"
    for r, row in enumerate(L):
        if sorted(row) != list(range(N)):
            return False, f"row {r} is not a permutation"
    for c in range(N):
        col = [L[r][c] for r in range(N)]
        if sorted(col) != list(range(N)):
            return False, f"col {c} is not a permutation"
    return True, "ok"


def is_orthogonal(A: list[list[int]], B: list[list[int]]) -> tuple[bool, str]:
    seen: set[tuple[int, int]] = set()
    for r in range(N):
        for c in range(N):
            pair = (A[r][c], B[r][c])
            if pair in seen:
                return False, f"repeated pair {pair}"
            seen.add(pair)
    if len(seen) != N * N:
        return False, f"only {len(seen)} pairs"
    return True, "ok"


def has_involution(L: list[list[int]]) -> tuple[bool, str]:
    for r in range(HALF):
        for c in range(N):
            got = L[r + HALF][c]
            want = (L[r][c] + HALF) % N
            if got != want:
                return False, f"L[{r+HALF}][{c}]={got} != {want}"
    return True, "ok"


def verify(squares: list[list[list[int]]], normalized: bool = False) -> dict:
    report: dict = {
        "t": len(squares),
        "latin": [],
        "involution": [],
        "orthogonal": [],
        "ok": True,
    }
    for i, L in enumerate(squares):
        ok, msg = is_latin(L)
        report["latin"].append({"k": i, "ok": ok, "msg": msg})
        if not ok:
            report["ok"] = False
        ok, msg = has_involution(L)
        report["involution"].append({"k": i, "ok": ok, "msg": msg})
        if not ok:
            report["ok"] = False
    for i in range(len(squares)):
        for j in range(i + 1, len(squares)):
            ok, msg = is_orthogonal(squares[i], squares[j])
            report["orthogonal"].append({"k": i, "kp": j, "ok": ok, "msg": msg})
            if not ok:
                report["ok"] = False
    if normalized and squares:
        L0 = squares[0]
        if L0[0] != list(range(N)):
            report["ok"] = False
            report["normalize_row0"] = "square 0 first row is not identity"
        if [L0[r][0] for r in range(N)] != list(range(N)):
            report["ok"] = False
            report["normalize_col0"] = "square 0 first col is not identity"
        for i, L in enumerate(squares[1:], start=1):
            if L[0] != list(range(N)):
                report["ok"] = False
                report[f"normalize_row0_{i}"] = f"square {i} first row is not identity"
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="path to JSON list of 12x12 squares")
    ap.add_argument("--model", help="kissat/v-line model")
    ap.add_argument("--t", type=int, help="t, required with --model")
    ap.add_argument("--normalized", action="store_true")
    args = ap.parse_args()
    if args.json:
        with open(args.json) as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            squares = payload["squares"]
        else:
            squares = payload
    elif args.model:
        if args.t is None:
            sys.exit("--t is required with --model")
        squares = model_to_squares(args.t, parse_model_lits(args.model))
    else:
        sys.exit("provide --json or --model")
    report = verify(squares, normalized=args.normalized)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
