# q4 — leftover (19,3) nests

The published census is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v3, §5.3). Seventeen more sit in
`../certs/new_schemes.json`, so the lower bound in this folder is
2,384. q1–q3 finished the radius-1 leftover thicken of every leftover
census triangulation of twist-rank at most 26. The two open (19,3)
deep nests remain.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q4/run_all.sh
```

That re-checks the seventeen and the bow-tie collection.

## Searches

From the same directory, after `python3 prep.py`:

```
python3 q4/ladder3.py q4/dn_out/ladder3_193.jsonl 0 193
python3 q4/ladder3.py q4/dn_out/ladder3_depth3.jsonl 0 depth3
python3 q4/even_walk.py bfs q4/even_out/bfs.jsonl 1200000
python3 q4/odd_skel.py 5 q4/even_out/odd_skel5.jsonl
python3 q4/write_certs.py
python3 q4/collect.py
```

A new scheme is a T-curve only after `python3 verify_new.py q4/certs/new_schemes.json`.
An incomplete search is not a lower bound.

## What this run found

See `certs/` after `collect.py`. The bound does not move unless a
certificate sits outside the published 2,367 and the seventeen
already stored, and then only after the exact verifier.
