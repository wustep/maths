#!/usr/bin/env python3
"""Recover M_OK's last hex word (paper OCR: ICE) and certify the OK seed.

Davydov--Marcugini--Pambianco, arXiv:2511.02542, (6.10) and Theorem 7.1
print the last Ostergard--Kaikkonen [18,9]_2 column as the invalid hex
word ICE.  This script treats that as OCR, tries 1CE first, then every
other 9-bit column, and keeps a candidate only if:

* H_OK = [I_9 | M_OK] has 18 distinct nonzero columns and rank 9;
* covering radius is exactly 3;
* columns 6, 9, 16 (one-based) sum to zero and lie in distinct P_OK blocks;
* P_OK is a (3,1)-partition of F_2^9.

All integer columns are LSB-first: bit i is matrix row i+1.  Paper hex
is MSB-first with row 1 as the high bit, matching build_qm44.py.
"""

from __future__ import annotations

OK_HEX_PREFIX = (0x1A0, 0x174, 0x0A5, 0x173, 0x017, 0x0E8, 0x009, 0x18D)
P_OK_ONE_BASED = (
    (1, 2, 4),
    (3,),
    (5, 8),
    (6, 17),
    (7, 10),
    (11, 14),
    (12,),
    (13, 18),
    (15,),
    (9,),
    (16,),
)


def reverse_bits(value: int, width: int) -> int:
    return sum(((value >> bit) & 1) << (width - 1 - bit) for bit in range(width))


def ok_columns(last_hex: int) -> list[int]:
    columns = [1 << row for row in range(9)]
    columns.extend(reverse_bits(value, 9) for value in OK_HEX_PREFIX)
    columns.append(reverse_bits(last_hex, 9))
    return columns


def block_of_column() -> list[int]:
    labels = [-1] * 18
    for block, members in enumerate(P_OK_ONE_BASED):
        for one_based in members:
            labels[one_based - 1] = block
    assert all(label >= 0 for label in labels)
    return labels


def covering_counts(columns: list[int], redundancy: int) -> tuple[int, int, int]:
    space = 1 << redundancy
    covered = bytearray(space)
    covered[0] = 1
    for column in columns:
        covered[column] = 1
    le1 = sum(covered)
    for left, column in enumerate(columns):
        for right in range(left):
            covered[column ^ columns[right]] = 1
    le2 = sum(covered)
    for left, a in enumerate(columns):
        for middle in range(left):
            ab = a ^ columns[middle]
            for right in range(middle):
                covered[ab ^ columns[right]] = 1
    return le1, le2, sum(covered)


def is_partition_31(columns: list[int], labels: list[int], redundancy: int) -> bool:
    """Every vector is a sum of 1, 2, or 3 columns from distinct blocks."""
    space = 1 << redundancy
    covered = bytearray(space)
    for index, column in enumerate(columns):
        covered[column] = 1
    for left, a in enumerate(columns):
        for right in range(left):
            if labels[left] == labels[right]:
                continue
            covered[a ^ columns[right]] = 1
    for left, a in enumerate(columns):
        for middle in range(left):
            if labels[left] == labels[middle]:
                continue
            ab = a ^ columns[middle]
            used = {labels[left], labels[middle]}
            for right in range(middle):
                if labels[right] in used:
                    continue
                covered[ab ^ columns[right]] = 1
    return sum(covered) == space


def candidate_ok(last_hex: int, labels: list[int]) -> dict[str, object] | None:
    columns = ok_columns(last_hex)
    if len(set(columns)) != 18 or not all(columns):
        return None
    if any(column >= (1 << 9) for column in columns):
        return None
    # Identity plus eight recovered M_OK columns already have rank 9; the
    # last column must stay in F_2^9 and not collapse projectivity.
    le1, le2, le3 = covering_counts(columns, 9)
    if le3 != 512 or le2 == 512:
        return None
    if columns[5] ^ columns[8] ^ columns[15] != 0:
        return None
    if len({labels[5], labels[8], labels[15]}) != 3:
        return None
    if not is_partition_31(columns, labels, 9):
        return None
    return {
        "last_hex": last_hex,
        "columns": columns,
        "covered_le1": le1,
        "covered_le2": le2,
        "covered_le3": le3,
    }


def main() -> None:
    labels = block_of_column()
    preferred = 0x1CE
    hits: list[dict[str, object]] = []
    first = candidate_ok(preferred, labels)
    if first is not None:
        hits.append(first)
    for last_hex in range(1 << 9):
        if last_hex == preferred:
            continue
        found = candidate_ok(last_hex, labels)
        if found is not None:
            hits.append(found)

    print("tried_last_words=%d hits=%d preferred_1CE=%s" % (
        1 << 9,
        len(hits),
        "yes" if first is not None else "no",
    ))
    for hit in hits:
        print(
            "OK last=0x%03X columns=%s le1=%d le2=%d le3=%d" %
            (
                hit["last_hex"],
                hit["columns"],
                hit["covered_le1"],
                hit["covered_le2"],
                hit["covered_le3"],
            )
        )
    if first is None:
        raise SystemExit("preferred last word 1CE failed the seed hypotheses")
    if any(hit["last_hex"] != preferred for hit in hits):
        raise SystemExit("multiple last words satisfy the seed hypotheses")
    print("PASS M_OK last word is 1CE; P_OK is a (3,1)-partition")


if __name__ == "__main__":
    main()
