DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=136 onward. q26 stays the n=135 store.

n=136 is not stored. First remaining hole n=136, δ⁺=46.
Incomplete search is residue, not a bound.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q27
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_136.json` once n=136 is stored.

F₄ stays in `../q4/` at c=0.34640.
