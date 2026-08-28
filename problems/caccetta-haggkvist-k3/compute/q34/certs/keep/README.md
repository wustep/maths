DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=143 onward. q33 stays the n=142 store.

n=143 is stored (46 cubes, k=48..93). n=144 is stored
(47 cubes, k=48..94). First remaining hole n=145.

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
Independent range logs: `replay_143.json`, `replay_144.json`.

F₄ stays in `../q4/` at c=0.34640.
