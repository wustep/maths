#!/usr/bin/env python3
"""Min-conflicts search for a cyclic 2-coloring of Z/nZ with no mono 7-AP."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from time import monotonic

from vdw import first_mono_ap, format_ab, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent


def cyclic_aps(n: int, k: int = 7) -> list[tuple[int, ...]]:
    aps = []
    seen: set[frozenset[int]] = set()
    for d in range(1, n):
        for a in range(n):
            pts = tuple((a + i * d) % n for i in range(k))
            key = frozenset(pts)
            if len(key) < k or key in seen:
                continue
            seen.add(key)
            aps.append(pts)
    return aps


def solve(n: int, seconds: float, rng_seed: int) -> dict:
    rng = random.Random(rng_seed)
    aps = cyclic_aps(n)
    incident = [[] for _ in range(n)]
    for eid, ap in enumerate(aps):
        for p in ap:
            incident[p].append(eid)
    # seed: 617 QR cycle padded/truncated
    base = quadratic_residue_cycle(617, 0)
    colors = [(base[i % 617] if i < 617 else rng.choice((0, 1))) for i in range(n)]
    if n < 617:
        colors = base[:n]
    bad = set()
    for eid, ap in enumerate(aps):
        c0 = colors[ap[0]]
        if all(colors[j] == c0 for j in ap[1:]):
            bad.add(eid)
    started = monotonic()
    best = len(bad)
    moves = 0
    while bad and monotonic() - started < seconds:
        eid = rng.choice(tuple(bad) if len(bad) < 200 else list(bad)[:200] or tuple(bad))
        # pick from a random violated AP
        eid = rng.choice(tuple(bad))
        ap = aps[eid]
        best_p, best_delta = ap[0], 10**9
        for p in ap:
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
            colors[p] ^= 1
            if delta < best_delta:
                best_delta, best_p = delta, p
        colors[best_p] ^= 1
        for other in incident[best_p]:
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
    ok = not bad
    if ok:
        assert first_mono_ap(colors, 7, cyclic=True) is None
    return {
        "n": n,
        "ok": ok,
        "best_violations": best,
        "moves": moves,
        "elapsed": round(monotonic() - started, 3),
        "colors": colors if ok else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=618)
    parser.add_argument("--n-max", type=int, default=640)
    parser.add_argument("--seconds", type=float, default=8.0)
    args = parser.parse_args()
    rows = []
    for n in range(args.n_min, args.n_max + 1):
        rec = solve(n, args.seconds, rng_seed=n)
        slim = {k: v for k, v in rec.items() if k != "colors"}
        rows.append(slim)
        print(slim, flush=True)
        if rec["ok"]:
            path = HERE / f"cycle_{n}.txt"
            path.write_text(format_ab(rec["colors"]) + "\n")
            linear = rec["colors"] * 6
            path2 = HERE / f"coloring_{6 * n}.txt"
            path2.write_text(format_ab(linear) + "\n")
            print("HIT linear", 6 * n, flush=True)
            break
    (HERE / "cyclic_local.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
