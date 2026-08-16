#!/usr/bin/env python3
"""CEGAR around a product template 10 x 33 in C7^2 ⊠ C7^3.

Sibling note: a cyclic/product template that kills one family can leave
thousands of other violations. Add adjacent-pair clauses incrementally and
stop if the leftover count plateaus.

Start from an explicit independent set in C7^{⊠2} times one in C7^{⊠3}
(sizes 10 and 33), then ask SAT for 38 extra residual vertices, adding
conflict clauses only when a model uses an edge.
"""

from __future__ import annotations

import itertools
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from c7_common import N, adjacent, encode, format_word, residual_of
from search_fewflip_sat import atmost
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent


def pair_adj(u: tuple[int, ...], v: tuple[int, ...]) -> bool:
    if u == v:
        return False
    for a, b in zip(u, v):
        d = (a - b) % N
        if d > 3:
            d = N - d
        if d > 1:
            return False
    return True


def mis_small(dim: int, target: int) -> list[tuple[int, ...]]:
    """Exact MIS via bitset/SAT on C7^{⊠dim} for dim=2 (49 verts)."""
    verts = list(itertools.product(range(N), repeat=dim))
    n = len(verts)
    # greedy+improve then SAT for target
    taken = []
    banned = set()
    for v in verts:
        if v in banned:
            continue
        taken.append(v)
        banned.add(v)
        for w in verts:
            if pair_adj(v, w):
                banned.add(w)
    if len(taken) >= target:
        return taken[:target]
    # SAT
    lits = list(range(1, n + 1))
    solver = Cadical195()
    for i, u in enumerate(verts):
        for j in range(i + 1, n):
            if pair_adj(u, verts[j]):
                solver.add_clause([-lits[i], -lits[j]])
    extra, _ = atmost([-x for x in lits], n - target, n)
    for cl in extra:
        solver.add_clause(cl)
    if not solver.solve():
        raise SystemExit(f"no independent set of size {target} in dim {dim}")
    model = set(solver.get_model())
    return [verts[i] for i, lit in enumerate(lits) if lit in model]


def mis_dim3(target: int = 33) -> list[tuple[int, ...]]:
    """Known α(C7^{⊠3})=33. Random-greedy then SAT on a reduced pool if needed."""
    verts = list(itertools.product(range(N), repeat=3))
    best: list[tuple[int, ...]] = []
    import random

    rng = random.Random(0)
    for _ in range(40):
        order = verts[:]
        rng.shuffle(order)
        taken = []
        banned = set()
        for v in order:
            if v in banned:
                continue
            taken.append(v)
            banned.add(v)
            for w in verts:
                if w not in banned and pair_adj(v, w):
                    banned.add(w)
        if len(taken) > len(best):
            best = taken
            if len(best) >= target:
                return best
    if len(best) < target:
        raise SystemExit(f"failed to find 33-set in C7^3, best={len(best)}")
    return best


def main() -> None:
    t0 = time.time()
    a = mis_small(2, 10)
    b = mis_dim3(33)
    print(f"|A|={len(a)} dim2 |B|={len(b)} dim3", flush=True)
    product = [encode(x + y) for x in a for y in b]
    product = sorted(set(product))
    print(f"|A x B|={len(product)}", flush=True)
    if first_conflict(product) is not None:
        raise SystemExit("product is not independent")
    residual = residual_of(product)
    print(f"residual={len(residual)} need_extra={368 - len(product)}", flush=True)
    need = 368 - len(product)
    lines = [
        f"product {len(product)} residual {len(residual)} need {need}",
    ]
    if need <= 0:
        lines.append("product already >= 368")
        (HERE / "cegar_product_log.txt").write_text("\n".join(lines) + "\n")
        return
    if not residual:
        lines.append("empty residual; product is maximal")
        (HERE / "cegar_product_log.txt").write_text("\n".join(lines) + "\n")
        print("empty residual")
        return

    # CEGAR: SAT for `need` residual verts, add edges when a model uses them.
    lits = {v: i + 1 for i, v in enumerate(residual)}
    top_id = len(residual)
    known_edges: set[tuple[int, int]] = set()
    leftover_hist = []
    extra, top_id = atmost([-lits[v] for v in residual], len(residual) - need, top_id)
    base_clauses = list(extra)
    plateau = 0
    last_left = None
    for it in range(1, 41):
        solver = Cadical195(bootstrap_with=base_clauses)
        for u, v in known_edges:
            solver.add_clause([-lits[u], -lits[v]])
        if not solver.solve():
            lines.append(f"iter {it} UNSAT known_edges={len(known_edges)}")
            print(lines[-1], flush=True)
            break
        model = set(solver.get_model())
        chosen = [v for v in residual if lits[v] in model]
        # leftover adjacent pairs in the model
        new_edges = []
        for i, u in enumerate(chosen):
            for v in chosen[i + 1 :]:
                if adjacent(u, v):
                    e = (u, v) if u < v else (v, u)
                    if e not in known_edges:
                        new_edges.append(e)
        leftover_hist.append(len(new_edges))
        lines.append(
            f"iter {it} chosen={len(chosen)} new_edges={len(new_edges)} "
            f"known={len(known_edges)}"
        )
        print(lines[-1], flush=True)
        if not new_edges:
            T = sorted(set(product) | set(chosen))
            if first_conflict(T) is None and len(T) >= 368:
                out = HERE / f"R{len(T)}_cegar.txt"
                out.write_text("\n".join(format_word(v) for v in T) + "\n")
                lines.append(f"WROTE {out}")
                print(lines[-1])
            else:
                lines.append(f"model clean but size={len(T)} or adjacent")
            break
        known_edges.update(new_edges)
        if last_left is not None and len(new_edges) >= last_left:
            plateau += 1
        else:
            plateau = 0
        last_left = len(new_edges)
        if plateau >= 3:
            lines.append(
                f"CEGAR plateau leftover~{len(new_edges)} after {it} iters; stop"
            )
            print(lines[-1], flush=True)
            break
    lines.append(f"seconds {time.time()-t0:.1f}")
    (HERE / "cegar_product_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
