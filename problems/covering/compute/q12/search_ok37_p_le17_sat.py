#!/usr/bin/env python3
"""SAT search for minimum-p (3,ell)-partitions of OK37, focusing on p<=17.

Ostergard--Kaikkonen [37,25]_2 R=3 seed (compute/ok37_seed.py).
Uses pysat Cadical195. Reuses representation precompute / CNF ideas from
search_ok37_p17_sat.py, parameterized by P.

Monotonicity: refining blocks preserves (3,ell), so feasible p-values form
an upward-closed set {p_min,...,n} (or empty). Binary search finds p_min.

Known structural facts for this seed:
- No dependent triple => syndrome 0 has no wt2/wt3 rep => (3,ell) impossible
  for every ell>=1 and every p.
- Unique conflict edges force 15 singleton columns for ell=0 => p_min>=15.
- Prior Cadical run: exactly p=17 is UNSAT for ell=0,1,2,3.

On SAT with p<=17, writes compute/partition_H_OK37_p{P}_ell{E}.txt and
verifies with ok37_seed.is_partition_3ell.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from pysat.formula import IDPool
from pysat.solvers import Cadical195

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ok37_seed import N, R, is_partition_3ell, ok37_columns

HERE = Path(__file__).resolve().parent
SPACE = 1 << R


def precompute_reps(columns: list[int]):
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


def structural_lower_bound(wt1, wt2, wt3, ell: int) -> tuple[int, int, int]:
    """Return (n_unique_edges, n_forced_singletons, lb)."""
    edges = unique_conflict_edges(wt1, wt2, wt3, ell)
    adj = [[False] * N for _ in range(N)]
    for i, j in edges:
        adj[i][j] = adj[j][i] = True
    sings = [i for i in range(N) if sum(adj[i]) == N - 1]
    lb = len(sings) if sings else 1
    # Also: if ell>=1 and 0 has no representation at all, lb = N+1 (impossible)
    if ell >= 1:
        goods = []
        if ell <= 1 and wt1.get(0):
            goods.append("wt1")
        if ell <= 2:
            goods.extend(wt2.get(0, ()))
        goods.extend(wt3.get(0, ()))
        if not goods:
            return len(edges), len(sings), N + 1
    return len(edges), len(sings), lb


def build_solver(
    columns: list[int],
    wt1,
    wt2,
    wt3,
    ell: int,
    p: int,
    force_nonempty: bool = True,
    solver_factory=Cadical195,
):
    vpool = IDPool()
    x = [[vpool.id(("x", i, b)) for b in range(p)] for i in range(N)]
    solver = solver_factory()

    for i in range(N):
        solver.add_clause(x[i])
        for b1, b2 in combinations(range(p), 2):
            solver.add_clause([-x[i][b1], -x[i][b2]])

    if force_nonempty:
        for b in range(p):
            solver.add_clause([x[i][b] for i in range(N)])

    edges = unique_conflict_edges(wt1, wt2, wt3, ell)
    adj = [[False] * N for _ in range(N)]
    for i, j in edges:
        adj[i][j] = adj[j][i] = True
        for b in range(p):
            solver.add_clause([-x[i][b], -x[j][b]])

    sings = [i for i in range(N) if sum(adj[i]) == N - 1]
    if len(sings) > p:
        solver.add_clause([])
    else:
        for b, i in enumerate(sings):
            solver.add_clause([x[i][b]])
        if len(sings) == p - 2:
            rest = [i for i in range(N) if i not in set(sings)]
            b0, b1 = p - 2, p - 1
            for i in rest:
                for b in range(b0):
                    solver.add_clause([-x[i][b]])
                solver.add_clause([x[i][b0], x[i][b1]])
        elif len(sings) == p - 1:
            rest = [i for i in range(N) if i not in set(sings)]
            b_last = p - 1
            for i in rest:
                for b in range(b_last):
                    solver.add_clause([-x[i][b]])
                solver.add_clause([x[i][b_last]])
        elif not sings:
            solver.add_clause([x[0][0]])

    g_pair: dict[tuple[int, int], int] = {}
    g_trip: dict[tuple[int, int, int], int] = {}

    def pair_aux(i: int, j: int) -> int:
        key = (i, j) if i < j else (j, i)
        if key not in g_pair:
            g = vpool.id(("gp", key[0], key[1]))
            g_pair[key] = g
            for b in range(p):
                solver.add_clause([-g, -x[key[0]][b], -x[key[1]][b]])
        return g_pair[key]

    def trip_aux(i: int, j: int, k: int) -> int:
        key = tuple(sorted((i, j, k)))
        if key not in g_trip:
            g = vpool.id(("gt", key[0], key[1], key[2]))
            g_trip[key] = g
            a, b_, c = key
            for b in range(p):
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
        "n_edges": len(edges),
        "n_sings": len(sings),
        "x": x,
        "p": p,
    }
    return solver, meta


def extract_labels(solver, x, p: int) -> list[int]:
    model = set(solver.get_model())
    labels = []
    for i in range(N):
        assigned = [b for b in range(p) if x[i][b] in model]
        assert len(assigned) == 1, assigned
        labels.append(assigned[0])
    return labels


def write_partition(path: Path, labels: list[int], ell: int, p: int) -> list[int]:
    used = sorted(set(labels))
    assert len(used) == p, (used, p)
    remap = {old: new for new, old in enumerate(used)}
    labels = [remap[lab] for lab in labels]
    lines = [
        f"# OK37 (3,{ell})-partition into {p} blocks; labels for columns 0..36",
        "# generated by search_ok37_p_le17_sat.py",
        " ".join(str(lab) for lab in labels),
        "",
    ]
    path.write_text("\n".join(lines))
    return labels


def solve_with_timeout(solver, timeout: float | None) -> bool | None:
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


def solve_one(
    columns: list[int],
    wt1,
    wt2,
    wt3,
    ell: int,
    p: int,
    force_nonempty: bool,
    timeout: float | None,
) -> tuple[str, list[int] | None, float, dict]:
    t0 = time.perf_counter()
    # Cheap structural reject
    _ne, ns, lb = structural_lower_bound(wt1, wt2, wt3, ell)
    if p < lb:
        return "UNSAT", None, 0.0, {"n_sings": ns, "lb": lb, "nvars": 0}

    solver, meta = build_solver(
        columns, wt1, wt2, wt3, ell, p, force_nonempty=force_nonempty
    )
    build_s = time.perf_counter() - t0
    print(
        f"  ell={ell} p={p}: built CNF vars={meta['nvars']} "
        f"pair={meta['n_pair_aux']} trip={meta['n_trip_aux']} "
        f"edges={meta['n_edges']} sings={meta['n_sings']} "
        f"build={build_s:.2f}s",
        flush=True,
    )
    t1 = time.perf_counter()
    result = solve_with_timeout(solver, timeout)
    solve_s = time.perf_counter() - t1
    wall = time.perf_counter() - t0
    if result is True:
        labels = extract_labels(solver, meta["x"], p)
        solver.delete()
        print(f"  ell={ell} p={p}: SAT solve={solve_s:.2f}s", flush=True)
        return "SAT", labels, wall, meta
    solver.delete()
    if result is False:
        print(f"  ell={ell} p={p}: UNSAT solve={solve_s:.2f}s", flush=True)
        return "UNSAT", None, wall, meta
    print(f"  ell={ell} p={p}: UNKNOWN timeout solve={solve_s:.2f}s", flush=True)
    return "UNKNOWN", None, wall, meta


def check_trivial(columns: list[int]) -> dict[int, bool]:
    labels = list(range(N))
    return {ell: is_partition_3ell(columns, labels, ell) for ell in range(4)}


def binary_search_min_p(
    columns,
    wt1,
    wt2,
    wt3,
    ell: int,
    lo: int,
    hi: int,
    timeout: float | None,
    force_nonempty: bool,
    cache: dict[tuple[int, int], str],
) -> tuple[int | None, dict]:
    """Find least p in [lo,hi] with SAT, using monotonicity. None if none/unknown."""
    details: dict = {}
    # hi must be feasible (typically trivial)
    status_hi, labels_hi, wall_hi, _ = solve_one(
        columns, wt1, wt2, wt3, ell, hi, force_nonempty, timeout
    )
    cache[(ell, hi)] = status_hi
    details[hi] = {"status": status_hi, "wall": wall_hi}
    if status_hi != "SAT":
        return None, details

    best_p = hi
    best_labels = labels_hi
    low, high = lo, hi
    while low < high:
        mid = (low + high) // 2
        if (ell, mid) in cache:
            status = cache[(ell, mid)]
            wall = 0.0
            labels = None
        else:
            status, labels, wall, _ = solve_one(
                columns, wt1, wt2, wt3, ell, mid, force_nonempty, timeout
            )
            cache[(ell, mid)] = status
        details[mid] = {"status": status, "wall": wall}
        if status == "SAT":
            best_p = mid
            best_labels = labels
            high = mid
        elif status == "UNSAT":
            low = mid + 1
        else:
            # UNKNOWN: treat as soft upper search failure; probe upward
            # Keep trying larger values via raising low cautiously
            print(
                f"  ell={ell}: UNKNOWN at p={mid}; probing higher half",
                flush=True,
            )
            low = mid + 1
    details["best_labels"] = best_labels
    return best_p, details


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ells", default="0,1,2,3")
    ap.add_argument("--p-min", type=int, default=3)
    ap.add_argument("--p-max", type=int, default=37)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--no-force-nonempty", action="store_true")
    ap.add_argument(
        "--descend-le17",
        action="store_true",
        help="explicitly solve every p=17..3 for each ell (after structural skips)",
    )
    ap.add_argument(
        "--find-min",
        action="store_true",
        help="binary-search min feasible p up to --p-max for each feasible ell",
    )
    ap.add_argument("--out-dir", type=Path, default=HERE)
    ap.add_argument(
        "--results-json",
        type=Path,
        default=HERE / "ok37_p_le17_results.json",
    )
    args = ap.parse_args(argv)

    columns = ok37_columns()
    assert len(columns) == N
    print(f"OK37 n={N} r={R}", flush=True)

    t_pre = time.perf_counter()
    wt1, wt2, wt3 = precompute_reps(columns)
    print(
        f"precompute reps in {time.perf_counter() - t_pre:.2f}s "
        f"(wt1={len(wt1)} wt2={len(wt2)} wt3={len(wt3)})",
        flush=True,
    )

    trivial = check_trivial(columns)
    print("--- trivial p=37 ---", flush=True)
    for ell, ok in trivial.items():
        print(f"  (3,{ell}): {ok}", flush=True)

    ells = [int(x) for x in args.ells.split(",") if x.strip() != ""]
    force_nonempty = not args.no_force_nonempty
    timeout = args.timeout if args.timeout > 0 else None
    cache: dict[tuple[int, int], str] = {}
    summary: dict = {"trivial": {str(k): v for k, v in trivial.items()}, "ells": {}}

    # Structural bounds / impossibility
    for ell in ells:
        ne, ns, lb = structural_lower_bound(wt1, wt2, wt3, ell)
        print(
            f"ell={ell}: unique_edges={ne} forced_singletons={ns} "
            f"structural_lb={lb}"
            + (" (IMPOSSIBLE: no rep of 0)" if lb > N else ""),
            flush=True,
        )
        summary["ells"][str(ell)] = {
            "structural_lb": lb,
            "forced_singletons": ns,
            "unique_edges": ne,
            "trivial": trivial.get(ell),
            "by_p": {},
        }

    # Explicit p=17..3 sweep if requested (or by default for le17 table)
    p_lo = max(args.p_min, 3)
    p_hi_le17 = min(args.p_max, 17)
    do_descend = args.descend_le17 or True  # always fill the le17 table
    if do_descend:
        print(f"--- descend/table p={p_hi_le17}..{p_lo} ---", flush=True)
        for ell in ells:
            lb = summary["ells"][str(ell)]["structural_lb"]
            if lb > N:
                for p in range(p_lo, p_hi_le17 + 1):
                    summary["ells"][str(ell)]["by_p"][str(p)] = "UNSAT"
                    cache[(ell, p)] = "UNSAT"
                print(
                    f"ell={ell}: all p<={p_hi_le17} UNSAT (no representation of 0)",
                    flush=True,
                )
                summary["ells"][str(ell)]["min_p"] = None
                summary["ells"][str(ell)]["min_p_note"] = "impossible for all p"
                continue
            for p in range(p_hi_le17, p_lo - 1, -1):
                if p < lb:
                    cache[(ell, p)] = "UNSAT"
                    summary["ells"][str(ell)]["by_p"][str(p)] = "UNSAT"
                    print(f"  ell={ell} p={p}: UNSAT (p < structural_lb={lb})", flush=True)
                    continue
                if (ell, p) in cache:
                    summary["ells"][str(ell)]["by_p"][str(p)] = cache[(ell, p)]
                    continue
                status, labels, wall, _ = solve_one(
                    columns, wt1, wt2, wt3, ell, p, force_nonempty, timeout
                )
                cache[(ell, p)] = status
                summary["ells"][str(ell)]["by_p"][str(p)] = status
                summary["ells"][str(ell)].setdefault("times", {})[str(p)] = wall
                if status == "SAT" and labels is not None:
                    assert len(set(labels)) == p
                    ok = is_partition_3ell(columns, labels, ell)
                    print(
                        f"  verify is_partition_3ell(..., ell={ell}) -> {ok}",
                        flush=True,
                    )
                    if not ok:
                        cache[(ell, p)] = "SAT_BUT_VERIFY_FAIL"
                        summary["ells"][str(ell)]["by_p"][str(p)] = cache[(ell, p)]
                        continue
                    out = args.out_dir / f"partition_H_OK37_p{p}_ell{ell}.txt"
                    labels = write_partition(out, labels, ell, p)
                    print(f"  wrote {out}", flush=True)
                    summary["ells"][str(ell)]["certificate"] = str(out)
                    summary["ells"][str(ell)]["min_p_le17"] = p
                    # smaller p may still exist; continue descending
                # If UNSAT at p, all smaller are UNSAT by refinement contrappositive
                # only when we required exactly-p nonempty AND refinement works.
                # Refinement: SAT at q<p => SAT at p by splitting. Contrapositive:
                # UNSAT at p => UNSAT at all q<p. Safe to mark and break.
                if status == "UNSAT":
                    for q in range(p_lo, p):
                        cache[(ell, q)] = "UNSAT"
                        summary["ells"][str(ell)]["by_p"][str(q)] = "UNSAT"
                    print(
                        f"  ell={ell}: UNSAT at p={p} => all q<{p} UNSAT "
                        f"(refinement contrappositive)",
                        flush=True,
                    )
                    break

    # Binary search for true min p (may be >17)
    if args.find_min:
        print(f"--- binary search min p in [{args.p_min},{args.p_max}] ---", flush=True)
        for ell in ells:
            lb = summary["ells"][str(ell)]["structural_lb"]
            if lb > N:
                print(f"ell={ell}: impossible", flush=True)
                continue
            if not trivial.get(ell, False) and args.p_max < N:
                # need a feasible upper end; try p_max first
                pass
            lo = max(args.p_min, lb)
            hi = args.p_max
            # Ensure hi is SAT: if trivial and hi==N ok; else solve hi
            if hi == N and trivial.get(ell):
                cache[(ell, hi)] = "SAT"
            min_p, details = binary_search_min_p(
                columns,
                wt1,
                wt2,
                wt3,
                ell,
                lo,
                hi,
                timeout,
                force_nonempty,
                cache,
            )
            summary["ells"][str(ell)]["min_p_search"] = min_p
            summary["ells"][str(ell)]["search_details"] = {
                str(k): v
                for k, v in details.items()
                if k != "best_labels"
            }
            print(f"ell={ell}: min_p={min_p}", flush=True)
            if min_p is not None and min_p <= 17:
                labels = details.get("best_labels")
                if labels is not None:
                    out = args.out_dir / f"partition_H_OK37_p{min_p}_ell{ell}.txt"
                    write_partition(out, labels, ell, min_p)
                    assert is_partition_3ell(columns, labels, ell)
                    print(f"  wrote {out}", flush=True)

    # Final table
    print("--- summary table ---", flush=True)
    print(
        f"{'ell':>4} {'trivial':>8} {'lb':>4} {'min_p':>8} "
        f"{'p<=17?':>8} {'QM_4^3 m=4':>12}"
    )
    for ell in ells:
        info = summary["ells"][str(ell)]
        lb = info["structural_lb"]
        # Determine min_p / bound from by_p and search
        min_p = info.get("min_p_search")
        note = ""
        if info.get("min_p_note"):
            min_p_disp = "none"
            note = info["min_p_note"]
            qm = "no"
        elif min_p is not None:
            min_p_disp = str(min_p)
            qm = "yes" if min_p <= 17 else "no"
        else:
            # infer from by_p: if all <=17 UNSAT, lb_min > 17
            statuses = [info["by_p"].get(str(p)) for p in range(p_lo, p_hi_le17 + 1)]
            if statuses and all(s == "UNSAT" for s in statuses):
                min_p_disp = f">={max(18, lb)}"
                qm = "no"
            else:
                min_p_disp = "?"
                qm = "?"
        print(
            f"{ell:>4} {str(trivial.get(ell)):>8} {lb:>4} {min_p_disp:>8} "
            f"{'yes' if (isinstance(min_p, int) and min_p <= 17) else 'no':>8} "
            f"{qm:>12}"
            + (f"  ({note})" if note else "")
        )

    args.results_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.results_json}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
