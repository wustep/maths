"""Classify every p-independent (s,r)-obstruction in N_13."""

from __future__ import annotations

import json
from pathlib import Path

K, M = 13, 14
NPAIRS = M * M


def pair_bit(s: int, r: int) -> int:
    return 1 << (s * M + r)


ALL = (1 << NPAIRS) - 1
FAIL = [[0] * M for _ in range(K)]
for i in range(K):
    idx = i + 1
    for val in range(M):
        msk = 0
        for s in range(M):
            for r in range(M):
                if (s * val + r * idx) % M in (0, M - 1):
                    msk |= pair_bit(s, r)
        FAIL[i][val] = msk


def zeros_mask(zero_idx: list[int]) -> int:
    m = 0
    for i in zero_idx:
        m |= FAIL[i][0]
    return m


def exists_mixed(zero_idx: list[int]) -> list[int] | None:
    """One unsaved assignment of the complementary coordinates, or None."""
    Z = set(zero_idx)
    free = [i for i in range(K) if i not in Z]
    base = zeros_mask(zero_idx)
    remain = ALL & ~base
    if remain == 0:
        raise RuntimeError("zeros already cover")

    # prune table: remaining killers of each pair among free coords / nonzero vals
    vals = [0] * len(free)

    def can_kill(remain_bits: int, pos: int) -> bool:
        # every remaining pair must have a killer in free[pos:]
        leftover = remain_bits
        # cheap: OR of all remaining fail masks
        pool = 0
        for j in range(pos, len(free)):
            i = free[j]
            for val in range(1, M):
                pool |= FAIL[i][val]
        return leftover & ~pool == 0

    found: list[int] | None = None

    def rec(pos: int, cov: int) -> bool:
        nonlocal found
        leftover = remain & ~cov
        if leftover == 0:
            v = [0] * K
            for j, i in enumerate(free):
                v[i] = vals[j]
            found = v
            return True
        if pos == len(free):
            return False
        if not can_kill(leftover, pos):
            return False
        i = free[pos]
        for val in range(1, M):
            vals[pos] = val
            if rec(pos + 1, cov | FAIL[i][val]):
                return True
        return False

    rec(0, 0)
    return found


def main() -> None:
    n_full = 0
    n_mixed = 0
    full_tmpls = []
    mixed = []
    for mask in range(1, (1 << K) - 1):
        zero_idx = [i for i in range(K) if mask >> i & 1]
        if zeros_mask(zero_idx) == ALL:
            n_full += 1
            tmpl = [0 if i in set(zero_idx) else -1 for i in range(K)]
            full_tmpls.append(tmpl)
            continue
        hit = exists_mixed(zero_idx)
        if hit is not None:
            n_mixed += 1
            mixed.append({"zeros": zero_idx, "example": hit})

    n_vec = 0
    for tmpl in full_tmpls:
        nfree = tmpl.count(-1)
        n_vec += 13**nfree

    print(f"Nk_zero_patterns {(1 << K) - 2}")
    print(f"zeros_alone_cover_patterns {n_full}")
    print(f"mixed_obstruction_patterns {n_mixed}")
    print(f"zeros_cover_vectors {n_vec}")
    if mixed:
        print("mixed examples:")
        for e in mixed[:8]:
            print(" ", e)
    else:
        print("NO mixed obstructions")

    # describe the zeros-alone family
    odds = [i for i in range(K) if (i + 1) % 2 == 1]
    evens = [i for i in range(K) if (i + 1) % 2 == 0]
    print(f"odd_speed_indices (0-based) {odds}")
    print(f"even_speed_indices (0-based) {evens}")
    n_contain_odds = 0
    for tmpl in full_tmpls:
        if all(tmpl[i] == 0 for i in odds):
            n_contain_odds += 1
    print(f"full_cover_patterns_containing_all_odd_zeros {n_contain_odds} / {n_full}")

    out = {
        "k": 13,
        "zeros_alone_cover_patterns": n_full,
        "mixed_obstruction_patterns": n_mixed,
        "zeros_cover_vectors": n_vec,
        "all_full_contain_odd_zeros": n_contain_odds == n_full,
        "mixed": mixed[:50],
    }
    d = Path(__file__).resolve().parent / "certs"
    d.mkdir(exist_ok=True)
    (d / "obstructions_indep.json").write_text(json.dumps(out, indent=2))
    print("wrote certs/obstructions_indep.json")


if __name__ == "__main__":
    main()
