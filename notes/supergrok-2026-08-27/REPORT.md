# SuperGrok 2026-08-27

Continuation of the five-dimensional kissing-number campaign.

## kissing-5d / q1

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
