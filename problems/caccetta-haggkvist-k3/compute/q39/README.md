# Leftover exact holes from n=149

After the q38 pigeonhole certificates through n=148, the remaining
exact orders not implied by Hoàng–Reed or by HKN 0.3465 (nor by
the stored F₄ certificate at 0.34640) begin at n=149, δ⁺=50.

A d-outregular oriented graph on n vertices has n d arcs, so some
vertex has in-degree at least d. Relabel that vertex as 0. The
exact statement reduces to cubes k=|N⁻(0)| ≥ d.

At leftover n=149 that is d=50 and k=50..97 (48 cubes). k=98 is
empty by the N⁺ counting cut: each v ∈ N⁺(0) needs d out-neighbours
from (N⁺(0)\{v}) ∪ U, of size n-2-k, so k ≤ n-2-d = 97. The
2-cycle covering count on A further empties k≥73, but those cubes
still get stored DRATs. The SAT work is k=50..72.

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
