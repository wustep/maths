DRAT proofs for exact Caccetta–Häggkvist triangle orders after n=36.

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

The index is `replay.json` after a successful `verify_keep.py`.
Soundness SAT models (cyclic degree, not a counterexample) are
checked in `regression.py` at n=38 d=12.
