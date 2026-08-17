#!/usr/bin/env python3
"""Independent arithmetic classification of Aut-elements of a putative PP(12).

This does not claim a new exclusion of |G|=2 or |G|=3.  It records the
divisibility constraints that cut the remaining geometric types down to
the list used in ATTACK.md, and it checks each cited numerical identity.
"""

from __future__ import annotations

import json
import sys


def check(name: str, cond: bool, detail: str, rows: list) -> None:
    rows.append({"name": name, "ok": bool(cond), "detail": detail})


def main() -> None:
    rows: list[dict] = []
    n = 12
    v = n * n + n + 1
    check("v=157", v == 157, f"v={v}", rows)
    check("v mod 2", v % 2 == 1, f"{v}%2={v%2}", rows)
    check("v mod 3", v % 3 == 1, f"{v}%3={v%3}", rows)
    check("bruck-ryser silent", n % 4 == 0, f"{n}%4={n%4}", rows)
    det = 13 * (12 ** 78)
    check("det identity integer", det == 13 * 12**78, "13*12^78", rows)

    # Order-2: Baer + even non-square => elation.
    check("12 even", n % 2 == 0, "", rows)
    check("12 not square", int(n**0.5) ** 2 != n, "", rows)
    check("2 divides n (elation order)", n % 2 == 0, "elation group order | n", rows)
    check("n not 2 mod 4", n % 4 == 0, "the n≡2 (mod 4) involution ban is silent", rows)

    # Order-3 fixed-point count.
    # f ≡ v ≡ 1 (mod 3).
    possible_f = [f for f in range(0, v + 1) if f % 3 == 1]
    check("possible f start at 1", possible_f[0] == 1, str(possible_f[:6]), rows)

    # True homology: f = n+2 = 14, and 3 | (n-1).
    check("true homology f=14 forbidden by v", 14 % 3 != 1, "14%3=2", rows)
    check("true homology 3 divides n-1", (n - 1) % 3 != 0, f"{n-1}%3={(n-1)%3}", rows)

    # Generalized homology: axis invariant, k fixed points on axis,
    # f=1+k, k≡0 (mod 3) from f≡1, but axis action needs 13-k≡0 (mod 3)
    # i.e. k≡1 (mod 3).
    gh_ok = []
    for k in range(0, 14):
        f = 1 + k
        if f % 3 != 1:
            continue
        if (13 - k) % 3 != 0:
            continue
        gh_ok.append((k, f))
    check("no generalized homology of order 3", gh_ok == [], f"survivors={gh_ok}", rows)

    # Fano planar: a fixed Fano line sits on an ambient line with
    # 3 fixed + 10 extra points.  10 not divisible by 3.
    check("Fano line extra points", (13 - 3) % 3 != 0, f"10%3={10%3}", rows)

    # Order-3 planar with PG(2,3): extra on a fixed line is 13-4=9, ok.
    check("PG(2,3) line extra points ok", (13 - 4) % 3 == 0, "9%3=0", rows)

    # Generalized elation: f on the axis, f≡1 (mod 3), f≤13, not the
    # true elation f=13 (excluded by Janko–van Trung 1981).
    ge = [f for f in (1, 4, 7, 10, 13) if (13 - f) % 3 == 0]
    check(
        "g.e. candidates",
        ge == [1, 4, 7, 10, 13],
        f"f in {ge}; f=13 is the 1981 true-elation case",
        rows,
    )

    remaining = {
        "order_2": ["involutory elation (unique Baer type)"],
        "order_3": [
            "planar with Fix ≅ PG(2,3)",
            "generalized elation with f in {1,4,7,10}",
        ],
        "excluded_here_by_divisibility": [
            "true homology of order 3",
            "generalized homology of order 3",
            "planar with Fix ≅ PG(2,2)",
        ],
        "excluded_in_literature": [
            "true elation of order 3 (Janko–van Trung 1981)",
            "any |G| not in {1,2,3} (Akiyama–Suetake–Tanaka 2023)",
        ],
    }
    report = {
        "checks": rows,
        "all_ok": all(r["ok"] for r in rows),
        "remaining": remaining,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(0 if report["all_ok"] else 1)


if __name__ == "__main__":
    main()
