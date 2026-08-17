#!/usr/bin/env python3
"""Classify each Ulam step as Eggleton / Type I / Type II / other.

Used to hunt extra forbidden majorant words beyond T3 T3.  A transition
that never occurs in the actual sequence is not automatically forbidden
for the majorant (the majorant may take Type I/II even when the true
step is 'other').  A transition that *cannot* occur by the same unique-
representation bookkeeping as CS Lemma 2 *is* a legal extra restriction.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ulam import ulam_first

HERE = Path(__file__).resolve().parent


def classify(seq: list[int]) -> list[str]:
    labels = ["seed", "seed"]
    for n in range(2, len(seq) - 1):
        # seq is 0-indexed; current last index is n, next is n+1
        an = seq[n]
        nxt = seq[n + 1]
        if nxt == an + seq[n - 2]:
            labels.append("E")
        elif nxt == an + seq[n - 3]:
            labels.append("I")
        elif nxt == seq[n - 1] + seq[n - 2]:
            labels.append("II")
        else:
            labels.append("O")
    return labels


def main() -> None:
    seq = ulam_first(20000)
    lab = classify(seq)
    steps = lab[2:]  # one label per produced term after the seeds
    counts = Counter(steps)
    pairs = Counter(zip(steps, steps[1:]))
    triples = Counter(zip(steps, steps[1:], steps[2:]))
    # Eggleton twice in a row must be absent (CS Lemma 2).
    ee = pairs.get(("E", "E"), 0)
    report = {
        "N": len(seq),
        "counts": dict(counts),
        "pairs": {f"{a}->{b}": c for (a, b), c in sorted(pairs.items())},
        "triples_top": [
            {"word": "".join(w), "count": c}
            for w, c in triples.most_common(30)
        ],
        "eggleton_twice": ee,
        "eggleton_indices": [i + 3 for i, x in enumerate(steps) if x == "E"],
        "first_other_examples": [],
    }
    # Record a few 'other' identities.
    others = []
    for n in range(2, min(len(seq) - 1, 5000)):
        if lab[n] != "O":
            continue
        nxt = seq[n + 1]
        # find the unique pair
        S = set(seq[: n + 1])
        pairs_found = []
        for u in seq[: n + 1]:
            v = nxt - u
            if v > u and v in S:
                pairs_found.append((u, v))
        others.append({"n": n + 1, "a_n": seq[n], "a_next": nxt, "reps": pairs_found})
        if len(others) >= 12:
            break
    report["first_other_examples"] = others
    out = HERE / "step_classify.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("N", "counts", "pairs", "eggleton_twice")}, indent=2))


if __name__ == "__main__":
    main()
