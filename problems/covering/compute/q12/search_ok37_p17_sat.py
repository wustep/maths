#!/usr/bin/env python3
"""SAT search for a 17-block (3,ell)-partition of OK37.

Ostergard--Kaikkonen [37,25]_2 R=3 seed (compute/ok37_seed.py).
Uses pysat Cadical195. Tries ell=0 first (enough for QM_4^3), then 1,2,3.
Also runs a short Metropolis (3,0) backup.

On SAT, writes compute/partition_H_OK37_p17.txt and verifies with
ok37_seed.is_partition_3ell.
"""
from __future__ import annotations

import argparse
import random
import sys
import threading
import time
from collections import defaultdict, deque
from itertools import combinations, product
from pathlib import Path

from pysat.formula import IDPool
from pysat.solvers import Cadical195

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ok37_seed import N, R, is_partition_3ell, ok37_columns

HERE = Path(__file__).resolve().parent
OUT_PATH = HERE / "partition_H_OK37_p17.txt"
P = 17
SPACE = 1 << R


def precompute_reps(columns: list[int]):
    """Map syndrome -> lists of wt1 / wt2 / wt3 column-index tuples."""
    wt1: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    wt2: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    wt3: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for i, c in enumerate(columns):
        wt1[c].append((i,))
    for i, j in combinations(range(N), 2):
        wt2[columns[i] ^ columns[j]].append((i, j))
    for i, j, k in combinations(range(N), 3):
        wt3[columns[i] ^ columns[j] ^ columns[k]].append((i, j, k))
    return wt1, wt2, wt3


def unique_conflict_edges(wt1, wt2, wt3, ell: int) -> list[tuple[int, int]]:
    """Edges that must receive distinct blocks from unique necessary reps."""
    edges = set()
    for s in range(SPACE):
        goods: list[tuple[int, ...]] = []
        if ell == 0 and s == 0:
            continue
        if ell <= 1 and wt1.get(s):
            continue
        if ell <= 2:
            goods.extend(wt2.get(s, ()))
        goods.extend(wt3.get(s, ()))
        if len(goods) != 1:
            continue
        rep = goods[0]
        if len(rep) == 2:
            i, j = rep
            edges.add((i, j) if i < j else (j, i))
        elif len(rep) == 3:
            for a, b in combinations(rep, 2):
                edges.add((a, b) if a < b else (b, a))
    return sorted(edges)


def structural_ell0_unsat(columns, wt1, wt2, wt3) -> tuple[bool, str]:
    """Enumerate all conflict-respecting 17-blockings for ell=0; prove UNSAT if none work."""
    # Build conflict adj from unique wt3-only syndromes
    adj = [[False] * N for _ in range(N)]
    for s in range(SPACE):
        if s == 0 or wt1.get(s) or wt2.get(s):
            continue
        reps = wt3.get(s, ())
        if len(reps) != 1:
            continue
        i, j, k = reps[0]
        for a, b in ((i, j), (i, k), (j, k)):
            adj[a][b] = adj[b][a] = True
    singletons = [i for i in range(N) if sum(adj[i]) == N - 1]
    if len(singletons) != 15:
        return False, f"unexpected singleton count {len(singletons)}"
    rest = [i for i in range(N) if i not in set(singletons)]
    if len(rest) != 22:
        return False, f"unexpected rest count {len(rest)}"
    # With p=17, the 15 singletons consume 15 blocks; rest must use exactly 2.
    seen: set[int] = set()
    comps: list[list[int]] = []
    for start in rest:
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        comp: list[int] = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in rest:
                if adj[u][v] and v not in seen:
                    seen.add(v)
                    q.append(v)
        comps.append(sorted(comp))

    sides_list: list[tuple[list[int], list[int]]] = []
    free: list[int] = []
    for comp in comps:
        n_edges = sum(1 for a, b in combinations(comp, 2) if adj[a][b])
        if n_edges == 0:
            free.extend(comp)
            continue
        color: dict[int, int] = {comp[0]: 0}
        q = deque([comp[0]])
        while q:
            u = q.popleft()
            for v in comp:
                if not adj[u][v]:
                    continue
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return True, "conflict graph not bipartite => UNSAT"
        side0 = [v for v in comp if color[v] == 0]
        side1 = [v for v in comp if color[v] == 1]
        sides_list.append((side0, side1))

    best = 0
    n_ok = 0
    for flips in product([0, 1], repeat=len(sides_list)):
        for free_assign in product([0, 1], repeat=len(free)):
            block_of: dict[int, int] = {}
            for (side0, side1), fl in zip(sides_list, flips):
                for v in side0:
                    block_of[v] = 15 if fl == 0 else 16
                for v in side1:
                    block_of[v] = 16 if fl == 0 else 15
            for v, a in zip(free, free_assign):
                block_of[v] = 15 if a == 0 else 16
            if set(block_of.values()) != {15, 16}:
                continue
            labels = [0] * N
            for b, i in enumerate(singletons):
                labels[i] = b
            for i, b in block_of.items():
                labels[i] = b
            if is_partition_3ell(columns, labels, 0):
                n_ok += 1
            else:
                # cheap coverage score
                covered = bytearray(SPACE)
                covered[0] = 1
                for c in columns:
                    covered[c] = 1
                for i, j in combinations(range(N), 2):
                    if labels[i] != labels[j]:
                        covered[columns[i] ^ columns[j]] = 1
                for i, j, k in combinations(range(N), 3):
                    if len({labels[i], labels[j], labels[k]}) == 3:
                        covered[columns[i] ^ columns[j] ^ columns[k]] = 1
                best = max(best, sum(covered))
    if n_ok:
        return False, f"structural found {n_ok} partitions (unexpected)"
    return (
        True,
        f"enumerated all conflict-respecting 17-blockings; none cover "
        f"(best {best}/{SPACE}; edged_comps={len(sides_list)} free={len(free)})",
    )


