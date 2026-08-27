# SuperGrok 2026-08-27 — Sidon second term

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
