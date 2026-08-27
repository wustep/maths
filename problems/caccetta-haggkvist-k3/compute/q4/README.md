# Leftover exact holes from n=73

After the q3 pigeonhole certificates through n=72, the remaining
exact orders not implied by Hoàng–Reed or by HKN 0.3465 (nor by
the stored F₄ certificate at 0.34645) begin at n=73, δ⁺=25.

A d-outregular oriented graph on n vertices has n d arcs, so some
vertex has in-degree at least d. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ≥ d.

`encode.py` is the q1 sequential-counter encoder. Replay:

```
./build_solvers.sh
./run_all.sh
```

A timeout on a later cube is an incomplete search, not a bound.
The encoder is not empty: n=21 d=6 is SAT with a checked C₃-free
model, and the n=73 circulant (degree 24) satisfies the cube
clauses after placing the neighbourhoods of 0.

High-k cubes empty by a 2-cycle covering count on N⁺(0)
(`count_obstruction.py`, notes in `certs/keep/combinatorial_notes.json`).
That count does not kill k near d. Those cubes are SAT-easy with
lex SB (n=73 k=25: 5244 conflicts, 1.08s) and hard without it.
