# Hilbert 16(a) degree 8, q3, 2026-08-27

Grok 4.6 on the existing `problems/hilbert16-degree-8` folder,
starting from `origin/main` `db98cb1` (q2 wrap merged).

## Record

Re-fetched arXiv:2602.06888: still v3, 27 Jul 2026, 2,367 nonempty
degree-8 T-schemes. Bound still ≥ 2,384. Rank 21 leftover finished
on main.

## Bound

Did not move. No `q3/certs/new_schemes.json`.

Rank 22 leftover thicken is 5/5, each with evals \(46\cdot 2^{22}\).
The rank-23 Harnack triangulation is also finished,
evals \(46\cdot 2^{23}\), 26 schemes. Novel empty on both.
Ranks 22 and 23 leftover thicken are finished (5/5 and 6/6).
Novel empty. Leftover ranks 22–26 are 11/15. Prefix only. Odd
collections of size 4 finished: twelve known M-schemes, no nest.

## Scope

Radius-1 thicken of the fifteen leftover census triangulations of
twist-rank 22–26, and the two open (19,3) nests. The only leftover
(19,3) census certificate is the rank-23 Harnack
`deg8/o22-p19-n03/(18v1(3)).pcom`.

Replay:

```
cd problems/hilbert16-degree-8/compute
sh run_all.sh
sh q3/run_all.sh
python3 q3/collect.py
```
