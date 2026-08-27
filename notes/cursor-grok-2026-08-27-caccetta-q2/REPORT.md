# Cursor Grok 2026-08-27 — Caccetta q2

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
Search lives in `problems/caccetta-haggkvist-k3/compute/q2/`.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). The stored F₄ certificate at
c=0.34645 still replays. Did not beat 0.34645. Did not treat
0.3388 as published.

After the n=18 pigeonhole, the remaining exact orders begin at
n=21, 24, 26, 27, … . A d-outregular oriented graph has n d arcs,
so some in-degree is at least d. Each cube k=|N⁻(0)| ≥ d is UNSAT
with a stored DRAT at

    n = 21, 24, 26, 27, 29, 30, 32, 33, 35, 36.

The encoder is not empty: n=21 d=6 and n=24 d=7 still SAT, with
checked C₃-free models.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q2 && ./build_solvers.sh && ./run_all.sh
```

Certificate directory: `compute/q2/certs/keep/`.
First remaining hole: n=38, δ⁺=13. Conjecture 1/3 still open.
