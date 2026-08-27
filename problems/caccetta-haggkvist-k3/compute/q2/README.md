# Next exact holes after n=18

After the n=18 in-degree pigeonhole, the remaining exact orders
not implied by Hoàng–Reed or by HKN 0.3465 (nor by the stored F₄
certificate at 0.34645) begin at n=21, 24, 26, 27, … .

A d-outregular oriented graph on n vertices has n d arcs, so some
vertex has in-degree at least d. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ≥ d.

Those cubes are UNSAT, with stored DRATs, at

    n = 21, 24, 26, 27, 29, 30, 32, 33, 35, 36.

The numerical threshold is unchanged: c = 0.34645. The first
remaining hole is n=38, δ⁺=13.

`encode.py` is the q1 sequential-counter encoder. Replay:

```
./build_solvers.sh
./run_all.sh
```

A timeout on a later cube is an incomplete search, not a bound.
