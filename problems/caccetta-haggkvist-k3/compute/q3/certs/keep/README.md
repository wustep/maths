DRAT proofs for exact Caccetta–Häggkvist triangle orders from n=38
through n=72.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q3
./build_solvers.sh
./run_all.sh
```

Orders stored: 38, 39, 41, 42, 44, 45, 47, 48, and 50 through 72.
The n ≡ 1 (mod 3) values 40, 43, 46, 49 are already implied by
HKN 0.3465. The index is `replay.json` after a successful
`verify_keep.py`. Circulant soundness (cyclic degree, not a
counterexample) is `soundness_n38_d12.json`.
