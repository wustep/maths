#!/usr/bin/env python3
"""Q2 search from a genuinely different almost-symmetric template.

The q1 near-coloring respects reflection about 1698 except at the mandatory
pair 566/1132.  Its two defects use the two additional reflection pairs
537/1161 and 624/1074.  This program can split any chosen list of such pairs,
then run a compiled weighted tabu/min-conflicts search on the resulting orbit
hypergraph.  It can also start from a unit-multiplier copy of the independently
verified cyclic coloring of Z/1681Z, instead of the Fredricksen--Sweet seed
used in q1.

Every SAT return is expanded to the actual interval and checked by the simple
integer-triple verifier imported from search_shifted_sat.py.  A separate
verifier is still required before a result is reported as a witness.
"""

from __future__ import annotations

import argparse
import json
from math import gcd
from pathlib import Path
from time import monotonic

import numpy as np
from numba import njit

from search_almost_symmetric_pysat import old_coloring
from search_shifted_sat import verify


def parse_representatives(raw: str) -> tuple[int, ...]:
    if not raw.strip():
        return ()
    values = tuple(sorted({int(token) for token in raw.split(",")}))
    if any(value < 1 for value in values):
        raise ValueError("split representatives must be positive")
    return values


def build(
    target: int, extra_split_representatives: tuple[int, ...]
) -> tuple[list[int], list[tuple[int, ...]], list[int]]:
    """Return orbit labels, folded Schur edges, and the point-to-orbit map."""
    center = target + 1
    split_points: set[int] = set()
    if center % 3 == 0:
        split_points.update((center // 3, 2 * center // 3))
    for representative in extra_split_representatives:
        mate = center - representative
        if not (1 <= representative <= target and 1 <= mate <= target):
            raise ValueError(f"split representative {representative} is outside [1,{target}]")
        split_points.update((representative, mate))

    def label(x: int) -> int:
        return x if x in split_points else min(x, center - x)

    labels = sorted({label(x) for x in range(1, target + 1)})
    label_index = {value: position for position, value in enumerate(labels)}
    point_orbit = [-1] + [label_index[label(x)] for x in range(1, target + 1)]

    edge_set: set[tuple[int, ...]] = set()
    for x in range(1, target + 1):
        for y in range(x, target - x + 1):
            edge_set.add(
                tuple(
                    sorted(
                        {
                            point_orbit[x],
                            point_orbit[y],
                            point_orbit[x + y],
                        }
                    )
                )
            )
    edges = sorted(edge_set)
    singleton = next((edge for edge in edges if len(edge) == 1), None)
    if singleton is not None:
        raise ValueError(f"template forces a monochromatic singleton edge {singleton}")
    return labels, edges, point_orbit


def phase_from_file(
    path: Path, target: int, labels: list[int], point_orbit: list[int]
) -> np.ndarray:
    tokens = path.read_text(encoding="ascii").split()
    if len(tokens) != target:
        raise ValueError(f"expected {target} colors in {path}, found {len(tokens)}")
    point_colors = [-1] + [int(token) for token in tokens]
    if any(color not in range(7) for color in point_colors[1:]):
        raise ValueError("phase colors must lie in 0..6")
    assignment = np.full(len(labels), -1, dtype=np.int8)
    for x in range(1, target + 1):
        orbit = point_orbit[x]
        color = point_colors[x]
        if assignment[orbit] == -1:
            assignment[orbit] = color
        elif assignment[orbit] != color:
            raise ValueError(
                f"phase {path} disagrees inside an unsplit reflection orbit at {x}"
            )
    return assignment


def phase_from_cyclic_multiplier(labels: list[int], multiplier: int) -> np.ndarray:
    if gcd(multiplier, 1681) != 1:
        raise ValueError("cyclic phase multiplier must be a unit modulo 1681")
    old = old_coloring()
    return np.asarray(
        [old[(multiplier * label) % 1681] for label in labels], dtype=np.int8
    )


def arrays(
    vertex_count: int, edges: list[tuple[int, ...]]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    padded = np.full((len(edges), 3), -1, dtype=np.int32)
    sizes = np.empty(len(edges), dtype=np.int8)
    degrees = np.zeros(vertex_count, dtype=np.int32)
    for eid, edge in enumerate(edges):
        sizes[eid] = len(edge)
        for offset, vertex in enumerate(edge):
            padded[eid, offset] = vertex
            degrees[vertex] += 1
    starts = np.empty(vertex_count + 1, dtype=np.int32)
    starts[0] = 0
    np.cumsum(degrees, out=starts[1:])
    incident = np.empty(int(starts[-1]), dtype=np.int32)
    cursor = starts[:-1].copy()
    for eid, edge in enumerate(edges):
        for vertex in edge:
            incident[cursor[vertex]] = eid
            cursor[vertex] += 1
    return padded, starts, incident


@njit(cache=True)
def edge_bad(edge_vertices: np.ndarray, assignment: np.ndarray, eid: int) -> bool:
    first = edge_vertices[eid, 0]
    second = edge_vertices[eid, 1]
    if assignment[first] != assignment[second]:
        return False
    third = edge_vertices[eid, 2]
    return third < 0 or assignment[first] == assignment[third]


@njit(cache=True)
def edge_bad_after(
    edge_vertices: np.ndarray,
    assignment: np.ndarray,
    eid: int,
    changed_vertex: int,
    changed_color: int,
) -> bool:
    first = edge_vertices[eid, 0]
    second = edge_vertices[eid, 1]
    first_color = changed_color if first == changed_vertex else assignment[first]
    second_color = changed_color if second == changed_vertex else assignment[second]
    if first_color != second_color:
        return False
    third = edge_vertices[eid, 2]
    if third < 0:
        return True
    third_color = changed_color if third == changed_vertex else assignment[third]
    return first_color == third_color


@njit(cache=True)
def tabu_search(
    initial: np.ndarray,
    edge_vertices: np.ndarray,
    incident_starts: np.ndarray,
    incident_edges: np.ndarray,
    move_limit: int,
    random_seed: int,
    breakout_after: int,
    noise_numerator: int,
    noise_denominator: int,
) -> tuple[np.ndarray, int, int, int]:
    """Return best assignment, best bad-edge count, moves used, breakouts."""
    np.random.seed(random_seed)
    assignment = initial.copy()
    edge_count = edge_vertices.shape[0]
    vertex_count = assignment.shape[0]
    weights = np.ones(edge_count, dtype=np.int32)
    bad_ids = np.empty(edge_count, dtype=np.int32)
    bad_position = np.full(edge_count, -1, dtype=np.int32)
    bad_count = 0
    for eid in range(edge_count):
        if edge_bad(edge_vertices, assignment, eid):
            bad_position[eid] = bad_count
            bad_ids[bad_count] = eid
            bad_count += 1

    best = assignment.copy()
    best_bad = bad_count
    tabu_until = np.zeros((vertex_count, 7), dtype=np.int64)
    plateau = 0
    breakouts = 0

    candidate_delta = np.empty(21, dtype=np.int64)
    candidate_vertex = np.empty(21, dtype=np.int32)
    candidate_color = np.empty(21, dtype=np.int8)

    for move in range(1, move_limit + 1):
        if bad_count == 0:
            return assignment, 0, move - 1, breakouts

        chosen_bad = bad_ids[np.random.randint(bad_count)]
        candidate_count = 0
        fallback_count = 0
        for slot in range(3):
            vertex = edge_vertices[chosen_bad, slot]
            if vertex < 0:
                continue
            old_color = assignment[vertex]
            for color in range(7):
                if color == old_color:
                    continue
                delta = 0
                for position in range(
                    incident_starts[vertex], incident_starts[vertex + 1]
                ):
                    eid = incident_edges[position]
                    was_bad = bad_position[eid] >= 0
                    now_bad = edge_bad_after(
                        edge_vertices, assignment, eid, vertex, color
                    )
                    if was_bad and not now_bad:
                        delta -= weights[eid]
                    elif not was_bad and now_bad:
                        delta += weights[eid]
                candidate_delta[fallback_count] = delta
                candidate_vertex[fallback_count] = vertex
                candidate_color[fallback_count] = color
                fallback_count += 1
                if tabu_until[vertex, color] <= move:
                    candidate_count = fallback_count

        # Pack the non-tabu candidates.  The small fixed buffer keeps this
        # branch cheaper than allocating a Python list on every move.
        if candidate_count:
            write = 0
            for read in range(fallback_count):
                vertex = candidate_vertex[read]
                color = candidate_color[read]
                if tabu_until[vertex, color] <= move:
                    candidate_delta[write] = candidate_delta[read]
                    candidate_vertex[write] = vertex
                    candidate_color[write] = color
                    write += 1
            candidate_count = write
        else:
            candidate_count = fallback_count

        if (
            noise_numerator > 0
            and np.random.randint(noise_denominator) < noise_numerator
        ):
            choice = np.random.randint(candidate_count)
        else:
            minimum = candidate_delta[0]
            tie_count = 1
            choice = 0
            for index in range(1, candidate_count):
                delta = candidate_delta[index]
                if delta < minimum:
                    minimum = delta
                    tie_count = 1
                    choice = index
                elif delta == minimum:
                    tie_count += 1
                    if np.random.randint(tie_count) == 0:
                        choice = index

        vertex = candidate_vertex[choice]
        new_color = candidate_color[choice]
        old_color = assignment[vertex]
        assignment[vertex] = new_color
        for position in range(incident_starts[vertex], incident_starts[vertex + 1]):
            eid = incident_edges[position]
            was_bad = bad_position[eid] >= 0
            now_bad = edge_bad(edge_vertices, assignment, eid)
            if was_bad and not now_bad:
                removed_position = bad_position[eid]
                bad_count -= 1
                last_eid = bad_ids[bad_count]
                bad_ids[removed_position] = last_eid
                bad_position[last_eid] = removed_position
                bad_position[eid] = -1
            elif not was_bad and now_bad:
                bad_position[eid] = bad_count
                bad_ids[bad_count] = eid
                bad_count += 1
        tabu_until[vertex, old_color] = move + 5 + np.random.randint(8)

        if bad_count < best_bad:
            best_bad = bad_count
            best[:] = assignment
            plateau = 0
        else:
            plateau += 1

        if plateau >= breakout_after and bad_count:
            for position in range(bad_count):
                weights[bad_ids[position]] += 1
            plateau = 0
            breakouts += 1

    return best, best_bad, move_limit, breakouts


def count_bad(assignment: np.ndarray, edges: list[tuple[int, ...]]) -> int:
    return sum(len({int(assignment[vertex]) for vertex in edge}) == 1 for edge in edges)


def expand(
    assignment: np.ndarray, target: int, point_orbit: list[int]
) -> list[int]:
    return [-1] + [int(assignment[point_orbit[x]]) for x in range(1, target + 1)]


def perturb(assignment: np.ndarray, changes: int, rng: np.random.Generator) -> np.ndarray:
    result = assignment.copy()
    for vertex in rng.choice(len(result), size=min(changes, len(result)), replace=False):
        old = int(result[vertex])
        color = int(rng.integers(6))
        if color >= old:
            color += 1
        result[vertex] = color
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1697)
    parser.add_argument(
        "--split-reps",
        default="537,624",
        help="comma-separated low representatives of extra reflection pairs to split",
    )
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument("--phase-file", type=Path)
    phase.add_argument("--cyclic-multiplier", type=int)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--moves-per-restart", type=int, default=1_000_000)
    parser.add_argument("--breakout-after", type=int, default=10_000)
    parser.add_argument("--perturb", type=int, default=12)
    parser.add_argument("--random-seed", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--best-output", type=Path)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()

    split_reps = parse_representatives(args.split_reps)
    labels, edges, point_orbit = build(args.target, split_reps)
    if args.phase_file is not None:
        initial = phase_from_file(args.phase_file, args.target, labels, point_orbit)
        phase_description = str(args.phase_file)
    else:
        initial = phase_from_cyclic_multiplier(labels, args.cyclic_multiplier)
        phase_description = f"cyclic-1680-multiplier-{args.cyclic_multiplier}"

    edge_vertices, incident_starts, incident_edges = arrays(len(labels), edges)
    initial_bad = count_bad(initial, edges)
    started = monotonic()
    deadline = started + args.seconds
    rng = np.random.default_rng(args.random_seed)
    global_best = initial.copy()
    global_best_bad = initial_bad
    restart = 0
    total_moves = 0
    total_breakouts = 0
    events: list[dict[str, int | float | str]] = []

    encoding_event: dict[str, int | float | str] = {
        "event": "encoding",
        "target": args.target,
        "center": args.target + 1,
        "extra_split_representatives": ",".join(map(str, split_reps)) or "none",
        "orbit_variables": len(labels),
        "orbit_edges": len(edges),
        "phase": phase_description,
        "initial_violations": initial_bad,
        "random_seed": args.random_seed,
    }
    print(json.dumps(encoding_event, sort_keys=True), flush=True)
    events.append(encoding_event)

    while monotonic() < deadline and global_best_bad:
        restart += 1
        if restart == 1:
            restart_assignment = initial
        else:
            restart_assignment = perturb(global_best, args.perturb, rng)
        best, best_bad, moves, breakouts = tabu_search(
            restart_assignment,
            edge_vertices,
            incident_starts,
            incident_edges,
            args.moves_per_restart,
            args.random_seed + 1_000_003 * restart,
            args.breakout_after,
            15,
            1000,
        )
        total_moves += moves
        total_breakouts += breakouts
        if best_bad < global_best_bad:
            global_best = best.copy()
            global_best_bad = best_bad
        event: dict[str, int | float | str] = {
            "event": "restart",
            "restart": restart,
            "restart_best_violations": best_bad,
            "global_best_violations": global_best_bad,
            "moves": moves,
            "total_moves": total_moves,
            "breakouts": breakouts,
            "elapsed_seconds": round(monotonic() - started, 6),
        }
        print(json.dumps(event, sort_keys=True), flush=True)
        events.append(event)

    result = "sat" if global_best_bad == 0 else "timeout"
    stats: dict[str, int | float | str] = {
        "event": "result",
        "result": result,
        "target": args.target,
        "extra_split_representatives": ",".join(map(str, split_reps)) or "none",
        "orbit_variables": len(labels),
        "orbit_edges": len(edges),
        "phase": phase_description,
        "initial_violations": initial_bad,
        "best_violations": global_best_bad,
        "restarts": restart,
        "moves": total_moves,
        "breakouts": total_breakouts,
        "elapsed_seconds": round(monotonic() - started, 6),
        "random_seed": args.random_seed,
    }
    events.append(stats)

    colors = expand(global_best, args.target, point_orbit)
    if global_best_bad == 0:
        verify(colors)
        if args.output is None:
            raise ValueError("--output is required when a witness is found")
        args.output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        stats["output"] = str(args.output)
    elif args.best_output is not None:
        args.best_output.write_text(
            " ".join(map(str, colors[1:])) + "\n", encoding="ascii"
        )
        stats["best_output"] = str(args.best_output)

    if args.log is not None:
        args.log.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, sort_keys=True), flush=True)
    if global_best_bad:
        raise RuntimeError(json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
