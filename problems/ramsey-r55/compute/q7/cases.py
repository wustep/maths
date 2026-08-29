#!/usr/bin/env python3
"""Degree-feasible order-2/3/5 representatives on 43 vertices.

A fixed vertex adjacent to k of the c p-cycles has degree p*k+d with
0 <= d <= fixed-1.  R(4,5)=25 forces every degree into [18,24].
Complementation sends k to c-k, so one representative covers both.
When k=0 is the only leftover, the complement c is used so the
existing nonempty-prefix symmetry breaking still applies.
"""

from __future__ import annotations

import json
from pathlib import Path


N = 43
PRIMES = (2, 3, 5)
DEG = (18, 24)
# Independently replayed on main; do not re-solve them here.
Q4_CLOSED = frozenset({"p5_c6_k2", "p5_c6_k3", "p5_c7_k3"})
Q5_CLOSED = frozenset({"p5_c4_k4"})
Q6_CLOSED = frozenset({"p5_c5_k2"})
CLOSED = Q4_CLOSED | Q5_CLOSED | Q6_CLOSED
# q2/q3 byte-identical maximum-cycle CNFs.
KNOWN_MAX_SHA256 = {
    (2, 21, 9): "9287d2d355d3f2f75a7bb79485cdebf8261827a51550d28b1f8de271f3eec9ef",
    (2, 21, 10): "407f41e8c0d6924ab8027361ae595b451b3c9c16820698b3f71e8c73120cce75",
    (3, 14, 6): "18180db92789d23faf4ffe73bd8676fc6af448bb1889d815378fcf888360fd05",
    (3, 14, 7): "d9cfe3d0949d66e37547e5c2f7dbfe44a2fef65d80331518f05c4352bf4c434d",
    (5, 8, 4): "de64155ef134bc37a27659db67cbba31ee6d998e52dedd8ce9f4c80cabda627d",
}


def feasible_k(p: int, cycles: int) -> list[int]:
    fixed = N - cycles * p
    out = []
    for k in range(cycles + 1):
        if any(DEG[0] <= p * k + d <= DEG[1] for d in range(fixed)):
            out.append(k)
    return out


def representatives(p: int) -> list[dict]:
    rows = []
    for cycles in range(1, N // p + 1):
        fixed = N - cycles * p
        feas = feasible_k(p, cycles)
        covered: set[int] = set()
        checked: list[int] = []
        for k in feas:
            partner = cycles - k
            if k == 0 and partner in feas and partner >= 1:
                if partner not in checked:
                    checked.append(partner)
                covered.update({k, partner})
            elif 1 <= k <= partner:
                checked.append(k)
                covered.update({k, partner})
        for k in feas:
            if k not in covered:
                checked.append(k)
                covered.update({k, cycles - k})
        for k in sorted(set(checked)):
            partner = cycles - k
            covers = sorted({k, partner} & set(feas))
            p5_special = (p, cycles, k) == (5, 8, 4)
            rows.append(
                {
                    "covers_k": covers,
                    "cycles": cycles,
                    "cycle_type": f"{p}^{cycles} 1^{fixed}",
                    "expected_cnf_sha256": KNOWN_MAX_SHA256.get((p, cycles, k)),
                    "fixed": fixed,
                    "fixed_cycle_count": k,
                    "maximum_cycle": cycles == N // p,
                    "name": f"p{p}_c{cycles}_k{k}",
                    "p": p,
                    "p5_symbreak": p5_special,
                    "anchor_symbreak": not p5_special,
                }
            )
    return rows


def all_cases() -> list[dict]:
    return [row for p in PRIMES for row in representatives(p)]


def leftover() -> list[dict]:
    return [row for row in all_cases() if row["p"] in PRIMES]


def leftover_q5() -> list[dict]:
    return [row for row in leftover() if row["name"] not in Q4_CLOSED]


def leftover_q6() -> list[dict]:
    return [row for row in leftover() if row["name"] not in (Q4_CLOSED | Q5_CLOSED)]


def leftover_q7() -> list[dict]:
    return [row for row in leftover() if row["name"] not in CLOSED]


def main() -> int:
    rows = all_cases()
    rec = {
        "degree_window": list(DEG),
        "n": N,
        "note": (
            "Representatives for leftover order-2/3/5 automorphisms on 43 "
            "vertices after q3. q4 closed 5^6 1^13 (k=2,3) and 5^7 1^8 "
            "(k=3). q5 closed 5^4 1^23 at k=4 (covers k=0). q6 closed "
            "5^5 1^18 at k=2 (covers k=3). leftover_q7 skips those five. "
            "This list is not a bound on R(5,5)."
        ),
        "primes": list(PRIMES),
        "q4_closed": sorted(Q4_CLOSED),
        "q5_closed": sorted(Q5_CLOSED),
        "q6_closed": sorted(Q6_CLOSED),
        "q7_names": [row["name"] for row in leftover_q7()],
        "q7_total": len(leftover_q7()),
        "representatives": rows,
        "total": len(rows),
        "totals_by_prime": {str(p): sum(1 for row in rows if row["p"] == p) for p in PRIMES},
    }
    out = Path(__file__).resolve().parent / "certs" / "cases.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "q4_closed": rec["q4_closed"],
        "q5_closed": rec["q5_closed"],
        "q6_closed": rec["q6_closed"],
        "q7_total": rec["q7_total"],
        "total": rec["total"],
        "totals_by_prime": rec["totals_by_prime"],
        "q7_names": rec["q7_names"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
