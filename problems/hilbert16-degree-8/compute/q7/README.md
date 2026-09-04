# q7 — leftover (19,3) nests

The current paper record is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v4, §4.3). Seventeen more are independently
verified in `../certs/new_schemes.json`, so the lower bound in this
folder starts at 2,384. The two algebraically open (19,3) deep nests
remain the main targets.

q5 left two incomplete searches: 18,340,000 evaluations from the
37,632,123 compatible odd collections of size 5, and a pinned
even-split BFS whose queue was still growing. This folder finishes
the odd first-index space in C rather than resuming Python shards,
and replaces the even BFS with direct fixed-odd component counting
and enumeration. It never writes a multi-gigabyte seen/queue pickle.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q7/run_all.sh
```

A candidate is a T-curve only after

```
python3 verify_new.py q7/certs/new_schemes.json
```

accepts its primitive regular triangulation, exact lifting, signs,
and independently recomputed scheme.

## Long searches

```
sh q7/run_leftover.sh
```

The odd search is complete only when its aggregate certificate counts
all 37,632,123 size-5 collections. The even search records exactly
which fixed-odd components finish. The a=10 component has 126,336
collections; the nested-box a=17 component has 25,292,736. The other
nonempty-odd components are larger than 10^10 and are counted, not
enumerated. Any unfinished component is search residue, not a lower
bound or an obstruction.
