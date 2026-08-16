#!/usr/bin/env python3
"""Check that every syndrome in F_2^10 is a sum of at most 2 columns of H."""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_columns(path: Path) -> list[int]:
    rows: list[list[int]] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if " " in line:
            bits = [int(x) for x in line.split()]
        else:
            bits = [int(ch) for ch in line]
        if any(b not in (0, 1) for b in bits):
            raise SystemExit("FAIL: H has a non-binary entry")
        rows.append(bits)
    if len(rows) != 10:
        raise SystemExit(f"FAIL: expected 10 rows, got {len(rows)}")
    n = len(rows[0])
    if any(len(r) != n for r in rows):
        raise SystemExit("FAIL: ragged matrix")
    cols = [sum(rows[r][j] << r for r in range(10)) for j in range(n)]
    return cols


def gf2_rank(cols: list[int], width: int = 10) -> int:
    basis = [0] * width
    rank = 0
    for original in cols:
        v = original
        while v:
            p = v.bit_length() - 1
            if basis[p]:
                v ^= basis[p]
            else:
                basis[p] = v
                rank += 1
                break
    return rank


def main() -> None:
    cols = load_columns(HERE / "H_r10_n50.txt")
    n = len(cols)
    print(f"n={n} columns")
    if n != 50:
        raise SystemExit(f"FAIL: expected 50 columns, got {n}")
    if any(c == 0 for c in cols):
        raise SystemExit("FAIL: zero column")
    if len(set(cols)) != n:
        raise SystemExit("FAIL: repeated columns")
    rank = gf2_rank(cols)
    print(f"F2-rank={rank}")
    if rank != 10:
        raise SystemExit(f"FAIL: rank {rank} != 10")

    covered = [False] * 1024
    covered[0] = True
    for c in cols:
        covered[c] = True
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            covered[a ^ b] = True
    missing = [i for i, ok in enumerate(covered) if not ok]
    print(f"syndromes covered: {1024 - len(missing)}/1024")
    if missing:
        raise SystemExit(f"FAIL: uncovered {missing[:20]} (count {len(missing)})")
    print("PASS: every syndrome in F_2^10 is a sum of at most 2 columns")
    print("code parameters: [50,40]_2, covering radius exactly 2")
    print("columns_decimal:", cols)


if __name__ == "__main__":
    main()
