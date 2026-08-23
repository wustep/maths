#!/usr/bin/env python3
"""Extract exact field coordinates from the committed reserve source table."""

from __future__ import annotations

import json
import re
from pathlib import Path

from udg import BASIS_INT, F, write_vtx

HERE = Path(__file__).resolve().parent


def parse_repr(value):
    text = value.strip()
    denominator = 1
    if text.startswith("(") and ")/" in text:
        close = text.rfind(")/")
        body = text[1:close]
        denominator = int(text[close + 2 :])
    elif "/" in text:
        body, raw_denominator = text.rsplit("/", 1)
        denominator = int(raw_denominator)
    else:
        body = text

    coefficients = [0] * 8
    terms = re.findall(r"[+-]?[^+-]+", body)
    if not terms:
        raise ValueError(f"empty field representation {value!r}")
    for term in terms:
        sign = -1 if term.startswith("-") else 1
        unsigned = term[1:] if term[:1] in "+-" else term
        if "√" in unsigned:
            raw_coefficient, raw_basis = unsigned.split("√", 1)
            coefficient = int(raw_coefficient) if raw_coefficient else 1
            try:
                index = BASIS_INT.index(int(raw_basis))
            except ValueError as error:
                raise ValueError(f"basis √{raw_basis} is outside the field") from error
            coefficients[index] += sign * coefficient
        else:
            coefficients[0] += sign * int(unsigned)
    return F(tuple(coefficients), denominator).normal()


def main():
    source = json.loads((HERE / "reserve_source.json").read_text())
    if source["n_kept"] != 677 or len(source["all"]) != 677:
        raise ValueError("source table does not contain the expected 677 records")
    points = [
        (parse_repr(record["x_repr"]), parse_repr(record["y_repr"]))
        for record in source["all"]
    ]
    if len(set(points)) != 677:
        raise ValueError("source table produced duplicate exact coordinates")
    write_vtx(HERE / "reserve_extras.vtx", points)
    print("reserve_extras.vtx: extracted 677 exact coordinates")


if __name__ == "__main__":
    main()
