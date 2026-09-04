# q6 — leftover (19,3) nests

The current paper record is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v4, §4.3). Seventeen more are independently
verified in `../certs/new_schemes.json`, so the lower bound in this
folder starts at 2,384. The two algebraically open \((19,3)\) deep
nests remain the main targets.

q5 left two incomplete searches: 18,340,000 evaluations from the
37,632,123 compatible odd collections of size 5, and a pinned
even-split BFS whose queue was still growing. This folder continues
the odd first-index shards without repeating completed q5 blocks. It
replaces the even BFS with direct fixed-odd component counting and
enumeration, so it never writes a multi-gigabyte seen/queue pickle.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q6/run_all.sh
```

The replay rechecks the existing seventeen, the q5 collection
encoder, the exact even-component counts, and any q6 certificate. A
candidate is a T-curve only after

```
python3 verify_new.py q6/certs/new_schemes.json
```

accepts its primitive regular triangulation, exact lifting, signs,
and independently recomputed scheme.

## Long searches

```
sh q6/run_leftover.sh
python3 q6/even_small.py
```

The odd search is complete only when its aggregate certificate counts
all 37,632,123 size-5 collections. The even search records exactly
which fixed-odd components finish. Any unfinished component is search
residue, not a lower bound or an obstruction.
