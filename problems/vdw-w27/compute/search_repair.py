#!/usr/bin/env python3
"""Repair the 3703 residue coloring so it extends to 3704+.

The published coloring cannot accept either color at 3704. Each blocking
7-AP shares the new point; flipping one earlier point on a blocking AP
can clear it. Search small flip-sets, then min-conflicts.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path
from time import monotonic

from vdw import (
    count_mono_aps,
    enumerate_new_aps_through,
    first_mono_ap,
    format_ab,
    load_coloring,
)

HERE = Path(__file__).resolve().parent


def blocking_aps(prefix: list[int], color: int, k: int = 7) -> list[tuple[int, ...]]:
    n = len(prefix) + 1
    point = n - 1
    colors = prefix + [color]
    bad = []
    for ap in enumerate_new_aps_through(n, point, k):
        c0 = colors[ap[0]]
        if all(colors[j] == c0 for j in ap[1:]):
            bad.append(ap)
    return bad


def all_linear_aps(n: int, k: int = 7) -> list[tuple[int, ...]]:
    out = []
    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        for a in range(n - (k - 1) * d):
            out.append(tuple(a + i * d for i in range(k)))
    return out


def violated(colors: list[int], aps: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    bad = []
    for ap in aps:
        c0 = colors[ap[0]]
        if all(colors[j] == c0 for j in ap[1:]):
            bad.append(ap)
    return bad


def try_flip_sets(seed: list[int], target: int, max_flips: int) -> dict:
    prefix = seed[: target - 1] if len(seed) >= target - 1 else seed
    # pad if seed is 3703 and target is 3704: prefix is the 3703 coloring
    if len(prefix) != target - 1:
        raise ValueError(f"need seed length >= {target - 1}, got {len(seed)}")
    attempts = []
    for color in (0, 1):
        blockers = blocking_aps(prefix, color)
        movable = []
        for ap in blockers:
            movable.append([p for p in ap if p != target - 1])
        attempts.append({"color": color, "blockers": len(blockers)})
        # Try flipping one point per blocker, product of small sets
        if not blockers:
            colors = prefix + [color]
            return {"ok": True, "colors": colors, "flips": 0, "color": color}
        if len(blockers) > 6:
            continue
        choices = movable
        for combo in itertools.product(*choices):
            flips = set(combo)
            if len(flips) > max_flips:
                continue
            colors = prefix[:]
            for i in flips:
                colors[i] ^= 1
            colors.append(color)
            if first_mono_ap(colors, k=7) is None:
                return {
                    "ok": True,
                    "colors": colors,
                    "flips": sorted(flips),
                    "color": color,
                    "n_flips": len(flips),
                }
    return {"ok": False, "attempts": attempts}


def minconflicts(seed: list[int], target: int, seconds: float, rng_seed: int) -> dict:
    rng = random.Random(rng_seed)
    colors = (seed + [rng.choice((0, 1))])[:target]
    if len(colors) < target:
        colors = colors + [rng.choice((0, 1)) for _ in range(target - len(colors))]
    aps = all_linear_aps(target)
    incident: list[list[int]] = [[] for _ in range(target)]
    for eid, ap in enumerate(aps):
        for p in ap:
            incident[p].append(eid)
    bad = set()
    for eid, ap in enumerate(aps):
        c0 = colors[ap[0]]
        if all(colors[j] == c0 for j in ap[1:]):
            bad.add(eid)
    started = monotonic()
    best = len(bad)
    moves = 0
    while bad and monotonic() - started < seconds:
        eid = rng.choice(tuple(bad))
        ap = aps[eid]
        best_pos = None
        best_delta = 10**9
        for p in ap:
            old = colors[p]
            colors[p] ^= 1
            delta = 0
            for other in incident[p]:
                oap = aps[other]
                c0 = colors[oap[0]]
                now = all(colors[j] == c0 for j in oap[1:])
                was = other in bad
                if now and not was:
                    delta += 1
                elif was and not now:
                    delta -= 1
            colors[p] = old
            if delta < best_delta:
                best_delta = delta
                best_pos = p
        assert best_pos is not None
        colors[best_pos] ^= 1
        for other in incident[best_pos]:
            oap = aps[other]
            c0 = colors[oap[0]]
            now = all(colors[j] == c0 for j in oap[1:])
            if now:
                bad.add(other)
            else:
                bad.discard(other)
        moves += 1
        if len(bad) < best:
            best = len(bad)
    return {
        "ok": not bad,
        "best_violations": best,
        "moves": moves,
        "elapsed": round(monotonic() - started, 3),
        "random_seed": rng_seed,
        "colors": colors if not bad else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=3704)
    parser.add_argument("--max-flips", type=int, default=4)
    parser.add_argument("--seconds", type=float, default=20.0)
    parser.add_argument("--restarts", type=int, default=4)
    args = parser.parse_args()
    seed = load_coloring(str(HERE / "coloring_3703.txt"))
    flip = try_flip_sets(seed, args.target, args.max_flips)
    print(json.dumps({k: v for k, v in flip.items() if k != "colors"}, sort_keys=True), flush=True)
    if flip.get("ok"):
        colors = flip["colors"]
        path = HERE / f"coloring_{args.target}.txt"
        path.write_text(format_ab(colors) + "\n", encoding="ascii")
        print("wrote", path, flush=True)
        (HERE / "repair.json").write_text(
            json.dumps({k: v for k, v in flip.items() if k != "colors"}, indent=2) + "\n"
        )
        return

    best = None
    logs = []
    for r in range(args.restarts):
        rec = minconflicts(seed, args.target, args.seconds, rng_seed=r + 1)
        logs.append({k: v for k, v in rec.items() if k != "colors"})
        print(json.dumps(logs[-1], sort_keys=True), flush=True)
        if rec["ok"]:
            best = rec
            break
        if best is None or rec["best_violations"] < best["best_violations"]:
            best = rec
    if best and best.get("ok"):
        path = HERE / f"coloring_{args.target}.txt"
        path.write_text(format_ab(best["colors"]) + "\n", encoding="ascii")
        print("wrote", path, flush=True)
    (HERE / "repair.json").write_text(
        json.dumps({"flip_search": {k: v for k, v in flip.items() if k != "colors"}, "minconflicts": logs}, indent=2)
        + "\n"
    )


if __name__ == "__main__":
    main()
