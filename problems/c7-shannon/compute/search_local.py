#!/usr/bin/env python3
"""Local search past the Polak-Schrijver 367-set.

Builds closed-neighborhood lists, then:
  1. reports free vertices (addable without deletion)
  2. exhaustive 1-out / 2-out improving swaps
  3. sampled 3-out and 4-out swaps
  4. simulated annealing that may drop below 367 and climb back
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from c7_common import NEIGH_CLOSED, NVERTS, closed_neighbors, format_word
from verify_set import first_conflict, load_set

HERE = Path(__file__).resolve().parent


def build_neigh() -> list[list[int]]:
    return [closed_neighbors(v) for v in range(NVERTS)]


def blocked_from(selected: set[int], neigh: list[list[int]]) -> list[int]:
    blocked = [0] * NVERTS
    for v in selected:
        for u in neigh[v]:
            blocked[u] += 1
    return blocked


def free_vertices(selected: set[int], blocked: list[int]) -> list[int]:
    return [v for v in range(NVERTS) if blocked[v] == 0 and v not in selected]


def add_vertex(v: int, selected: set[int], blocked: list[int], neigh: list[list[int]]) -> None:
    selected.add(v)
    for u in neigh[v]:
        blocked[u] += 1


def rem_vertex(v: int, selected: set[int], blocked: list[int], neigh: list[list[int]]) -> None:
    selected.remove(v)
    for u in neigh[v]:
        blocked[u] -= 1


def residual_mis(cands: list[int], neigh: list[list[int]], limit: int = 40) -> list[int]:
    """Greedy+exact MIS on a small candidate list (vertices pairwise checked via neigh)."""
    if not cands:
        return []
    if len(cands) > 64:
        # greedy by degree, then stop
        cand_set = set(cands)
        deg = {v: sum(1 for u in neigh[v] if u in cand_set and u != v) for v in cands}
        order = sorted(cands, key=lambda v: deg[v])
        taken = []
        forbidden = set()
        for v in order:
            if v in forbidden:
                continue
            taken.append(v)
            forbidden.update(neigh[v])
        return taken
    idx = {v: i for i, v in enumerate(cands)}
    n = len(cands)
    adj = [0] * n
    for i, v in enumerate(cands):
        for u in neigh[v]:
            if u != v and u in idx:
                adj[i] |= 1 << idx[u]
    best = 0
    best_mask = 0

    def rec(cand: int, cur: int) -> None:
        nonlocal best, best_mask
        if cand.bit_count() + cur.bit_count() <= best:
            return
        if cand == 0:
            if cur.bit_count() > best:
                best = cur.bit_count()
                best_mask = cur
            return
        v = (cand & -cand).bit_length() - 1
        rec(cand & ~adj[v] & ~(1 << v), cur | (1 << v))
        rec(cand & ~(1 << v), cur)

    rec((1 << n) - 1, 0)
    return [cands[i] for i in range(n) if (best_mask >> i) & 1]


def newly_free(removed: list[int], blocked: list[int], neigh: list[list[int]]) -> list[int]:
    cand = []
    seen = set()
    for v in removed:
        for u in neigh[v]:
            if blocked[u] == 0 and u not in seen:
                seen.add(u)
                cand.append(u)
    return cand


def try_k_out(selected: set[int], blocked: list[int], neigh: list[list[int]], remove: list[int]) -> list[int] | None:
    for v in remove:
        rem_vertex(v, selected, blocked, neigh)
    freed = newly_free(remove, blocked, neigh)
    add = residual_mis(freed, neigh)
    gained = len(add) - len(remove)
    if gained >= 1:
        result = list(selected | set(add))
        for v in add:
            add_vertex(v, selected, blocked, neigh)
        for v in remove:
            add_vertex(v, selected, blocked, neigh)
        return result
    for v in remove:
        add_vertex(v, selected, blocked, neigh)
    return None


def anneal(selected: set[int], blocked: list[int], neigh: list[list[int]], steps: int, seed: int) -> int:
    rng = random.Random(seed)
    cur = list(selected)
    best = len(cur)
    temp = 1.2
    for t in range(steps):
        temp *= 0.9995
        if not cur:
            break
        v = rng.choice(cur)
        rem_vertex(v, selected, blocked, neigh)
        cur.remove(v)
        freed = newly_free([v], blocked, neigh)
        if freed:
            # add a random maximal packing of freed vertices
            rng.shuffle(freed)
            added = []
            for u in freed:
                if blocked[u] == 0:
                    add_vertex(u, selected, blocked, neigh)
                    added.append(u)
            cur.extend(added)
        delta = len(cur) - best
        if len(cur) > best:
            best = len(cur)
            print(f"  anneal seed={seed} step={t} size={best}", flush=True)
            if best >= 368:
                return best
        elif rng.random() > (1.0 if temp <= 0 else min(1.0, pow(2.718, delta / max(temp, 1e-6)))):
            # reject: restore by not doing anything further; already moved
            pass
        if t % 2000 == 0:
            print(f"  anneal seed={seed} step={t} size={len(cur)} best={best} temp={temp:.4f}", flush=True)
    return best


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-set", type=Path, default=HERE / "R367.txt")
    ap.add_argument("--anneal-steps", type=int, default=8000)
    ap.add_argument("--anneal-restarts", type=int, default=3)
    ap.add_argument("--sample-3", type=int, default=4000)
    ap.add_argument("--sample-4", type=int, default=4000)
    args = ap.parse_args()
    t0 = time.time()
    words = load_set(args.seed_set)
    selected = set(words)
    print(f"loaded {len(selected)} from {args.seed_set}", flush=True)
    print("building neighborhoods...", flush=True)
    neigh = build_neigh()
    blocked = blocked_from(selected, neigh)
    free = free_vertices(selected, blocked)
    print(f"free_vertices={len(free)}", flush=True)
    log = [f"seed {args.seed_set} size {len(selected)}", f"free {len(free)}"]

    # 1-out
    improved = None
    cur_list = list(selected)
    for i, v in enumerate(cur_list):
        hit = try_k_out(selected, blocked, neigh, [v])
        if hit is not None and len(hit) >= 368:
            improved = hit
            print(f"1-out improvement size={len(hit)}", flush=True)
            break
        if i % 50 == 0:
            print(f"  1-out {i}/{len(cur_list)}", flush=True)
    log.append(f"1-out {'HIT '+str(len(improved)) if improved else 'none'}")

    if improved is None:
        n = len(cur_list)
        trials = 0
        for i in range(n):
            for j in range(i + 1, n):
                trials += 1
                hit = try_k_out(selected, blocked, neigh, [cur_list[i], cur_list[j]])
                if hit is not None and len(hit) >= 368:
                    improved = hit
                    print(f"2-out improvement size={len(hit)}", flush=True)
                    break
                if trials % 2000 == 0:
                    print(f"  2-out {trials}", flush=True)
            if improved is not None:
                break
        log.append(f"2-out {'HIT '+str(len(improved)) if improved else 'none'} trials={trials}")

    rng = random.Random(1)
    if improved is None:
        hits3 = 0
        for t in range(args.sample_3):
            rem = rng.sample(cur_list, 3)
            hit = try_k_out(selected, blocked, neigh, rem)
            if hit is not None and len(hit) >= 368:
                improved = hit
                hits3 += 1
                print(f"3-out improvement size={len(hit)}", flush=True)
                break
        log.append(f"3-out-sample {args.sample_3} {'HIT' if improved else 'none'}")

    if improved is None:
        for t in range(args.sample_4):
            rem = rng.sample(cur_list, 4)
            hit = try_k_out(selected, blocked, neigh, rem)
            if hit is not None and len(hit) >= 368:
                improved = hit
                print(f"4-out improvement size={len(hit)}", flush=True)
                break
        log.append(f"4-out-sample {args.sample_4} {'HIT' if improved else 'none'}")

    best_anneal = 0
    if improved is None:
        for s in range(args.anneal_restarts):
            sel = set(words)
            blk = blocked_from(sel, neigh)
            best_anneal = max(best_anneal, anneal(sel, blk, neigh, args.anneal_steps, seed=s + 7))
            if best_anneal >= 368:
                improved = list(sel)
                break
        log.append(f"anneal_best {best_anneal}")

    if improved is not None:
        improved = sorted(set(improved))
        conflict = first_conflict(improved)
        if conflict is not None:
            raise SystemExit("local search produced an adjacent pair")
        out = HERE / f"R{len(improved)}.txt"
        out.write_text("\n".join(format_word(v) for v in improved) + "\n")
        print(f"WROTE {out} size={len(improved)}")
        log.append(f"wrote {out}")
    else:
        print("no 368-set found")
        log.append("no 368-set")
    log.append(f"seconds {time.time()-t0:.1f}")
    (HERE / "local_search_log.txt").write_text("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
