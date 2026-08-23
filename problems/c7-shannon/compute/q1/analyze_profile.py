#!/usr/bin/env python3
"""Fiber profile of R367 and of Itty's 6th-power 1120-set (shape 5)."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import sys
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from c7_common import circ_dist, decode, format_word, closed_neighbors, NVERTS
from verify_set import load_set
URL_1120 = (
    "https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/"
    "main/CC_6_7_1120.txt"
)

PAIRS = (
    ((1, 3, 4, 4, 6), (2, 3, 5, 4, 6)),
    ((3, 4, 0, 3, 5), (2, 4, 6, 3, 5)),
    ((5, 3, 1, 3, 4), (5, 3, 2, 3, 5)),
    ((4, 4, 6, 1, 6), (5, 4, 6, 0, 6)),
    ((6, 0, 6, 4, 5), (6, 1, 6, 5, 5)),
    ((0, 3, 5, 6, 5), (6, 3, 5, 0, 5)),
    ((6, 4, 3, 4, 0), (6, 4, 2, 4, 6)),
    ((6, 4, 5, 3, 2), (6, 5, 5, 3, 1)),
)


def fibers(words, dim=5):
    out = []
    for ax in range(dim):
        c = [0] * 7
        for w in words:
            c[decode(w)[ax] if isinstance(w, int) else w[ax]] += 1
        out.append(c)
    return out


def main() -> None:
    seed = load_set(ROOT / "R367.txt")
    recon = load_set(ROOT / "R_reconstructed.txt")
    lines = []
    lines.append(f"R367 fibers {fibers(seed)}")
    lines.append(
        f"symdiff {sorted(format_word(v) for v in set(seed)^set(recon))}"
    )
    sset = set(seed)
    blockers = [[] for _ in range(NVERTS)]
    index = {s: i for i, s in enumerate(seed)}
    for i, s in enumerate(seed):
        for u in closed_neighbors(s):
            if u in index:
                continue
            blockers[u].append(i)
    single = [v for v in range(NVERTS) if v not in sset and len(blockers[v]) == 1]
    lines.append(f"single_blocker {len(single)} {[format_word(v) for v in single]}")

    path = HERE / "CC_6_7_1120.txt"
    if not path.exists():
        urllib.request.urlretrieve(URL_1120, path)
    words6 = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        words6.append(tuple(int(t) for t in line.split()))
    lines.append(f"1120 unique {len(set(words6))}")

    def adj6(a, b):
        if a == b:
            return False
        for i in range(6):
            if circ_dist(a[i], b[i]) > 1:
                return False
        return True

    conflict = None
    for i, a in enumerate(words6):
        for b in words6[i + 1 :]:
            if adj6(a, b):
                conflict = (a, b)
                break
        if conflict:
            break
    lines.append(f"1120 independent {conflict is None}")
    best = 0
    for drop in range(6):
        buckets = defaultdict(set)
        for w in words6:
            rest = w[:drop] + w[drop + 1 :]
            buckets[w[drop]].add(rest)
        sizes = [len(buckets.get(i, ())) for i in range(7)]
        lines.append(f"drop{drop} {sizes} max {max(sizes)}")
        best = max(best, max(sizes))
    lines.append(f"best_5_fiber {best}")

    # 10th-power gadget fibers
    R = {tuple(decode(w)) for w in seed}
    deleted = {r for r, _ in PAIRS}
    B = {w for w in R if w not in deleted}

    def Tmap(w):
        return ((2 - w[1]) % 7, w[3], w[0], (2 - w[2]) % 7, w[4])

    Xset = {Tmap(w) for w in R}
    Xset.discard((2, 4, 6, 3, 5))
    Xset.add((1, 5, 6, 3, 5))
    J0, J1 = {0, 5, 6}, {1, 2, 3, 4, 7}
    PH = [PAIRS[j][0] for j in J0] + [PAIRS[j][1] for j in J1]
    PV = [PAIRS[j][1] for j in J0] + [PAIRS[j][0] for j in J1]

    def conf(x, P):
        for y in P:
            if max(min((xi - yi) % 7, (yi - xi) % 7) for xi, yi in zip(x, y)) <= 1:
                return True
        return False

    A = {x for x in Xset if conf(x, PV)}
    D = {x for x in Xset if conf(x, PH)}

    def hj(x, j):
        use_q = (j in J0 and x in A) or (j in J1 and x in D)
        return PAIRS[j][1 if use_q else 0]

    def vj(x, j):
        use_q = (j in J0 and x in D) or (j in J1 and x in A)
        return PAIRS[j][1 if use_q else 0]

    rights = defaultdict(set)
    for b in B:
        rights[b].update(B)
    for x in Xset:
        for j in range(8):
            rights[hj(x, j)].add(x)
            rights[x].add(vj(x, j))
    mx = max(len(s) for s in rights.values())
    lines.append(f"10D left fibers nonempty {len(rights)} max {mx}")
    print("\n".join(lines))
    (HERE / "profile_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
