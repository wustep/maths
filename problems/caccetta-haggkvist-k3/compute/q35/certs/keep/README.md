DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=145 onward. q34 stays the n=143–144 store.

n=145 is stored (46 cubes, k=49..94). First remaining hole n=146.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q35
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_145.json`.

F₄ stays in `../q4/` at c=0.34640.
