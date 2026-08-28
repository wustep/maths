DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=135 onward. q25 stays the n=134 store.

n=135 is not stored. First remaining hole n=135, δ⁺=45.
Incomplete search is residue, not a bound.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q26
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_135.json` once n=135 is stored.

F₄ stays in `../q4/` at c=0.34640.
