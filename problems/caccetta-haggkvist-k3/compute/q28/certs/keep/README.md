DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=137 onward. q27 stays the n=136 store.

n=137 is not stored. First remaining hole n=137, δ⁺=46.
Incomplete search is residue, not a bound.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q28
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_137.json` once n=137 is stored.

F₄ stays in `../q4/` at c=0.34640.
