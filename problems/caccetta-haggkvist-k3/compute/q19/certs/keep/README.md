DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=128 onward. q18 stays the n=127 store.

n=128 is stored (41 cubes, k=43..83). First remaining hole n=129.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q19
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_128.json`.

F₄ stays in `../q4/` at c=0.34640.
