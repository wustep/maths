DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=147 onward. q36 stays the n=146 store.

First remaining hole n=147, δ⁺=49 (cubes k=49..96).

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q37
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_147.json` once n=147 is stored.

F₄ stays in `../q4/` at c=0.34640.
