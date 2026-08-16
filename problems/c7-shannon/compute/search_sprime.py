#!/usr/bin/env python3
"""Keep a maximum independent set of the folded 382-orbit, not only isolates.

Polak-Schrijver step (iv) deletes every vertex that touches an edge in the
folded image S'. The 327 isolates are a feasible independent set, but G[S']
may be larger: isolates plus an MIS of the conflict component. Then extend
the residual as in step (v).
"""

from __future__ import annotations

from pathlib import Path

from c7_common import format_word, residual_of
from reconstruct_polak import (
    fold_words,
    geometric_orbit,
    induced_edges,
    isolated_vertices,
    max_independent_set,
)
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent


def main() -> None:
    folded = fold_words(geometric_orbit())
    S = sorted(set(folded))
    print(f"|S'|={len(S)}")
    isolates = set(isolated_vertices(S))
    conflict = [v for v in S if v not in isolates]
    edges = induced_edges(conflict)
    print(f"isolates={len(isolates)} conflict={len(conflict)} edges={len(edges)}")
    I_conf = max_independent_set(conflict)
    print(f"alpha(conflict)={len(I_conf)}")
    M = sorted(isolates | set(I_conf))
    print(f"|M_mis|={len(M)}")
    residual = residual_of(M)
    redges = induced_edges(residual)
    print(f"residual verts={len(residual)} edges={len(redges)}")
    if len(residual) <= 90:
        I = max_independent_set(residual)
    else:
        I = []
        print("residual too large for exact MIS this pass")
    print(f"|I|={len(I)}")
    R = sorted(set(M) | set(I))
    print(f"|R|={len(R)}")
    if first_conflict(R) is not None:
        raise SystemExit("adjacent pair in S'-MIS construction")
    out = HERE / f"R{len(R)}_sprime.txt"
    out.write_text("\n".join(format_word(v) for v in R) + "\n")
    (HERE / "sprime_stats.txt").write_text(
        f"S {len(S)}\n"
        f"isolates {len(isolates)}\n"
        f"conflict {len(conflict)}\n"
        f"conflict_edges {len(edges)}\n"
        f"alpha_conflict {len(I_conf)}\n"
        f"M {len(M)}\n"
        f"residual {len(residual)}\n"
        f"residual_edges {len(redges)}\n"
        f"I {len(I)}\n"
        f"R {len(R)}\n"
    )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
