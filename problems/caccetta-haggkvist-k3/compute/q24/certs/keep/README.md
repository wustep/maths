DRAT proofs for exact Caccetta–Häggkvist triangle leftover orders
from n=133 onward. q23 stays the n=132 store.

Work in this folder starts at n=133, δ⁺=45. Cubes are
k=|N⁻(0)| ≥ d. Each stored cube is UNSAT with a DRAT.
Replay regenerates the CNF from `encode.py` and checks the proof;
do not trust leftover `certs/*.cnf` scratch files.

```
cd problems/caccetta-haggkvist-k3/compute/q24
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Independent range logs: `replay_N.json`.

F₄ stays in `../q4/` at c=0.34640.
