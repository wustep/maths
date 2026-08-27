# n=21 and the next exact holes

After the n=18 in-degree pigeonhole, the remaining exact orders
not implied by Hoàng–Reed or by HKN 0.3465 (nor by the stored F₄
certificate at 0.34645) are n=21, 24, 27, … . The first of those
is n=21, δ⁺=7: ⌈21/3⌉=7 < 0.3465·21=7.2765.

A 7-outregular oriented graph on 21 vertices has 147 arcs, so some
vertex has in-degree at least 7. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ∈ {7,…,13}.

`encode.py` is the q1 sequential-counter encoder. `--indeg0 k`
fixes N⁻(0)={8,…,7+k}.

Replay:

```
./build_solvers.sh
./run_all.sh
```

A timeout on a cube is an incomplete search, not a bound.
