#!/usr/bin/env python3
"""Second path for the Z=2,3,4,5 envelope table. stdlib math only.

No mpmath, no shared helpers with envelopes.py. Closed forms for b(2), b(3)
and the same printed / q1 decimals. Diffs envelopes.json.

Replay: python3 envelopes.py && python3 envelopes_check.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def b2() -> float:
    return 0.5 * (math.sqrt(2.0) + 1.0)


def b3() -> float:
    s = 1.0 + math.sqrt(2.0)
    return (2.0 / 3.0) * (s ** (1.0 / 3.0)) / (s ** (2.0 / 3.0) - 1.0)


def max_int_below(U: float) -> int:
    n = math.floor(U)
    if abs(U - n) < 1e-15:
        return n - 1
    return int(n)


def main() -> None:
    path = CERTS / "envelopes.json"
    blob = json.loads(path.read_text())
    b2v, b3v = b2(), b3()
    if abs(b2v - float(blob["constants"]["b2"])) > 1e-12:
        raise SystemExit("b2 mismatch")
    if abs(b3v - float(blob["constants"]["b3"])) > 1e-12:
        raise SystemExit("b3 mismatch")

    def z13(z):
        return z ** (1.0 / 3.0)

    def expected(z):
        t = z13(z)
        return {
            "lieb": 2.0 * z + 1.0,
            "nam": 1.22 * z + 3.0 * t,
            "hps_s2_printed": b2v * z + 2.96 * t if z >= 2 else None,
            "hps_s2_q1": b2v * z + 2.953 * t if z >= 2 else None,
            "hps_s3_printed": (
                b3v * z + 3.90 * t + 0.0134 + 0.184 / t + 0.0196 / (t * t)
                if z >= 4
                else None
            ),
            "hps_s3_q1": (
                b3v * z + 3.892 * t + 0.0134 + 0.184 / t + 0.0196 / (t * t)
                if z >= 4
                else None
            ),
            "hps_simplified_printed": 1.1185 * z + 4.0 * t if z >= 4 else None,
            "hps_simplified_q1": 1.1185 * z + 3.9781 * t if z >= 4 else None,
        }

    for row in blob["at"]:
        z = row["Z"]
        exp = expected(z)
        for key, U in exp.items():
            got = row[key]
            if U is None:
                if got is not None:
                    raise SystemExit(f"Z={z} {key} should be n/a")
                continue
            if abs(got["U_float"] - U) > 5e-12:
                raise SystemExit(f"Z={z} {key}: {got['U_float']} vs {U}")
            if got["max_integer_Nc"] != max_int_below(U):
                raise SystemExit(
                    f"Z={z} {key} integer: {got['max_integer_Nc']} vs {max_int_below(U)}"
                )
        if row["best_published"]["name"] != "lieb":
            raise SystemExit(f"Z={z}: best published should be Lieb")
        if row["best_published"]["max_integer_Nc"] != 2 * z:
            raise SystemExit(f"Z={z}: Lieb max integer should be 2Z")
        if row["zhislin_N0_at_least"] != z:
            raise SystemExit("Zhislin floor drifted")

    print("envelopes_check.py agrees with envelopes.json (stdlib path)")
    print("At Z=2,3,4,5 Lieb is the best published integer bound:")
    print("  Nc(2)<=4, Nc(3)<=6, Nc(4)<=8, Nc(5)<=10.")


if __name__ == "__main__":
    main()
