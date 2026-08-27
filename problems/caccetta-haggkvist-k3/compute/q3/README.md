# Next exact holes after n=36

After the q2 pigeonhole certificates through n=36, the remaining
exact orders not implied by Hoàng–Reed or by HKN 0.3465 (nor by
the stored F₄ certificate at 0.34645) begin at n=38, δ⁺=13.
Then 39, 41, 42, 44, 45, … .

A d-outregular oriented graph on n vertices has n d arcs, so some
vertex has in-degree at least d. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ≥ d.

`encode.py` is the q1 sequential-counter encoder. Replay:

```
./build_solvers.sh
./run_all.sh
```

A timeout on a later cube is an incomplete search, not a bound.
The numerical threshold is unchanged unless a new F₄ certificate
appears: c = 0.34645.
