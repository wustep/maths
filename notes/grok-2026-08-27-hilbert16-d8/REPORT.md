# Hilbert 16(a) degree 8, 2026-08-27

Grok 4.6 on the existing `problems/hilbert16-degree-8` folder.

## Record

Re-fetched arXiv:2602.06888: still v3, 27 Jul 2026, 2,367 nonempty
degree-8 T-schemes. Parent replay: 2,367/2,367 and 17/17. Bound still
≥ 2,384.

## Bound

Did not move. No new T-curve scheme.

## Finished

- Radius-4 balls around all 237 twenty-oval census certificates.
- Odd Harnack-split collections of size at most 3.
- Pinned even-split BFS (200,000 collections; queue not exhausted).
- One-split neighbourhood of all 38 published M-collections: those
  38 schemes only.
- Nested odd pairs on the five published (19,3) collections. The
  a=10 nest admits no compatible nested odd pair.
- Radius-1 thicken of every leftover census triangulation of
  twist-rank at most 20 (164/164, 1,438,512,000 evaluations).
  Only rediscovery of schemes already among the seventeen.
- One-split neighbourhood of all 38 published M-collections, and
  the two-split ladder around all 12 depth-3 M-collections.
- Radius-6 balls around the eleven of our seventeen certificates
  whose ball leaves the old region.

Replay:

```
cd problems/hilbert16-degree-8/compute
sh run_all.sh
sh q1/run_all.sh
python3 q1/collect.py
```

Hilbert 16(a) in degree 8 remains open. The leftover thicken of
all 164 rank-at-most-20 census triangulations is finished and
added nothing. The two open deep nests are unfinished. The twenty
census triangulations of rank 21–26 were never in that leftover.
