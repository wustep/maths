# C7 fifth power, 2026-08-23

Grok 4.6 on `grok/c7-shannon`. Replayed the Polak–Schrijver 367-set, then
searched for a 368-set by writing six possible shapes and working backwards.

No 368-set. The published record is still 367. Do not claim a new
$\Theta(C_7)$: $367^{1/5}$ is below the Lean-verified $3.258805$.

Complete for two shapes: 3-letter support is impossible ($3\cdot 115=345$),
and the union of the 367-set with any translate has independence number 367.
The other shapes left incomplete searches, which are not a lower bound.

Replay: `python3 problems/c7-shannon/compute/verify_set.py problems/c7-shannon/compute/R367.txt --min-size 367`.
Logs under `problems/c7-shannon/compute/q1/`.
