#!/usr/bin/env python3
"""Replay published ionization upper bounds. Not a new bound."""

from __future__ import annotations

import json
import math
from pathlib import Path


def b3() -> float:
    """Hundertmark–Pattakos–Schulz (2.9) closed form for b(3)."""
    s = 1.0 + math.sqrt(2.0)
    return (2.0 / 3.0) * (s ** (1.0 / 3.0)) / (s ** (2.0 / 3.0) - 1.0)


def half_sqrt2_plus_one() -> float:
    return 0.5 * (math.sqrt(2.0) + 1.0)


def lieb(z: float) -> float:
    return 2.0 * z + 1.0


def nam(z: float) -> float:
    return 1.22 * z + 3.0 * (z ** (1.0 / 3.0))


def hps_s2(z: float) -> float:
    return half_sqrt2_plus_one() * z + 2.96 * (z ** (1.0 / 3.0))


def hps_s3(z: float) -> float:
    return (
        b3() * z
        + 3.90 * (z ** (1.0 / 3.0))
        + 0.0134
        + 0.184 * (z ** (-1.0 / 3.0))
        + 0.0196 * (z ** (-2.0 / 3.0))
    )


def hps_coarse(z: float) -> float:
    return 1.1185 * z + 4.0 * (z ** (1.0 / 3.0))


def first_z(pred, zmin: int, zmax: int) -> int | None:
    for z in range(zmin, zmax + 1):
        if pred(z):
            return z
    return None


def build_record() -> dict:
    b = b3()
    s2 = half_sqrt2_plus_one()
    def row_at(z: int) -> dict:
        row = {"Z": z, "Lieb": lieb(z), "Nam": nam(z)}
        if z >= 2:
            row["HPS_s2"] = hps_s2(z)
        if z >= 4:
            row["HPS_s3"] = hps_s3(z)
            row["HPS_coarse"] = hps_coarse(z)
        return row

    sample_z = (1, 5, 6, 36, 118)
    rows = [row_at(z) for z in sample_z]

    nam_beats_lieb = first_z(lambda z: nam(z) < lieb(z), 1, 200)
    s2_beats_nam = first_z(lambda z: z >= 2 and hps_s2(z) < nam(z), 2, 200)
    s3_beats_s2 = first_z(lambda z: z >= 4 and hps_s3(z) < hps_s2(z), 4, 200)

    return {
        "constants": {
            "b3": b,
            "b3_window": [1.1184, 1.1185],
            "half_sqrt2_plus_one": s2,
            "s2_window": [1.2071, 1.2072],
        },
        "crossovers": {
            "Nam_beats_Lieb_first_integer_Z": nam_beats_lieb,
            "HPS_s2_beats_Nam_first_integer_Z": s2_beats_nam,
            "HPS_s3_beats_HPS_s2_first_integer_Z": s3_beats_s2,
            "paper_Nam_beats_Lieb": 6,
            "paper_s3_beats_s2_remark": 35.8,
        },
        "at_Z_118": {
            "Lieb": lieb(118),
            "Nam": nam(118),
            "HPS_s3": hps_s3(118),
            "HPS_coarse": hps_coarse(118),
        },
        "sample_rows": rows,
        "note": (
            "These are already-published upper bounds on Nc(Z). "
            "Replaying the comparison is not a new bound."
        ),
    }


def verify(record: dict) -> list[str]:
    errors = []
    b = record["constants"]["b3"]
    lo, hi = record["constants"]["b3_window"]
    if not (lo < b < hi):
        errors.append(f"b(3)={b} not in (1.1184, 1.1185)")
    s2 = record["constants"]["half_sqrt2_plus_one"]
    lo2, hi2 = record["constants"]["s2_window"]
    if not (lo2 < s2 < hi2):
        errors.append(f"(sqrt(2)+1)/2={s2} not in (1.2071, 1.2072)")
    if record["crossovers"]["Nam_beats_Lieb_first_integer_Z"] != 6:
        errors.append("Nam should first beat Lieb at Z=6")
    if record["crossovers"]["HPS_s2_beats_Nam_first_integer_Z"] != 2:
        errors.append("HPS s=2 should beat Nam at every Z>=2")
    s3s2 = record["crossovers"]["HPS_s3_beats_HPS_s2_first_integer_Z"]
    if s3s2 is None or s3s2 < 35 or s3s2 > 36:
        errors.append(f"s=3 vs s=2 first integer Z={s3s2}, expected 36")
    # Spot-check a few table rows against the closed forms.
    by_z = {row["Z"]: row for row in record["sample_rows"]}
    row6 = by_z[6]
    if abs(row6["Lieb"] - 13.0) > 1e-12:
        errors.append("Lieb(6) != 13")
    if row6["Nam"] >= row6["Lieb"]:
        errors.append("Nam(6) should be < Lieb(6)")
    if by_z[5]["Nam"] < by_z[5]["Lieb"]:
        errors.append("Nam should not yet beat Lieb at Z=5")
    return errors


def main() -> None:
    here = Path(__file__).resolve().parent
    record = build_record()
    out = here / "record.json"
    out.write_text(json.dumps(record, indent=2) + "\n")
    errors = verify(record)
    print(f"wrote {out}")
    print(f"b(3) = {record['constants']['b3']:.12f}  (paper window (1.1184, 1.1185))")
    print(
        f"(sqrt(2)+1)/2 = {record['constants']['half_sqrt2_plus_one']:.12f}  "
        "(paper window (1.2071, 1.2072))"
    )
    print("crossovers:", json.dumps(record["crossovers"]))
    print("at Z=118:", json.dumps(record["at_Z_118"]))
    if errors:
        print("VERIFY FAIL:")
        for e in errors:
            print(" ", e)
        raise SystemExit(1)
    print("VERIFY OK")


if __name__ == "__main__":
    main()
