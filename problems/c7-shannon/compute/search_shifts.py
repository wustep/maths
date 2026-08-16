#!/usr/bin/env python3
"""Sample translations of the 382-orbit at the published fold denominator 109."""

from __future__ import annotations

import random
import time
from pathlib import Path

from c7_common import encode, format_word, greedy_mis_fast, residual_of
from reconstruct_polak import FOLD_DEN, MOD, Q, induced_edges, isolated_vertices, max_independent_set
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent


def folded_with_shift(shift: tuple[int, ...]) -> list[int]:
    pows = [pow(Q, i, MOD) for i in range(5)]
    out = []
    for t in range(MOD):
        coords = [((t * p + shift[j]) % MOD) * 2 // FOLD_DEN for j, p in enumerate(pows)]
        if any(c > 6 for c in coords):
            return []
        out.append(encode(coords))
    return out


def main() -> None:
    t0 = time.time()
    rng = random.Random(1)
    best = 0
    best_shift = None
    lines = []
    shifts = [(40, 123, 40, 123, 40), (0, 0, 0, 0, 0), (1, 0, 0, 0, 0)]
    for a in range(0, MOD, 20):
        for b in range(0, MOD, 30):
            shifts.append((a, b, a, b, a))
    for _ in range(80):
        shifts.append(tuple(rng.randrange(MOD) for _ in range(5)))
    print(f"trying {len(shifts)} shifts", flush=True)
    for i, shift in enumerate(shifts):
        folded = folded_with_shift(shift)
        if not folded:
            continue
        M = isolated_vertices(folded)
        residual = residual_of(M)
        I = greedy_mis_fast(residual)
        if len(M) >= 320 and 60 <= len(residual) <= 75:
            n_edges = len(induced_edges(residual))
            if n_edges <= 90:
                I = max_independent_set(residual)
        total = len(M) + len(I)
        if total > best:
            best = total
            best_shift = shift
            print(f"best {best} shift={shift} M={len(M)} res={len(residual)} I={len(I)}", flush=True)
            lines.append(f"{shift} M={len(M)} res={len(residual)} I={len(I)} total={total}")
            if total >= 368:
                R = sorted(set(M) | set(I))
                if first_conflict(R) is None:
                    out = HERE / f"R{len(R)}_shift.txt"
                    out.write_text("\n".join(format_word(v) for v in R) + "\n")
                    print(f"WROTE {out}")
        if i % 50 == 0:
            print(f"  {i}/{len(shifts)} best={best}", flush=True)
    (HERE / "shift_search.txt").write_text(
        f"best {best} shift {best_shift}\nseconds {time.time()-t0:.1f}\n" + "\n".join(lines) + "\n"
    )
    print(f"done best={best} shift={best_shift} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
