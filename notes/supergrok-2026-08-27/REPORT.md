# SuperGrok / Grok 4.6, 2026-08-27

Caccetta–Häggkvist directed triangles, `problems/caccetta-haggkvist-k3/compute/q1`.

Published unrestricted threshold is still HKN 0.3465. The stored F4
certificate at c=0.34645 still replays. Did not beat 0.34645. Did not
treat 0.3388 as published.

Exact statement at n=18, δ⁺=6: a 6-outregular oriented graph has 108
arcs, so some vertex has in-degree at least 6. The SAT cubes for
k=|N⁻(0)| in {6,7,8,9,10,11} are each DRAT-unsatisfiable. Those six
proofs are stored in `compute/q1/certs/keep/`. So every 18-vertex
oriented graph of minimum out-degree 6 has a directed triangle.

Did not improve the numerical threshold 0.34645. Conjecture 1/3 still
open. The leftover k=0 search is unused.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q1 && ./build_solvers.sh && ./run_all.sh
```
