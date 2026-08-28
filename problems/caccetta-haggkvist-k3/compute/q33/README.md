# Leftover exact holes from n=142

After the q32 pigeonhole certificates through n=141, the remaining
exact orders not implied by Hoàng–Reed or by HKN 0.3465 (nor by
the stored F₄ certificate at 0.34640) begin at n=142, δ⁺=48.

A d-outregular oriented graph on n vertices has n d arcs, so some
vertex has in-degree at least d. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ≥ d.

Cubes at leftover n=142 (d=48) run k=48..92 (45 cubes; k=93 empty
by the N⁺ counting cut). This folder stores those DRATs after an
independent replay.

The numerical threshold is unchanged: c = 0.34640 (CKLS 2015 fork).
It does not beat 0.3388.

`encode.py` is the q1 sequential-counter encoder. Replay:

```
./build_solvers.sh
./run_all.sh
```

The encoder is not empty: n=21 d=6 is SAT with a checked C₃-free
model. High-k cubes empty by a 2-cycle covering count on N⁺(0).
Oversized kissat proofs are replaced by `drat-trim` core lemmas
that still replay.
