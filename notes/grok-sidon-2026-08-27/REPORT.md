# Grok 2026-08-27 — Sidon second term, q2

Continuation of the 2026-08-27 q1 campaign on
`problems/sidon-second-term`. Search lives in `compute/q2/`.

Published record is still Hou–Zhao arXiv:2607.01169v2,
$F(N)\le N^{1/2}+0.9435\,N^{1/4}+O(1)$. Folder record was the q1
certificate $C<0.94325$.

q1 leftover refine / dropped-symmetry never finished. An L-lift of
the q1 kernels saturates. Block descent and extra free histograms at
$m=32$ saved only $2\times 10^{-7}$. Resampling the grown mix to
$m=48$ and re-blocking produced the exact certificate
`compute/q2/certs/r11_m48_L6.json`:

    F(N) ≤ √N + 0.94301 N^{1/4} + O(1)

with √(ab) = 0.943006169985179. This beats the folder 0.94325 and
Hou–Zhao 0.9435.

Does not claim Erdős–Turán. No growing lower-bound second term.

Replay: `cd problems/sidon-second-term/compute/q2 && ./run_all.sh`.
