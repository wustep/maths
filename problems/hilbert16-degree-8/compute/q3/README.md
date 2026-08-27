# q3 — leftover ranks 22–26 and the open (19,3) nests

The published census is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v3, §5.3). Seventeen more sit in
`../certs/new_schemes.json`, so the lower bound in this folder is
2,384. q1 finished the radius-1 thicken of every leftover census
triangulation of twist-rank at most 20. q2 finished the five of
rank 21. Fifteen leftover triangulations of ranks 22–26, and the
two open (19,3) deep nests, remain.

The only leftover (19,3) census certificate is the rank-23 Harnack
triangulation `deg8/o22-p19-n03/(18v1(3)).pcom`.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q3/run_all.sh
```

That re-checks the seventeen, compiles `q3/thicken`, and diffs it
against the parent `thickc` on a rank-6 triangulation.

## Searches

From the same directory, after `python3 prep.py`:

```
gcc -O3 -march=native -o q3/thicken q3/thicken.c
python3 q3/thick_drive.py 0 2 22 26 q3/thick_out 1 --prefer-193
python3 q3/ladder3.py q3/dn_out/ladder3_depth3.jsonl 10800 depth3
python3 q3/odd_skel.py 4 q3/even_out/odd_skel4.jsonl
python3 q3/even_walk.py bfs q3/even_out/bfs.jsonl 800000
python3 q3/collect.py
```

A new scheme is a T-curve only after `python3 verify_new.py q3/certs/new_schemes.json`.
An incomplete search is not a lower bound.

## What this run found

See `certs/` after `collect.py`. The bound does not move unless a
certificate sits outside the published 2,367 and the seventeen
already stored, and then only after the exact verifier.
