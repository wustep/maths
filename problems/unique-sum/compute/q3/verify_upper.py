#!/usr/bin/env python3
"""Check the saved p=59 upper-bound witness directly from the definition."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "p59_upper.json"


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    p = payload["p"]
    values = payload["witness"]
    if (
        p != 59
        or payload["cardinality"] != 15
        or values != sorted(set(values))
        or len(values) != payload["cardinality"]
        or any(type(value) is not int or not 0 <= value < p for value in values)
    ):
        raise AssertionError("malformed p=59 witness certificate")

    counts = [0] * p
    for left in values:
        for right in values:
            counts[(left + right) % p] += 1
    forbidden = [
        (residue, count)
        for residue, count in enumerate(counts)
        if count in (1, 2)
    ]
    if forbidden:
        raise AssertionError(f"unique sums remain: {forbidden}")
    if sum(count > 0 for count in counts) != payload["sumset_size"]:
        raise AssertionError("sumset-size annotation mismatch")
    if max(counts) != payload["max_ordered_multiplicity"]:
        raise AssertionError("maximum-multiplicity annotation mismatch")

    print(
        "VALID_UPPER p=59 cardinality=15 "
        f"ordered_pairs={len(values) ** 2} sumset_size={sum(count > 0 for count in counts)}"
    )
    print("BOUNDARY_UNRESOLVED size_at_most=14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
