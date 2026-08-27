# C7 fifth power, 2026-08-27

Grok 4.6 on `cursor/c7-shannon-q2-d348`. Replayed the Polak–Schrijver
367-set, then finished two leftover shapes and enumerated the third.

No 368-set. The published record is still 367. Do not claim a new
$\Theta(C_7)$: $367^{1/5}$ is below the Lean-verified $3.258805$.

An independent set that misses a letter in any coordinate has size at
most 345, so a 368-set is 7-surjective. Hamming distance 11 from the
published 367-set is empty. The 8-coset census found no 8-pack among
97240 good 2-dimensional codes; 1280 quotient graphs hit a node cap
and are not a proof.

Replay: `python3 problems/c7-shannon/compute/verify_set.py problems/c7-shannon/compute/R367.txt --min-size 367`
and `python3 problems/c7-shannon/compute/q2/bound_support.py`.
Logs under `problems/c7-shannon/compute/q2/`.
