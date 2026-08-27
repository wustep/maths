# Cursor Grok 2026-08-27 — Caccetta leftover holes

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
Search lives in `problems/caccetta-haggkvist-k3/compute/q3/`.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). The stored F₄ certificate at
c=0.34645 still replays. A second F₄ Cauchy–Schwarz block on the
non-edge type did not move the number. Did not beat 0.34645. Did
not treat 0.3388 as published.

After the q2 certificates through n=36, the remaining exact orders
begin at n=38, δ⁺=13. A d-outregular oriented graph has n d arcs,
so some in-degree is at least d. Each cube k=|N⁻(0)| ≥ d is UNSAT
with a stored DRAT at every leftover order through n=72.

The encoder is not empty: n=21 d=6 is SAT with a checked C₃-free
model, and the n=38 circulant (degree 12) satisfies the cube
clauses after placing the neighbourhoods of 0.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q2 && ./build_solvers.sh && ./run_all.sh
cd ../q3 && ./build_solvers.sh && ./run_all.sh
```

Certificate directory: `compute/q3/certs/keep/`.
First remaining hole: n=73, δ⁺=25. Conjecture 1/3 still open.
