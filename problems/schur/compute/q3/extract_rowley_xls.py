#!/usr/bin/env python3
"""Extract Rowley's published 1696-coloring from the ancillary workbook.

The binary workbook is not vendored.  Fetch it from the official arXiv
source archive and install xlrd 2.x before running this provenance check.
The resulting plain-text coloring is committed and needs only the standard
library verifier in the parent directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_XLS_SHA256 = "c50cf981c1c437557b261cb8a66e193ee2cf77a8a50b0ae70c986b1c1cbb6fbb"
EXPECTED_COLORING_SHA256 = "feef1da7e70d328e2b0771a4b0f8b91329f2f832482a6103c72cb12524c40896"
SHEET = "S(7) >= 1696"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    workbook_hash = sha256(args.workbook)
    if workbook_hash != EXPECTED_XLS_SHA256:
        raise ValueError(
            f"unexpected workbook SHA-256 {workbook_hash}; "
            f"expected {EXPECTED_XLS_SHA256}"
        )

    try:
        import xlrd
    except ImportError as exc:
        raise SystemExit("install xlrd 2.x to extract the legacy XLS workbook") from exc

    sheet = xlrd.open_workbook(args.workbook).sheet_by_name(SHEET)
    colors: list[int] = []
    for x, row in enumerate(range(5, 1701), start=1):
        workbook_x = sheet.cell_value(row, 3)
        workbook_color = sheet.cell_value(row, 4)
        if workbook_x != x:
            raise ValueError(f"row {row}: expected integer {x}, found {workbook_x!r}")
        if workbook_color not in range(1, 8):
            raise ValueError(f"row {row}: invalid subset {workbook_color!r}")
        colors.append(int(workbook_color) - 1)

    args.output.write_text(" ".join(map(str, colors)) + "\n", encoding="ascii")
    coloring_hash = sha256(args.output)
    if coloring_hash != EXPECTED_COLORING_SHA256:
        raise ValueError(
            f"unexpected coloring SHA-256 {coloring_hash}; "
            f"expected {EXPECTED_COLORING_SHA256}"
        )
    print(
        json.dumps(
            {
                "coloring_sha256": coloring_hash,
                "length": len(colors),
                "result": "extracted",
                "sheet": SHEET,
                "workbook_sha256": workbook_hash,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
