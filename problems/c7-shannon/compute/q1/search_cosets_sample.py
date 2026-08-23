#!/usr/bin/env python3
"""Verified sample of good 2-dim codes: greedy + residual of the pack.

Uses the actual closed-neighbourhood graph, not a quotient-coordinate gadget.
Eight cosets would be 392 vertices. A leftover quotient vertex after a 7-pack
would already be 392.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from c7_common import DIM, N, NVERTS, closed_neighbors, encode, format_word
from verify_set import first_conflict

SMALL = {0, 1, 6}


def apply(a, b, s, t):
    return tuple((s * a[i] + t * b[i]) % N for i in range(DIM))


def is_good(a, b) -> bool:
    for s in range(N):
        for t in range(N):
            if s == 0 and t == 0:
                continue
            w = apply(a, b, s, t)
            if all(x in SMALL for x in w):
                return False
    return True


def random_indep_pair(rng: random.Random):
    while True:
        a = tuple(rng.randrange(N) for _ in range(DIM))
        b = tuple(rng.randrange(N) for _ in range(DIM))
        # rank 2
        ok = False
        ratio = None
        for i in range(DIM):
            if a[i] == 0 and b[i] == 0:
                continue
            if a[i] == 0 or b[i] == 0:
                ok = True
                break
            r = next(t for t in range(N) if (t * a[i]) % N == b[i])
            if ratio is None:
                ratio = r
            elif r != ratio:
                ok = True
                break
        if ok:
            return a, b


def coset_ids(a, b) -> list[int]:
    """Clear the two pivot-ish coordinates of a random basis of V."""
    # Build 49-element V, map each x to min encode(x-v) over v in V as a key,
    # then dense-rank the keys. Slow if naive 16807*49. Instead: pick two
    # coordinates where the 2x2 on a,b is invertible, use those as (s,t).
    for i in range(DIM):
        for j in range(i + 1, DIM):
            det = (a[i] * b[j] - a[j] * b[i]) % N
            if det == 0:
                continue
            inv = next(t for t in range(1, N) if (t * det) % N == 1)
            cid = [0] * NVERTS
            for v in range(NVERTS):
                x0, x1, x2, x3, x4 = (
                    v // 2401,
                    (v // 343) % 7,
                    (v // 49) % 7,
                    (v // 7) % 7,
                    v % 7,
                )
                x = (x0, x1, x2, x3, x4)
                # solve s a + t b ≡ x on coords i,j
                # [a_i b_i; a_j b_j] [s;t] = [x_i; x_j]
                s = (inv * (x[i] * b[j] - x[j] * b[i])) % N
                t = (inv * (a[i] * x[j] - a[j] * x[i])) % N
                w = [(x[k] - s * a[k] - t * b[k]) % N for k in range(DIM)]
                # remaining 3 coords as id
                rest = [w[k] for k in range(DIM) if k != i and k != j]
                cid[v] = rest[0] * 49 + rest[1] * 7 + rest[2]
            return cid
    raise RuntimeError("no invertible 2x2")


def greedy_pack(adj: list[int], rng: random.Random) -> list[int]:
    n = 343
    order = list(range(n))
    rng.shuffle(order)
    taken = []
    banned = 0
    for v in order:
        if (banned >> v) & 1:
            continue
        taken.append(v)
        banned |= adj[v] | (1 << v)
    return taken


def main() -> None:
    t0 = time.time()
    rng = random.Random(0)
    samples = 120
    best = 0
    n_good = 0
    n_tried = 0
    residual_after_7 = 0
    lines = []
    neigh = [closed_neighbors(v) for v in range(NVERTS)]
    print("neighbourhoods ready", flush=True)
    while n_good < samples and n_tried < 4000:
        n_tried += 1
        a, b = random_indep_pair(rng)
        if not is_good(a, b):
            continue
        n_good += 1
        cid = coset_ids(a, b)
        adj = [0] * 343
        for v in range(NVERTS):
            i = cid[v]
            for u in neigh[v]:
                if u == v:
                    continue
                j = cid[u]
                if i != j:
                    adj[i] |= 1 << j
        local = []
        for trial in range(10):
            pack = greedy_pack(adj, rng)
            if len(pack) > len(local):
                local = pack
        # leftover after this pack
        banned = 0
        for v in local:
            banned |= adj[v] | (1 << v)
        leftover = [i for i in range(343) if not ((banned >> i) & 1)]
        if leftover:
            residual_after_7 += 1
            local.extend(leftover[:1])
        sz = len(local)
        if sz > best:
            best = sz
            print(
                f"good {n_good} V={a}/{b} cosets={sz} leftover={len(leftover)} total={49*sz}",
                flush=True,
            )
            lines.append(f"{a} {b} cosets={sz} leftover={len(leftover)}")
            if sz >= 8:
                keep = set(local)
                pts = [v for v in range(NVERTS) if cid[v] in keep]
                if first_conflict(pts) is None:
                    out = HERE / f"R{len(pts)}_cosets.txt"
                    out.write_text("\n".join(format_word(v) for v in pts) + "\n")
                    print(f"WROTE {out} verified {len(pts)}")
                    lines.append(f"wrote {out}")
                    break
                else:
                    print("FALSE PACK failed verify", flush=True)
                    lines.append("false pack")
        elif n_good % 20 == 0:
            print(f"  good={n_good} best={best} leftover_hits={residual_after_7}", flush=True)
    lines.append(f"good {n_good} tried {n_tried} best_cosets {best} leftover_hits {residual_after_7}")
    lines.append(f"seconds {time.time()-t0:.1f}")
    print(
        f"DONE good={n_good} best_cosets={best} leftover_hits={residual_after_7} "
        f"t={time.time()-t0:.1f}s"
    )
    (HERE / "coset_sample_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
