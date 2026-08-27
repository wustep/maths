# C7 fifth power, 2026-08-27 q3

Grok 4.6 on `cursor/c7-shannon-q3-e7c3`. Replayed the Polak–Schrijver
367-set, then finished the leftover 8-coset Cayley graphs.

No 368-set. The published record is still 367. Do not claim a new
$\Theta(C_7)$: $367^{1/5}$ is below the Lean-verified $3.258805$.

The $97240$ good $2$-dimensional codes are $9584$ unique connection
sets. None has eight independent cosets. Hamming $13$ is empty when
an added vertex has $5$ or $6$ blockers.

Replay: `python3 problems/c7-shannon/compute/verify_set.py problems/c7-shannon/compute/R367.txt --min-size 367`
and `sh problems/c7-shannon/compute/q3/run_q3.sh`.
Logs under `problems/c7-shannon/compute/q3/`.
