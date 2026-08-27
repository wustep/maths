DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=132 onward. q22 stays the n=131 store.

Work in this folder starts at n=132, δ⁺=44. Cubes are
k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q23
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range logs: `replay_N.json`.

F₄ stays in `../q4/` at c=0.34640.
