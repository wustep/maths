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

## kissing-5d / q2

Continuation the same day. Search lives in `compute/q2/`.

Published range still $40\le\tau_5\le 44$ (Tao $C_{29}$, Cohn table,
Mittelmann–Vallentin $s_{14}(5)=44.998\ldots$). The unaffiliated
Zenodo $44.0297$ note is retracted.

Replayed first: `compute/certs/restricted_delsarte.json` (bounds 42
and $239925/5456$) and the q1 polar / $T_{Q_5}$ integer certificates.

No unrestricted dual below 44. Numerical Delsarte is $46.3368\ldots$.
Exact $(t-1/2)q(t)^2$ duals exist (best searched $53235/1109\approx 48.003$).
No 41-point code. Finite graphs with no 41-clique: the 355-point $T^5$
remainder, the 200-point half-integer sphere, the 320-point $Q_5$-cap
orbit. The 36-clique hunt that would give a 41-set via five universal
basis vectors, and the 1480-point $(1/4)\mathbb Z^5$ graph, did not
finish.

Replay: `sh problems/kissing-5d/compute/q2/run_all.sh`.

Does not claim $\tau_5=40$. The unrestricted interval did not move.

## union-closed / q1

Continuation of the 2026-08-17 SuperGrok campaign on
`problems/union-closed`. Search lives in `compute/q1/`.

Published quoted constant is still Liu arXiv:2306.08824,
0.382709 under two numerical hypotheses. The 2026-08-17 repo
number on `{b,1}` was 0.38285 at mix weight `β = 1/5`.

On that same family, pure Example 4 (`β = 1`) has first-crossing
equal to the critical point of `1 − (1−b)h(b)`:

    h(b) = (1−b) log₂((1−b)/b)

which evaluates to 0.3830513565868…. Certified 5-decimal constant
0.38304; mesh min ratio 1.000021687 (Python and C). Replay
`cd problems/union-closed/compute/q1 && ./run_all.sh`.

Does not claim 1/2. Does not claim every measure on [0,1].

## two-smooth-summands / q1

Continuation of the 2026-08-17 campaign. Search lives in
`problems/two-smooth-summands/compute/q1/`.

Published record still Balog 1989,
$F(n)\ll_\varepsilon n^{4/(9\sqrt{e})+\varepsilon}$. Green #59 and
Erdős #334 still open. No exponent below Balog. No infinite covering
at any $\varepsilon<1/2$.

Certified in that folder: closed-form templates fail through
$n=20000$ at $9/20$, $2/5$, $1/3$, $27/100$; floor-divisor and
largest-power-of-two have explicit infinite failure families;
polynomial values of degree $d\ge 2$ cannot beat the square covering
by size; two-factor $u\le n^{1/5}$ matches the known $F$ exception
prefixes (sixteen at $2/5$, last $479$; seventy-six at $1/3$, last
$18191$).

Replay:

```
cd problems/two-smooth-summands/compute
python3 verify_all.py
cc -O3 -std=c11 -o g_of_y_c g_of_y.c
./g_of_y_c 61 6077111 200000
cd q1 && ./run_all.sh
```

Does not claim Green #59.

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

## long-gap-dilate / q1

Continuation of the 2026-08-17 SuperGrok start on Green #32.
Search lives in `problems/long-gap-dilate/compute/q1/`.

Fetched Green #32 and Shakan arXiv:2004.14828 before searching.
The list id arXiv:2205.14038 is the Weyl-equation paper, not Shakan.
Parent `compute/run_all.sh` still replays.

Did not beat Shakan’s universal 2. Rising-factorial Alon degrees
equal the worst-case $k$ on $p=11,13$. Exact $G(73,9)=24$ (Cadical
unsat at $T=24$). SAT upper bounds $G(79,9)\le 26$,
$G(83,9)\le 27$, $G(89,9)\le 30$. No $C\to 2$ family through
$p=199$.

Replay:

```
cd problems/long-gap-dilate && sh compute/run_all.sh
cd compute/q1 && ./run_all.sh
```
