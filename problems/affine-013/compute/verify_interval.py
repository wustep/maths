"""Independently check the interval closed form and the 3/4 lemma."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import hl_upper, interval_formula_check, interval_t, t_count  # noqa: E402


def main() -> None:
    ok = True
    for n in range(0, 80):
        brute = t_count(range(n))
        f1 = interval_t(n)
        f2 = interval_formula_check(n)
        if brute != f1 or f1 != f2:
            print("FAIL interval", n, brute, f1, f2)
            ok = False
        if brute > hl_upper(n):
            print("FAIL HL", n, brute, hl_upper(n))
            ok = False
    # centred interval, odd n = 2M+1
    for M in range(0, 25):
        s = range(-M, M + 1)
        n = 2 * M + 1
        brute = t_count(s)
        # still x≡y (mod 3) and z in range; for centred, z auto-in-range too
        if brute != interval_t(n):
            # may differ by translation of residues
            print(
                f"centred M={M} T={brute} uncentred={interval_t(n)} "
                f"ratio={brute/(n*n):.6f}"
            )
    print("interval formula ok" if ok else "FAILED")
    # sample {0,1,3}
    print("{0,1,3} T=", t_count([0, 1, 3]), "expected 4")
    print("{0,1,2} T=", t_count([0, 1, 2]), "expected 3")
    if t_count([0, 1, 3]) != 4 or t_count([0, 1, 2]) != 3:
        ok = False
        print("FAIL aaronson n=3 remark")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
