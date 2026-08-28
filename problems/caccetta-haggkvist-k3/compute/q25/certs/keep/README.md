DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=134 onward. q24 stays the n=133 store.

n=134 is the first remaining hole (d=45, cubes k=45..87).

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q25
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_134.json` once that order is stored.

F₄ stays in `../q4/` at c=0.34640.