def build_solver(
    columns: list[int],
    wt1,
    wt2,
    wt3,
    ell: int,
    force_nonempty: bool = True,
):
    """Encode column->block assignment + syndrome covering for given ell."""
    vpool = IDPool()
    x = [[vpool.id(("x", i, b)) for b in range(P)] for i in range(N)]
    solver = Cadical195()

    for i in range(N):
        solver.add_clause(x[i])
        for b1, b2 in combinations(range(P), 2):
            solver.add_clause([-x[i][b1], -x[i][b2]])

    if force_nonempty:
        for b in range(P):
            solver.add_clause([x[i][b] for i in range(N)])

    # Hard conflict edges from unique representations
    edges = unique_conflict_edges(wt1, wt2, wt3, ell)
    adj = [[False] * N for _ in range(N)]
    for i, j in edges:
        adj[i][j] = adj[j][i] = True
        for b in range(P):
            solver.add_clause([-x[i][b], -x[j][b]])

    # Columns adjacent to all others must be singleton blocks.
    # Pin them to the first len(sings) block ids to collapse symmetry.
    sings = [i for i in range(N) if sum(adj[i]) == N - 1]
    if len(sings) > P:
        solver.add_clause([])  # impossible
    else:
        for b, i in enumerate(sings):
            solver.add_clause([x[i][b]])
        if len(sings) == P - 2:
            # Remaining columns must occupy the last two blocks only.
            rest = [i for i in range(N) if i not in set(sings)]
            b0, b1 = P - 2, P - 1
            for i in rest:
                for b in range(b0):
                    solver.add_clause([-x[i][b]])
                solver.add_clause([x[i][b0], x[i][b1]])
        elif not sings:
            # Mild symmetry break when no forced singletons.
            solver.add_clause([x[0][0]])

    g_pair: dict[tuple[int, int], int] = {}
    g_trip: dict[tuple[int, int, int], int] = {}

    def pair_aux(i: int, j: int) -> int:
        key = (i, j) if i < j else (j, i)
        if key not in g_pair:
            g = vpool.id(("gp", key[0], key[1]))
            g_pair[key] = g
            for b in range(P):
                solver.add_clause([-g, -x[key[0]][b], -x[key[1]][b]])
        return g_pair[key]

    def trip_aux(i: int, j: int, k: int) -> int:
        key = tuple(sorted((i, j, k)))
        if key not in g_trip:
            g = vpool.id(("gt", key[0], key[1], key[2]))
            g_trip[key] = g
            a, b_, c = key
            for b in range(P):
                solver.add_clause([-g, -x[a][b], -x[b_][b]])
                solver.add_clause([-g, -x[a][b], -x[c][b]])
                solver.add_clause([-g, -x[b_][b], -x[c][b]])
        return g_trip[key]

    n_cover = 0
    for s in range(SPACE):
        goods: list[int] = []
        if ell == 0 and s == 0:
            continue
        if ell <= 1 and wt1.get(s):
            continue
        if ell <= 2:
            for i, j in wt2.get(s, ()):
                goods.append(pair_aux(i, j))
        for trip in wt3.get(s, ()):
            goods.append(trip_aux(*trip))
        if not goods:
            solver.add_clause([])
            n_cover += 1
            continue
        solver.add_clause(goods)
        n_cover += 1

    meta = {
        "nvars": vpool.top,
        "n_pair_aux": len(g_pair),
        "n_trip_aux": len(g_trip),
        "n_cover": n_cover,
        "x": x,
    }
    return solver, meta


