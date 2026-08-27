DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=115 onward. q5 stays the n=109–114 store.

n=115 is stored (36 cubes, k=39..74). First remaining hole n=116.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q6
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_115.json`.

F₄ stays in `../q4/` at c=0.34640.
