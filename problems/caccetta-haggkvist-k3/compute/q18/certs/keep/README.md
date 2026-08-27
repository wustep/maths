DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=127 onward. q17 stays the n=126 store.

n=127 is stored (40 cubes, k=43..82). First remaining hole n=128.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q18
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_127.json`.

F₄ stays in `../q4/` at c=0.34640.