def extract_labels(solver, x) -> list[int]:
    model = set(solver.get_model())
    labels = []
    for i in range(N):
        assigned = [b for b in range(P) if x[i][b] in model]
        assert len(assigned) == 1, assigned
        labels.append(assigned[0])
    return labels


def write_partition(path: Path, labels: list[int], ell: int) -> None:
    used = sorted(set(labels))
    assert len(used) == P, used
    # renormalize to 0..P-1
    remap = {old: new for new, old in enumerate(used)}
    labels = [remap[lab] for lab in labels]
    lines = [
        f"# OK37 (3,{ell})-partition into {P} blocks; labels for columns 0..36",
        "# generated by search_ok37_p17_sat.py",
        " ".join(str(lab) for lab in labels),
        "",
    ]
    path.write_text("\n".join(lines))


def solve_with_timeout(solver, timeout: float | None) -> bool | None:
    """Return True/False/None(UNKNOWN on timeout)."""
    if timeout is None or timeout <= 0:
        return solver.solve()

    outcome: dict[str, bool | None] = {"res": None}
    done = threading.Event()

    def _run() -> None:
        try:
            outcome["res"] = solver.solve()
        finally:
            done.set()

    th = threading.Thread(target=_run, daemon=True)
    th.start()
    if done.wait(timeout):
        return outcome["res"]
    solver.interrupt()
    done.wait(5.0)
    solver.clear_interrupt()
    return None


def solve_ell(
    columns: list[int],
    wt1,
    wt2,
    wt3,
    ell: int,
    force_nonempty: bool,
    timeout: float | None,
) -> tuple[str, list[int] | None, float, dict]:
    t0 = time.perf_counter()
    solver, meta = build_solver(
        columns, wt1, wt2, wt3, ell, force_nonempty=force_nonempty
    )
    build_s = time.perf_counter() - t0
    print(
        f"  ell={ell}: built CNF vars={meta['nvars']} "
        f"pair_aux={meta['n_pair_aux']} trip_aux={meta['n_trip_aux']} "
        f"cover={meta['n_cover']} build={build_s:.2f}s",
        flush=True,
    )
    t1 = time.perf_counter()
    result = solve_with_timeout(solver, timeout)
    solve_s = time.perf_counter() - t1
    wall = time.perf_counter() - t0
    if result is True:
        labels = extract_labels(solver, meta["x"])
        solver.delete()
        print(f"  ell={ell}: SAT solve={solve_s:.2f}s", flush=True)
        return "SAT", labels, wall, meta
    solver.delete()
    if result is False:
        print(f"  ell={ell}: UNSAT solve={solve_s:.2f}s", flush=True)
        return "UNSAT", None, wall, meta
    print(f"  ell={ell}: UNKNOWN (timeout) solve={solve_s:.2f}s", flush=True)
    return "UNKNOWN", None, wall, meta


def partition_energy(labels: list[int], columns: list[int], ell: int = 0) -> int:
    covered = bytearray(SPACE)
    if ell == 0:
        covered[0] = 1
    if ell <= 1:
        for c in columns:
            covered[c] = 1
    if ell <= 2:
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
    return SPACE - sum(covered)


