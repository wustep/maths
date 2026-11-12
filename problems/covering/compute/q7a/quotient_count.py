#!/usr/bin/env python3
"""Necessary quotient-fiber count for invariant radius-two coverings.

Let G fix a subspace F pointwise.  Every nonfixed point orbit projects
bijectionally to a G-orbit in V/F, and there are |F| lifted point orbits over
each quotient orbit.  For a G-invariant set, let k_i be the number of selected
lifts above quotient orbit i and let s be the number of selected nonzero fixed
points.  For a fixed nonzero quotient vector in orbit t, this program computes
an optimistic upper bound B_t on the number of F-coordinates that can be
covered by zero, singletons, and unordered pairs.  A covering requires
B_t >= |F| for every t.  Thus a complete enumeration with max_t min(B_t)<|F|
is a rigorous exclusion; an OPEN result is only residue.

The program derives F, V/F, all quotient orbits, and their sum incidence
directly from the .grp generator.  It does not trust the class name or header.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path


R = 10
V = 1 << R


def read_group(path: Path) -> list[list[int]]:
    generators: list[list[int]] = []
    for line in path.read_text().splitlines():
        if not line or line.lstrip().startswith("#"):
            continue
        images = [int(token, 0) for token in line.split()]
        if len(images) != R or any(not 0 <= value < V for value in images):
            raise ValueError(f"malformed generator in {path}")
        if len({apply(images, value) for value in range(V)}) != V:
            raise ValueError(f"singular generator in {path}")
        generators.append(images)
    if not generators:
        raise ValueError(f"no generators in {path}")
    return generators


def apply(images: list[int], value: int) -> int:
    output = 0
    while value:
        low_bit = value & -value
        output ^= images[low_bit.bit_length() - 1]
        value ^= low_bit
    return output


def group_orbit(start: int, generators: list[list[int]]) -> tuple[int, ...]:
    seen = {start}
    queue = deque([start])
    while queue:
        value = queue.popleft()
        for generator in generators:
            image = apply(generator, value)
            if image not in seen:
                seen.add(image)
                queue.append(image)
    return tuple(sorted(seen))


def optimistic_counts(
    counts: list[int], selected_fixed: int,
    incidence: list[list[set[int]]],
) -> list[int]:
    classes = len(counts)
    result: list[int] = []
    fixed_with_zero = selected_fixed + 1
    for target in range(classes):
        # A selected lift over the target quotient orbit can pair with zero or
        # any selected fixed point.  Each such pair contributes at most one
        # F-coordinate.
        bound = counts[target] * fixed_with_zero

        # All within-one-lift pairs have F-coordinate zero, collectively
        # contributing at most one value for this target quotient vector.
        if any(
            counts[index] and target in incidence[index][index]
            for index in range(classes)
        ):
            bound += 1

        # A pair of distinct lifted orbits has one constant F-coordinate.
        # Counting every orbit pair separately is optimistic because their
        # coordinates may collide, hence remains safe for an exclusion.
        for left in range(classes):
            if target in incidence[left][left]:
                bound += counts[left] * (counts[left] - 1) // 2
            for right in range(left):
                if target in incidence[left][right]:
                    bound += counts[left] * counts[right]
        result.append(bound)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=Path, required=True)
    parser.add_argument("--n", type=int, default=49)
    parser.add_argument(
        "--selected-orbits", type=int,
        help="enumerate only this number of selected nonfixed point orbits",
    )
    parser.add_argument("--max-compositions", type=int, default=10_000_000)
    args = parser.parse_args()

    generators = read_group(args.group)
    fixed = tuple(
        value for value in range(V)
        if all(apply(generator, value) == value for generator in generators)
    )
    fixed_set = set(fixed)
    if not fixed or len(fixed) & (len(fixed) - 1):
        raise RuntimeError("common fixed set is not a binary subspace")
    if any(left ^ right not in fixed_set for left in fixed for right in fixed):
        raise RuntimeError("common fixed set is not XOR-closed")

    def representative(value: int) -> int:
        return min(value ^ shift for shift in fixed)

    quotient_points = sorted({representative(value) for value in range(V)})
    if len(quotient_points) * len(fixed) != V or quotient_points[0] != 0:
        raise RuntimeError("bad quotient transversal")

    quotient_orbits: list[tuple[int, ...]] = []
    seen_quotient = {0}
    for start in quotient_points[1:]:
        if start in seen_quotient:
            continue
        orbit = {
            representative(value)
            for value in group_orbit(start, generators)
        }
        quotient_orbit = tuple(sorted(orbit))
        quotient_orbits.append(quotient_orbit)
        seen_quotient.update(quotient_orbit)
    quotient_orbits.sort(key=lambda orbit: (len(orbit), orbit[0]))
    quotient_class = {
        value: index
        for index, orbit in enumerate(quotient_orbits)
        for value in orbit
    }
    if seen_quotient != set(quotient_points):
        raise RuntimeError("quotient orbit enumeration is incomplete")

    # Independently enumerate full point orbits and confirm the lift model.
    seen_points: set[int] = set()
    lift_counts = [0] * len(quotient_orbits)
    fixed_orbits = 0
    for start in range(1, V):
        if start in seen_points:
            continue
        orbit = group_orbit(start, generators)
        seen_points.update(orbit)
        projection = tuple(sorted({representative(value) for value in orbit}))
        if projection == (0,):
            if len(orbit) != 1:
                raise RuntimeError("nontrivial orbit projects to zero")
            fixed_orbits += 1
            continue
        quotient_id = quotient_class[projection[0]]
        if projection != quotient_orbits[quotient_id] or len(orbit) != len(projection):
            raise RuntimeError("a point orbit does not project bijectively")
        lift_counts[quotient_id] += 1
    if seen_points != set(range(1, V)):
        raise RuntimeError("point orbit enumeration is incomplete")
    if fixed_orbits != len(fixed) - 1:
        raise RuntimeError("wrong number of nonzero fixed-point orbits")
    if any(count != len(fixed) for count in lift_counts):
        raise RuntimeError(f"unexpected lift multiplicities {lift_counts}")

    classes = len(quotient_orbits)
    incidence = [[set() for _ in range(classes)] for _ in range(classes)]
    for left in range(classes):
        for right in range(left + 1):
            targets = {
                quotient_class[representative(x ^ y)]
                for x in quotient_orbits[left]
                for y in quotient_orbits[right]
                if representative(x ^ y) != 0
            }
            incidence[left][right] = targets
            incidence[right][left] = targets

    weights = [len(orbit) for orbit in quotient_orbits]
    fixed_capacity = len(fixed) - 1
    best_by_orbit_count: dict[int, tuple[int, list[int], int, list[int]]] = {}
    feasible = 0
    counts: list[int] = []

    def recurse(index: int, used_points: int, used_orbits: int) -> None:
        nonlocal feasible
        if feasible >= args.max_compositions:
            raise RuntimeError(
                f"composition limit {args.max_compositions} reached; no result"
            )
        if used_points > args.n:
            return
        if args.selected_orbits is not None and used_orbits > args.selected_orbits:
            return
        if index == classes:
            selected_fixed = args.n - used_points
            if not 0 <= selected_fixed <= fixed_capacity:
                return
            if (args.selected_orbits is not None and
                    used_orbits != args.selected_orbits):
                return
            feasible += 1
            bounds = optimistic_counts(counts, selected_fixed, incidence)
            score = min(bounds)
            prior = best_by_orbit_count.get(used_orbits)
            if prior is None or score > prior[0]:
                best_by_orbit_count[used_orbits] = (
                    score, counts.copy(), selected_fixed, bounds
                )
            return

        weight = weights[index]
        maximum = min(len(fixed), (args.n - used_points) // weight)
        if args.selected_orbits is not None:
            maximum = min(maximum, args.selected_orbits - used_orbits)
        for count in range(maximum + 1):
            counts.append(count)
            recurse(
                index + 1,
                used_points + count * weight,
                used_orbits + count,
            )
            counts.pop()

    recurse(0, 0, 0)
    print(
        f"group={args.group} fixed_dim={len(fixed).bit_length() - 1} "
        f"fixed_size={len(fixed)} quotient_orbits={classes} "
        f"weights={weights} lifts={lift_counts} feasible={feasible}"
    )
    for orbit_count in sorted(best_by_orbit_count):
        score, best_counts, selected_fixed, bounds = best_by_orbit_count[orbit_count]
        print(
            f"branch nonfixed_orbits={orbit_count} fixed_points={selected_fixed} "
            f"best_min={score}/{len(fixed)} counts={best_counts} "
            f"bounds={bounds}"
        )
    if feasible and all(
        record[0] < len(fixed) for record in best_by_orbit_count.values()
    ):
        print(
            f"RESULT group={args.group} n={args.n} excluded=yes "
            "(exhausted by necessary quotient-fiber count)"
        )
        return 0
    print(
        f"RESULT group={args.group} n={args.n} excluded=no "
        "(quotient-fiber count leaves branches open)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
