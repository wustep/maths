# q2 — leftover high-rank thicken and the next (19,3) moves

The published census is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v3, §5.3). Seventeen more sit in
`../certs/new_schemes.json`, so the lower bound in this folder is
2,384. q1 finished the radius-1 thicken of every leftover census
triangulation of twist-rank at most 20. Twenty census triangulations
of ranks 21–26 were never in that leftover, and the two open (19,3)
nests are still undecided.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q2/run_all.sh
```

That re-checks the seventeen, compiles `q2/thicken`, and diffs it
against the parent `thickc` on a rank-6 triangulation.

## Searches

From the same directory, after `python3 prep.py`:

```
gcc -O3 -march=native -o q2/thicken q2/thicken.c
python3 q2/thick_drive.py <w> 2 21 26 q2/thick_out 1
python3 q2/ladder3.py q2/dn_out/ladder3.jsonl 7200 193
python3 q2/odd_skel.py 4 q2/even_out/odd_skel4.jsonl
python3 q2/even_walk.py bfs q2/even_out/bfs.jsonl 400000
python3 q2/collect.py
```

A new scheme is a T-curve only after `python3 verify_new.py q2/certs/new_schemes.json`.
An incomplete search is not a lower bound.

## What this run found

The bound did not move. The seventeen still verify; nothing new
appeared.

Finished, with certificates under `certs/`:

- Radius-1 leftover thicken of all five census triangulations of
  twist-rank 21 (482,344,960 evaluations, exactly \(46\cdot 2^{21}\)
  on each). Every scheme is already in the published 2,367.

Also recorded, incomplete:

- A 400,000-collection even-split walk that never drops an odd
  split (only the five published (19,3) M-schemes; queue left
  393,239).
- Three-split moves around those five collections (2,719,977
  evaluations; 30 known schemes; time cap during the last seed).
- Odd collections of size 4, snapshot at 40 of 189 (size 3 matches
  the q1 count; still the same twelve M-schemes).

Fifteen leftover triangulations of ranks 22–26 are still open.
Neither open nest is decided. Hilbert 16(a) degree 8 is still open.
