# q1 — leftover maximal-stratum thicken and the (19,3) row

The published census is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v3, §5.3). Seventeen more sit in
`../certs/new_schemes.json`, so the lower bound in this folder is
2,384. This campaign finishes the whole-stratum thicken that stopped
at 4 of 164 census triangulations, walks even Harnack splits along the
occupied (p, n) = (19, 3) depth-3 row (the two open M-schemes live
there), and looks next to the 237 twenty-oval certificates.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q1/run_all.sh
```

That re-checks the seventeen, compiles `q1/thicken`, and diffs it
against the parent `thickc` on a rank-6 triangulation.

## Searches

From the same directory, after `python3 prep.py` and `cc -O2 -o zonec zonec.c`
and `cc -O2 -o ballc ballc.c`:

```
gcc -O3 -march=native -o q1/thicken q1/thicken.c
python3 q1/thick_drive.py <w> 2 20 q1/thick_out 1
python3 q1/even_walk.py bfs q1/even_out/bfs.jsonl 200000
python3 q1/nest_walk.py <w> <seed> 400 q1/walk_out 12
python3 q1/m2_drive.py 4 q1/m2_out <w> 2
python3 q1/collect.py
```

A new scheme is a T-curve only after `python3 verify_new.py q1/certs/new_schemes.json`.
An incomplete search is not a lower bound.