def metropolis_30(
    columns: list[int],
    steps: int,
    seed: int,
    n_colors: int = P,
) -> tuple[list[int] | None, int, float]:
    t0 = time.perf_counter()
    rng = random.Random(seed)
    labels = [i % n_colors for i in range(N)]
    rng.shuffle(labels)
    for b in range(min(n_colors, N)):
        labels[b] = b
    energy = partition_energy(labels, columns, ell=0)
    best_e = energy
    best = list(labels)
    print(f"  metropolis start energy={energy}", flush=True)
    for step in range(steps):
        v = rng.randrange(N)
        old = labels[v]
        new = rng.randrange(n_colors)
        if new == old:
            continue
        if sum(1 for lab in labels if lab == old) == 1:
            continue
        labels[v] = new
        nxt = partition_energy(labels, columns, ell=0)
        if nxt <= energy or rng.random() < 0.03:
            energy = nxt
            if energy < best_e:
                best_e = energy
                best = list(labels)
                if step < 100 or step % 200 == 0 or best_e == 0:
                    print(f"  metropolis step={step} best={best_e}", flush=True)
        else:
            labels[v] = old
        if best_e == 0:
            break
    wall = time.perf_counter() - t0
    return (best if best_e == 0 else None), best_e, wall


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ells", default="0,1,2,3")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--no-force-nonempty", action="store_true")
    ap.add_argument("--metropolis-steps", type=int, default=3000)
    ap.add_argument("--metropolis-seed", type=int, default=0)
    ap.add_argument("--output", type=Path, default=OUT_PATH)
    ap.add_argument(
        "--skip-structural",
        action="store_true",
        help="skip ell=0 structural UNSAT enumeration",
    )
    args = ap.parse_args(argv)

    columns = ok37_columns()
    assert len(columns) == N
    print(f"OK37 n={N} r={R} p={P}", flush=True)

    t_pre = time.perf_counter()
    wt1, wt2, wt3 = precompute_reps(columns)
    print(
        f"precompute reps in {time.perf_counter() - t_pre:.2f}s "
        f"(wt1 keys={len(wt1)} wt2={len(wt2)} wt3={len(wt3)})",
        flush=True,
    )

    results: dict[object, str] = {}
    times: dict[object, float] = {}
    found_labels: list[int] | None = None
    found_ell: int | None = None

    ells = [int(x) for x in args.ells.split(",") if x.strip() != ""]
    force_nonempty = not args.no_force_nonempty
    timeout = args.timeout if args.timeout > 0 else None

    if 0 in ells and not args.skip_structural:
        t0 = time.perf_counter()
        unsat, msg = structural_ell0_unsat(columns, wt1, wt2, wt3)
        wall = time.perf_counter() - t0
        times["structural0"] = wall
        print(f"structural ell=0: {msg} ({wall:.3f}s)", flush=True)
        if unsat:
            results[0] = "UNSAT"
            times[0] = wall
            # ell=1 is stricter (0 must be a distinct-block triple)
            if 1 in ells:
                results[1] = "UNSAT"
                times[1] = 0.0
                print(
                    "ell=1: UNSAT (inherits ell=0 unique-triple forcing; "
                    "stricter on syndrome 0)",
                    flush=True,
                )

    for ell in ells:
        if ell in results:
            continue
        status, labels, wall, _meta = solve_ell(
            columns, wt1, wt2, wt3, ell, force_nonempty, timeout
        )
        results[ell] = status
        times[ell] = wall
        print(f"  ell={ell}: {status} wall={wall:.2f}s", flush=True)
        if status == "SAT" and labels is not None:
            # renormalize / ensure P labels
            if len(set(labels)) != P:
                results[ell] = "SAT_WRONG_P"
                continue
            ok = is_partition_3ell(columns, labels, ell)
            print(f"  verify is_partition_3ell(..., ell={ell}) -> {ok}", flush=True)
            if not ok:
                results[ell] = "SAT_BUT_VERIFY_FAIL"
                continue
            found_labels = labels
            found_ell = ell
            write_partition(args.output, labels, ell)
            print(f"  wrote {args.output}", flush=True)
            break

    if found_labels is None and args.metropolis_steps > 0:
        print(
            f"Metropolis (3,0) backup steps={args.metropolis_steps} "
            f"seed={args.metropolis_seed}",
            flush=True,
        )
        labels, best_e, wall = metropolis_30(
            columns, steps=args.metropolis_steps, seed=args.metropolis_seed
        )
        print(f"  metropolis best_energy={best_e} wall={wall:.2f}s", flush=True)
        times["metropolis"] = wall
        if labels is not None:
            assert is_partition_3ell(columns, labels, 0)
            found_labels = labels
            found_ell = 0
            results["metropolis"] = "SAT"
            write_partition(args.output, labels, 0)
            print(f"  wrote {args.output}", flush=True)
        else:
            results["metropolis"] = f"FAIL energy={best_e}"

    print("--- summary ---", flush=True)
    for ell in ells:
        print(
            f"ell={ell}: {results.get(ell, 'skipped')} "
            f"({times.get(ell, 0):.2f}s)"
        )
    if "metropolis" in results:
        print(
            f"metropolis: {results['metropolis']} "
            f"({times.get('metropolis', 0):.2f}s)"
        )
    if found_labels is not None:
        print(f"FOUND ell={found_ell} path={args.output}")
        print("labels:", " ".join(map(str, found_labels)))
        return 0
    print("NO PARTITION FOUND")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
