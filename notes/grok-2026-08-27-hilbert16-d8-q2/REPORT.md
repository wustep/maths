# Hilbert 16(a) degree 8, q2, 2026-08-27

Grok 4.6 on the existing `problems/hilbert16-degree-8` folder,
starting from `origin/main` `6ae8676` (q1 wrap merged).

## Record

Re-fetched arXiv:2602.06888: still v3, 27 Jul 2026, 2,367 nonempty
degree-8 T-schemes. Parent 17/17 and q1 replay still green. Bound
still ≥ 2,384.

## Bound

Did not move unless a later certificate says otherwise.

## Scope

Radius-1 thicken of the twenty leftover census triangulations of
twist-rank 21–26, a three-split ladder on the published (19,3)
collections, odd collections of size 4, and a longer pinned
even-split walk.

Replay:

```
cd problems/hilbert16-degree-8/compute
sh run_all.sh
sh q2/run_all.sh
python3 q2/collect.py
```

## Results

Bound still ≥ 2,384. No `q2/certs/new_schemes.json`.

Rank 21 leftover thicken: **5/5 complete**, 482,344,960 evaluations,
evals = \(46\cdot 2^{21}\) on each, novel empty.
`problems/hilbert16-degree-8/compute/q2/certs/thick_r1_rank_21.json`.

Pinned even BFS, 400,000 collections: five published (19,3)
M-schemes, queue left 393,239. Residue.
`compute/q2/certs/even_pinned.json`.

Three-split ladder on the five published (19,3) collections:
2,719,977 evaluations, 30 known schemes, 0 new, 0 hits. Time cap
during the last seed. Residue. `compute/q2/certs/ladder3.json`.

Odd size 4: size 3 replayed 368,936 / 12 schemes. Size 4 snapshot
at 40/189, 3,740,056 evaluations, still those 12, 0 hits. Residue.
`compute/q2/certs/odd_skel4.json`.

Ranks 22–26 (15 triangulations) and both open nests remain.
