#!/usr/bin/env python3
"""Replay the explicit published ES(7) interval from its two formulas."""

from math import comb


def main() -> None:
    k = 7
    lower = 2 ** (k - 2) + 1
    upper = comb(2 * k - 5, k - 2) - comb(2 * k - 8, k - 3) + 2
    assert lower == 33
    assert upper == 113
    print(f"record arithmetic: {lower} <= ES(7) <= {upper}")


if __name__ == "__main__":
    main()
