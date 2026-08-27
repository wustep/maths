DRAT proofs for the remaining exact Caccetta–Häggkvist triangle
orders through n=36.

A d-outregular oriented graph on n=3d vertices has n d arcs, so
some in-degree is at least d. The same pigeonhole applies at the
nearby holes n=3d−1. Relabel that vertex as 0. The exact statement
reduces to cubes k=|N⁻(0)| ≥ d. Each cube is UNSAT with a stored
DRAT. Replay regenerates the CNF from `encode.py` and checks the
proof; do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q2
./build_solvers.sh
./run_all.sh
```

Orders stored: 21, 24, 26, 27, 29, 30, 32, 33, 35, 36.
The index is `replay.json` after a successful `verify_keep.py`.
Soundness SAT models (cyclic degree, not a counterexample) live
in `soundness_n21_d6*.json` and `soundness_n24_d7_k7.json`.
