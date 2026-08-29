DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=149 onward. q38 stays the n=148 store.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

At leftover n=149: d=50, needed k=50..97 (48 cubes). k=98 is
empty by the N⁺ counting cut.

```
cd problems/caccetta-haggkvist-k3/compute/q39
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range log: `replay_149.json`.

F₄ stays in `../q4/` at c=0.34640.
