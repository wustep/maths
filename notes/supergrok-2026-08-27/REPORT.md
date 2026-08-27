# SuperGrok 2026-08-27

## Sidon second term

Continuation of the 2026-08-17 SuperGrok campaign on
`problems/sidon-second-term`. Search lives in `compute/q1/`.

Published record was Hou–Zhao arXiv:2607.01169v2,
$F(N)\le N^{1/2}+0.9435\,N^{1/4}+O(1)$.

q1 re-optimized the eight kernels as free symmetric histograms at
$L=6$. Exact certificate `compute/q1/certs/joint_r8_L6.json`:

    F(N) ≤ √N + 0.94325 N^{1/4} + O(1)

with √(ab) = 0.9432425309706136. This beats the published 0.9435.
Replay: `cd problems/sidon-second-term/compute/q1 && ./run_all.sh`.

Does not claim Erdős–Turán. No growing lower-bound second term.

## Caccetta–Häggkvist n=18

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

## kissing-5d / q1

Continuation of the five-dimensional kissing-number campaign.

Published range still $40\le\tau_5\le 44$ (Tao $C_{29}$, Cohn table,
Mittelmann–Vallentin). No unrestricted dual below 44. No 41-point code.

Certified in `problems/kissing-5d/compute/q1/`:

- Polar of each published 40-point code has $\max|x|^2=5/4<2$.
  $D_5,L_5,Q_5,R_5$ are maximal as spherical codes. C and Python
  enumerations agree. Replay `replay_max_vertex.py`.
- Integer Delsarte on the $Q_5$ angle set is empty at $N=44$
  ($14.7$ billion points, zero hits). Excludes size 44 in that class.

Replay: `sh problems/kissing-5d/compute/q1/run_all.sh`.

Does not claim $\tau_5=40$.

## affine-013 / q1

Continuation of the 2026-08-17 affine {0,1,3} campaign.
Search lives in `problems/affine-013/compute/q1/`.

Green #24 refetched (SHA-256 unchanged). Aaronson v4 still the
paper. Parent `compute/run_all.sh` replayed, exit 0.

The 1/2 bound did not move. Endpoint induction that would give 1/3
fails: both ends can exceed the 2/3 budget (n=5 already; an 11-set
scores 9/10) without beating the interval. No family with limsup
T/n² > 1/3. Conjecture 1/3 still open.

Replay: `cd problems/affine-013/compute/q1 && ./run_all.sh`.
Cert: `problems/affine-013/compute/q1/certs/q1.json`.
