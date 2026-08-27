# Leftover exact holes from n=38

After the q2 pigeonhole certificates through n=36, the remaining
exact orders not implied by Hoàng–Reed or by HKN 0.3465 (nor by
the stored F₄ certificate at 0.34645) begin at n=38, δ⁺=13.

A d-outregular oriented graph on n vertices has n d arcs, so some
vertex has in-degree at least d. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ≥ d.

Those cubes are UNSAT, with stored DRATs, at every leftover order
through n=72:

    38, 39, 41, 42, 44, 45, 47, 48, 50, 51, …, 72.

The numerical threshold is unchanged: c = 0.34645. The first
remaining hole is n=73, δ⁺=25.

`encode.py` is the q1 sequential-counter encoder. Replay:

```
./build_solvers.sh
./run_all.sh
```

A timeout on a later cube is an incomplete search, not a bound.
