# C7 fifth power, 2026-08-27 q4

Grok 4.6 on `cursor/c7-shannon-q4-6983`. Replayed the Polak–Schrijver
367-set, then hunted a 368-set of a new shape.

No 368-set. The published record is still 367. Do not claim a new
$\Theta(C_7)$: $367^{1/5}$ is below the Lean-verified $3.258805$.

Hamming $13$ around the published seed is now empty (case C plus
Cadical UNSAT on the $\le 3$-blocker leftover). One-dimensional
good-code packs reached $46$ cosets, not $53$. Cyclic $5$-orbit
and negation-pair SAT instances did not finish.

Replay: `python3 problems/c7-shannon/compute/verify_set.py problems/c7-shannon/compute/R367.txt --min-size 367`
and `sh problems/c7-shannon/compute/q4/run_q4.sh`.
Logs under `problems/c7-shannon/compute/q4/`.
