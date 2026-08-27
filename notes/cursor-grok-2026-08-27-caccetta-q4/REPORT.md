# Cursor Grok 2026-08-27 — Caccetta leftover holes from n=73

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
Search lives in `problems/caccetta-haggkvist-k3/compute/q4/`.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). The stored F₄ certificate at
c=0.34645 is the starting numerical number. Do not treat 0.3388
as published.

After the q3 certificates through n=72, the remaining exact orders
begin at n=73, δ⁺=25. A d-outregular oriented graph has n d arcs,
so some in-degree is at least d. Cubes k=|N⁻(0)| ≥ d are the
search.

Replay (after certificates exist):

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4 && ./build_solvers.sh && ./run_all.sh
```
