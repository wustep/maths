# Hilbert 16(a) degree 8, q4, 2026-08-29

Grok 4.6 on the existing `problems/hilbert16-degree-8` folder,
starting from `origin/main` `b93fded` (q3 wrap merged).

## Record

Re-fetched arXiv:2602.06888: still v3, 27 Jul 2026, 2,367 nonempty
degree-8 T-schemes. Bound still ≥ 2,384. Leftover ranks 22–26
finished on main.

## Bound

Did not move. No `q4/certs/new_schemes.json`.

## Scope

The two open (19,3) nests, and any further collection-space
neighbourhood that could add a scheme outside the seventeen.
q1–q3 finished the leftover radius-1 thicken through rank 26.

Replay:

```
cd problems/hilbert16-degree-8/compute
sh run_all.sh
sh q4/run_all.sh
python3 q4/collect.py
```
