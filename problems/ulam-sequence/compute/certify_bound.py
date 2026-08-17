#!/usr/bin/env python3
"""Exact integer certificate for a CS-majorant Frobenius bound.

Given a word, multiply the 0-1 matrices over the integers, form the sum of
squares of entries, and report C = (sum)^{1/(2L)}.  Independently checks
that the word is admissible and that the C-search nwords count matches the
closed recurrence for the language {1,2,3}^* with no consecutive 3s.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cs_matrices import MATS, count_admissible, eggleton_root, t3t1sq_root

HERE = Path(__file__).resolve().parent
CS_PUBLISHED = 1.454


def product_int(word: list[int]):
    A = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    for k in word:
        T = MATS[k].tolist()
        A = [
            [sum(T[i][p] * A[p][j] for p in range(4)) for j in range(4)]
            for i in range(4)
        ]
    return A


def frobenius2(A) -> int:
    return sum(A[i][j] * A[i][j] for i in range(4) for j in range(4))


def admissible(word: list[int]) -> bool:
    if any(k not in (1, 2, 3) for k in word):
        return False
    return all(not (word[i] == 3 and word[i + 1] == 3) for i in range(len(word) - 1))


def certify(word: list[int], nwords_reported: int | None = None) -> dict:
    L = len(word)
    if not admissible(word):
        raise ValueError(f"inadmissible word {word}")
    A = product_int(word)
    F2 = frobenius2(A)
    # C = F2^{1/(2L)}.  Compare to 1.454 by integer arithmetic:
    #     F2^{1/(2L)} < 1454/1000  iff  F2 * 1000^{2L} < 1454^{2L}.
    left = F2 * (1000 ** (2 * L))
    targets = (1454, 1452, 1445, 1444, 1443, 1442)
    beats = {f"beats_{t/1000:.3f}_exact": left < (t ** (2 * L)) for t in targets}
    CF = F2 ** (0.5 / L)
    rec = {
        "word": "".join(str(k) for k in word),
        "L": L,
        "admissible": True,
        "matrix": A,
        "F2": F2,
        "CF_float": CF,
        **beats,
        "integer_compare_1454": {
            "left": str(left),
            "right": str(1454 ** (2 * L)),
        },
        "count_admissible": count_admissible(L),
        "nwords_reported": nwords_reported,
        "nwords_match": nwords_reported is None or nwords_reported == count_admissible(L),
        "eggleton_root": eggleton_root(),
        "method_barrier_T3T1sq": t3t1sq_root(),
        "published_CS": CS_PUBLISHED,
    }
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--word", required=True, help="digits 1,2,3 e.g. 2313131131311313")
    ap.add_argument("--nwords", type=int, default=None)
    ap.add_argument("--out", type=Path, default=HERE / "certificate.json")
    args = ap.parse_args()
    word = [int(c) for c in args.word]
    rec = certify(word, args.nwords)
    args.out.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in rec if k != "integer_compare_1454"}, indent=2))
    print("integer compare 1454: left < right =", rec["beats_1.454_exact"])
    if not rec["beats_1.454_exact"]:
        raise SystemExit("does not beat 1.454")


if __name__ == "__main__":
    main()
