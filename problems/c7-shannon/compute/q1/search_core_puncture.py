#!/usr/bin/env python3
"""Punctured isolate core (shape 3).

Delete k vertices from the Polak-Schrijver isolate set M of size 327,
then take an exact maximum independent set in the residual of what remains.
This re-packs the leftover, unlike a k-out of the finished 367-set.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from c7_common import format_word, residual_of
from reconstruct_polak import (
    fold_words,
    geometric_orbit,
    induced_edges,
    isolated_vertices,
    max_independent_set,
)
from verify_set import first_conflict

def main() -> None:
    t0 = time.time()
    folded = fold_words(geometric_orbit())
    M = isolated_vertices(folded)
    print(f"|M|={len(M)}", flush=True)
    residual0 = residual_of(M)
    I0 = max_independent_set(residual0)
    print(
        f"k=0 residual={len(residual0)} edges={len(induced_edges(residual0))} "
        f"alpha={len(I0)} total={len(M)+len(I0)}",
        flush=True,
    )
    best = len(M) + len(I0)
    hit = None
    lines = [
        f"M {len(M)}",
        f"k=0 res={len(residual0)} I={len(I0)} total={best}",
    ]

    # k=1: every isolate.
    for i, m in enumerate(M):
        base = M[:i] + M[i + 1 :]
        residual = residual_of(base)
        if len(residual) > 95:
            I = []
            skipped = True
        else:
            skipped = False
            I = max_independent_set(residual)
        total = len(base) + len(I)
        if total > best or (not skipped and i < 3):
            if total > best:
                best = total
            msg = (
                f"k=1 i={i} drop={format_word(m)} res={len(residual)} "
                f"I={len(I)} total={total} skip={skipped}"
            )
            print(msg, flush=True)
            lines.append(msg)
        if total >= 368 and not skipped:
            R = sorted(set(base) | set(I))
            if first_conflict(R) is None:
                hit = R
                break
        if i % 50 == 0:
            print(f"  k=1 {i}/{len(M)} best={best} t={time.time()-t0:.1f}s", flush=True)

    # k=2: only if k=1 never gained; sample structured pairs (share a coordinate).
    if hit is None:
        trials = 0
        for i in range(len(M)):
            for j in range(i + 1, len(M)):
                # skip most pairs: keep those whose closed-neighbourhoods overlap
                # is handled by residual size; cap wall-clock via stride.
                if (i + 3 * j) % 17 != 0:
                    continue
                base = [M[t] for t in range(len(M)) if t != i and t != j]
                residual = residual_of(base)
                if len(residual) > 95:
                    continue
                I = max_independent_set(residual)
                total = len(base) + len(I)
                trials += 1
                if total > best:
                    best = total
                    msg = (
                        f"k=2 i={i} j={j} res={len(residual)} I={len(I)} total={total}"
                    )
                    print(msg, flush=True)
                    lines.append(msg)
                if total >= 368:
                    R = sorted(set(base) | set(I))
                    if first_conflict(R) is None:
                        hit = R
                        break
            if hit is not None:
                break
            if i % 20 == 0:
                print(
                    f"  k=2 i={i} trials={trials} best={best} t={time.time()-t0:.1f}s",
                    flush=True,
                )
        lines.append(f"k=2 trials {trials}")

    lines.append(f"best {best}")
    lines.append(f"seconds {time.time()-t0:.1f}")
    if hit is not None:
        out = HERE / f"R{len(hit)}_core.txt"
        out.write_text("\n".join(format_word(v) for v in hit) + "\n")
        lines.append(f"wrote {out}")
        print(f"WROTE {out} size={len(hit)}")
    else:
        print(f"no 368 from core puncture best={best}")
        lines.append("no 368")
    (HERE / "core_puncture_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
