#!/usr/bin/env python3
"""Write a 0/1 parity-check matrix from integer columns (LSB = row 1)."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--columns", required=True,
                        help="space-separated decimals, or a file of them")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--comment", action="append", default=[])
    args = parser.parse_args()

    text = args.columns
    path = Path(text)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    columns = [int(token, 0) for token in text.replace(",", " ").split()
               if token and not token.startswith("#")]
    if len(columns) != args.n:
        raise SystemExit(f"expected {args.n} columns, got {len(columns)}")
    if len(set(columns)) != args.n or min(columns) <= 0 or max(columns) >= (1 << args.r):
        raise SystemExit("columns must be distinct, nonzero, and in range")

    lines = [f"# {comment}" for comment in args.comment]
    lines.append(f"# {args.r} x {args.n} binary parity-check matrix; LSB = row 1")
    for row in range(args.r):
        lines.append(" ".join(str((column >> row) & 1) for column in columns))
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.output} r={args.r} n={args.n}")


if __name__ == "__main__":
    main()
