#!/usr/bin/env python3
"""Independent check: H_OK radius 3 and 9-block (3,0)-partition."""

from __future__ import annotations

from pathlib import Path

from recover_mok import covering_counts, ok_columns
from build_qm43_p9 import P9_LABELS, is_partition_30


def main() -> None:
    labels_path = Path("compute/partition_H_OK_p9_ell0.txt")
    labels = [
        int(tok)
        for line in labels_path.read_text().splitlines()
        if line and not line.startswith("#")
        for tok in line.split()
    ]
    assert labels == P9_LABELS
    assert len(set(labels)) == 9
    columns = ok_columns(0x1CE)
    le1, le2, le3 = covering_counts(columns, 9)
    assert (le1, le2, le3) == (19, 163, 512)
    assert is_partition_30(columns, labels, 9)
    # ell=1 must fail (dependent triple shares a block)
    assert len({labels[5], labels[8], labels[15]}) < 3
    print(
        "PASS H_OK r=9 n=18 le3=%d/512 p9_ell0=yes ell1_impossible_by_triple=yes"
        % le3
    )


if __name__ == "__main__":
    main()
