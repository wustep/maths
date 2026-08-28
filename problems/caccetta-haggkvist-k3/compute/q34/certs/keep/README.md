DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=143 onward. q33 stays the n=142 store.

First remaining hole n=143, δ⁺=48 (cubes k=48..93).

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q34
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_143.json` once n=143 is stored.

F₄ stays in `../q4/` at c=0.34640.
