#!/usr/bin/env python3
"""Weighted min-conflicts search on the complement-orbit Schur hypergraph."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from time import monotonic

from search_almost_symmetric_pysat import old_coloring
from search_shifted_sat import seed_coloring, verify


def build(target: int) -> tuple[list[int], list[tuple[int, ...]], list[list[int]], callable]:
    center = target + 1
    exceptional = (center // 3, 2 * center // 3) if center % 3 == 0 else None

    def key(x: int) -> int:
        if exceptional is not None and x in exceptional:
            return x
        return min(x, center - x)

    keys = sorted({key(x) for x in range(1, target + 1)})
    index = {value: position for position, value in enumerate(keys)}
    edge_set: set[tuple[int, ...]] = set()
    for x in range(1, target + 1):
        for y in range(x, target - x + 1):
            edge_set.add(tuple(sorted({index[key(x)], index[key(y)], index[key(x + y)]})))
    edges = sorted(edge_set)
    if edges and len(edges[0]) == 1:
        raise ValueError(f"orbit symmetry creates unavoidable edge {edges[0]}")
    incident = [[] for _ in keys]
    for eid, edge in enumerate(edges):
        for vertex in edge:
            incident[vertex].append(eid)
    return keys, edges, incident, key


def solve(
    target: int,
    seconds: float,
    random_seed: int,
    structural_prefix: bool,
) -> tuple[list[int], dict[str, int | float | str]]:
    keys, edges, incident, key = build(target)
    key_index = {value: position for position, value in enumerate(keys)}
    rng = random.Random(random_seed)
    old = old_coloring()
    six = seed_coloring()
    domains = [list(range(7)) for _ in keys]
    if structural_prefix:
        for x in range(1, 537):
            domains[key_index[key(x)]] = list(range(6))
        domains[key_index[key(537)]] = [6]

    started = monotonic()
    deadline = started + seconds
    best = len(edges) + 1
    restarts = 0
    moves = 0
    best_assignment: list[int] | None = None

    while monotonic() < deadline:
        restarts += 1
        assignment: list[int] = []
        for position, key_value in enumerate(keys):
            domain = domains[position]
            if len(domain) == 1:
                assignment.append(domain[0])
            elif restarts == 1 and key_value <= 536 and six[key_value] in domain:
                assignment.append(six[key_value])
            elif restarts == 1 and key_value <= 1680 and old[key_value] in domain:
                assignment.append(old[key_value])
            else:
                assignment.append(rng.choice(domain))

        weights = [1] * len(edges)
        costs = [[0] * 7 for _ in keys]
        violated: list[int] = []
        violated_position = [-1] * len(edges)

        def edge_violated(eid: int) -> bool:
            edge = edges[eid]
            color = assignment[edge[0]]
            return all(assignment[vertex] == color for vertex in edge[1:])

        def add_violation(eid: int) -> None:
            if violated_position[eid] == -1:
                violated_position[eid] = len(violated)
                violated.append(eid)

        def remove_violation(eid: int) -> None:
            position = violated_position[eid]
            if position == -1:
                return
            last = violated.pop()
            if position < len(violated):
                violated[position] = last
                violated_position[last] = position
            violated_position[eid] = -1

        def adjust_edge_costs(eid: int, sign: int) -> None:
            edge = edges[eid]
            weight = sign * weights[eid]
            for vertex in edge:
                other_colors = {assignment[other] for other in edge if other != vertex}
                if len(other_colors) == 1:
                    costs[vertex][other_colors.pop()] += weight

        for eid in range(len(edges)):
            adjust_edge_costs(eid, 1)
            if edge_violated(eid):
                add_violation(eid)

        tabu_until = [[0] * 7 for _ in keys]
        plateau = 0
        local_moves = 0
        restart_limit = 300_000
        while violated and monotonic() < deadline and local_moves < restart_limit:
            local_moves += 1
            moves += 1
            if len(violated) < best:
                best = len(violated)
                best_assignment = assignment[:]
                plateau = 0
                print(
                    json.dumps(
                        {
                            "best_violations": best,
                            "moves": moves,
                            "restart": restarts,
                            "elapsed_seconds": round(monotonic() - started, 3),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
            else:
                plateau += 1

            eid = rng.choice(violated)
            edge = edges[eid]
            candidates: list[tuple[int, int, int]] = []
            for vertex in edge:
                old_color = assignment[vertex]
                for color in domains[vertex]:
                    if color == old_color:
                        continue
                    delta = costs[vertex][color] - costs[vertex][old_color]
                    if tabu_until[vertex][color] <= moves or len(violated) + delta == 0:
                        candidates.append((delta, vertex, color))
            if not candidates:
                vertex = rng.choice(edge)
                choices = [color for color in domains[vertex] if color != assignment[vertex]]
                if not choices:
                    continue
                chosen = (0, vertex, rng.choice(choices))
            elif rng.random() < 0.015:
                chosen = rng.choice(candidates)
            else:
                minimum = min(item[0] for item in candidates)
                chosen = rng.choice([item for item in candidates if item[0] == minimum])

            _, vertex, new_color = chosen
            old_color = assignment[vertex]
            affected = incident[vertex]
            before = [(affected_eid, edge_violated(affected_eid)) for affected_eid in affected]
            for affected_eid in affected:
                adjust_edge_costs(affected_eid, -1)
            assignment[vertex] = new_color
            for affected_eid in affected:
                adjust_edge_costs(affected_eid, 1)
            for affected_eid, was_violated in before:
                now_violated = edge_violated(affected_eid)
                if was_violated and not now_violated:
                    remove_violation(affected_eid)
                elif not was_violated and now_violated:
                    add_violation(affected_eid)
            tabu_until[vertex][old_color] = moves + 5 + rng.randrange(8)

            if plateau >= 10_000 and violated:
                # Breakout: make the current local obstruction more expensive.
                for bad_eid in violated:
                    adjust_edge_costs(bad_eid, -1)
                    weights[bad_eid] += 1
                    adjust_edge_costs(bad_eid, 1)
                plateau = 0

        if not violated:
            key_colors = {key_value: assignment[position] for position, key_value in enumerate(keys)}
            colors = [-1] + [key_colors[key(x)] for x in range(1, target + 1)]
            verify(colors)
            return colors, {
                "target": target,
                "random_seed": random_seed,
                "structural_prefix": str(structural_prefix).lower(),
                "orbit_variables": len(keys),
                "orbit_edges": len(edges),
                "restarts": restarts,
                "moves": moves,
                "elapsed_seconds": round(monotonic() - started, 6),
                "result": "sat",
            }

    raise RuntimeError(
        json.dumps(
            {
                "target": target,
                "random_seed": random_seed,
                "structural_prefix": str(structural_prefix).lower(),
                "orbit_variables": len(keys),
                "orbit_edges": len(edges),
                "restarts": restarts,
                "moves": moves,
                "elapsed_seconds": round(monotonic() - started, 6),
                "result": "timeout",
                "best_violations": best,
                "best_assignment_recorded": str(best_assignment is not None).lower(),
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1697)
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--random-seed", type=int, default=1)
    parser.add_argument("--structural-prefix", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    colors, stats = solve(args.target, args.seconds, args.random_seed, args.structural_prefix)
    print(json.dumps(stats, sort_keys=True), flush=True)
    if args.output:
        args.output.write_text(" ".join(map(str, colors[1:])) + "\n", encoding="ascii")
        print(f"wrote {args.output} ({len(colors) - 1} colors)", flush=True)


if __name__ == "__main__":
    main()
