#!/usr/bin/env python3
"""Exhaust the one-orbit rct4 repairs of the embedded n=73 witness."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from rct4_model import build_rct4_geometry, selected_points  # noqa: E402


def read_points(path: Path) -> set[tuple[int, int]]:
    return {tuple(map(int, line.split())) for line in path.read_text().splitlines() if line.strip()}


def incidence(orbit: tuple[tuple[int, int], ...], n: int) -> tuple[int, ...]:
    rows = Counter(y for _, y in orbit)
    columns = Counter(x for x, _ in orbit)
    return tuple(rows[i] for i in range(n)) + tuple(columns[i] for i in range(n))


def add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def subtract(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...] | None:
    result = tuple(a - b for a, b in zip(left, right))
    return result if min(result) >= 0 else None


def normalized_line(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int, int]:
    dx = right[0] - left[0]
    dy = right[1] - left[1]
    a, b = dy, -dx
    c = dx * left[1] - dy * left[0]
    divisor = gcd(gcd(abs(a), abs(b)), abs(c))
    a, b, c = a // divisor, b // divisor, c // divisor
    if a < 0 or (a == 0 and b < 0):
        a, b, c = -a, -b, -c
    return a, b, c


def no_three(points: list[tuple[int, int]]) -> bool:
    lines = set()
    for left in range(len(points)):
        for right in range(left + 1, len(points)):
            line = normalized_line(points[left], points[right])
            if line in lines:
                return False
            lines.add(line)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=HERE / "n73-best-embedding.txt")
    parser.add_argument("--output", type=Path, default=HERE / "n75-150-small-repair.txt")
    parser.add_argument("--json", type=Path, default=HERE / "small-repair.json")
    args = parser.parse_args()

    n = 75
    geometry = build_rct4_geometry(n)
    seed = read_points(args.seed)
    selected = {
        orbit_id
        for orbit_id, orbit in enumerate(geometry.orbits)
        if all(point in seed for point in orbit)
    }
    if sum(len(geometry.orbits[i]) for i in selected) != len(seed):
        raise AssertionError("seed is not a union of complete rct4 orbits")

    contributions = [incidence(orbit, n) for orbit in geometry.orbits]
    seed_total = tuple(sum(vector[k] for vector in (contributions[i] for i in selected)) for k in range(2 * n))
    target = (2,) * (2 * n)
    selected_diag = set(geometry.diagonal_orbits) & selected
    selected_off = set(geometry.off_diagonal_orbits) & selected
    available_diag = set(geometry.diagonal_orbits) - selected
    available_off = set(geometry.off_diagonal_orbits) - selected
    if len(selected_diag) != 1 or len(selected_off) != 36:
        raise AssertionError("expected one diagonal and 36 off-diagonal seed orbits")

    off_by_vector: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for orbit_id in sorted(available_off):
        off_by_vector[contributions[orbit_id]].append(orbit_id)

    radius_one: set[frozenset[int]] = set()
    # Keep the selected diagonal: remove one old four-orbit and add two new.
    for removed in selected_off:
        need = subtract(target, add(seed_total, tuple(-x for x in contributions[removed])))
        if need is None:
            raise AssertionError("removing an orbit cannot overfill a row")
        for first in sorted(available_off):
            complement = subtract(need, contributions[first])
            if complement is None:
                continue
            for second in off_by_vector.get(complement, []):
                if first < second:
                    radius_one.add(frozenset((selected - {removed}) | {first, second}))

    # Swap the selected diagonal pair and add one new four-orbit.
    old_diag = next(iter(selected_diag))
    after_removal = add(seed_total, tuple(-x for x in contributions[old_diag]))
    for new_diag in sorted(available_diag):
        need = subtract(target, add(after_removal, contributions[new_diag]))
        if need is None:
            continue
        for off in off_by_vector.get(need, []):
            radius_one.add(frozenset((selected - {old_diag}) | {new_diag, off}))

    # Radius two. Exactly two newly selected off-diagonal orbits must touch
    # the empty boundary rows/columns; any third new off-diagonal orbit is
    # interior. Hash the boundary-pair incidence vectors.
    boundary_off = {
        orbit_id
        for orbit_id in available_off
        if any(x in (0, n - 1) or y in (0, n - 1) for x, y in geometry.orbits[orbit_id])
    }
    interior_off = available_off - boundary_off
    boundary_pairs: dict[tuple[int, ...], list[tuple[int, int]]] = defaultdict(list)
    for first, second in combinations(sorted(boundary_off), 2):
        vector = add(contributions[first], contributions[second])
        if all(vector[i] == 2 for i in (0, n - 1, n, 2 * n - 1)):
            boundary_pairs[vector].append((first, second))

    radius_two: set[frozenset[int]] = set()
    for removed_left, removed_right in combinations(sorted(selected_off), 2):
        after_removal = add(
            seed_total,
            tuple(
                -contributions[removed_left][k] - contributions[removed_right][k]
                for k in range(2 * n)
            ),
        )
        need = subtract(target, after_removal)
        if need is None:
            raise AssertionError("removing orbits cannot overfill a row")
        for interior in sorted(interior_off):
            pair_need = subtract(need, contributions[interior])
            if pair_need is None:
                continue
            for first, second in boundary_pairs.get(pair_need, []):
                radius_two.add(
                    frozenset(
                        (selected - {removed_left, removed_right})
                        | {interior, first, second}
                    )
                )

    # Radius-two diagonal swap: remove the old diagonal and one old
    # four-orbit, then add another diagonal and two boundary four-orbits.
    for removed in sorted(selected_off):
        after_removal = add(
            seed_total,
            tuple(
                -contributions[old_diag][k] - contributions[removed][k]
                for k in range(2 * n)
            ),
        )
        for new_diag in sorted(available_diag):
            pair_need = subtract(target, add(after_removal, contributions[new_diag]))
            if pair_need is None:
                continue
            for first, second in boundary_pairs.get(pair_need, []):
                radius_two.add(
                    frozenset((selected - {old_diag, removed}) | {new_diag, first, second})
                )

    candidates = radius_one | radius_two

    checked = 0
    witness = None
    for orbit_set in sorted(candidates, key=lambda item: tuple(sorted(item))):
        checked += 1
        points = selected_points(geometry, set(orbit_set))
        if no_three(points):
            witness = points
            break

    result = {
        "n": n,
        "symmetry": "canonical-rct4",
        "seed_orbits": len(selected),
        "incidence_feasible_one_orbit_repairs": len(radius_one),
        "incidence_feasible_two_orbit_repairs": len(radius_two),
        "geometry_candidates_checked": checked,
        "status": "SAT" if witness is not None else "EXHAUSTED_NO_WITNESS",
    }
    if witness is not None:
        payload = "".join(f"{x} {y}\n" for x, y in witness)
        args.output.write_text(payload, encoding="ascii")
        result["witness"] = str(args.output)
        result["witness_sha256"] = hashlib.sha256(payload.encode("ascii")).hexdigest()
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
