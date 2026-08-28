# Cursor Grok 2026-08-28 — Caccetta leftover holes from n=137

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
New leftover SAT lives in `problems/caccetta-haggkvist-k3/compute/q28/`.
q27 stays the n=136 store. q4 stays the n=73–108 store and the
F₄ certificate.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). Do not treat 0.3388 as published.

Leftover n=137 is not stored: d=46, cubes k=46..89. Residue, not a
bound. F₄ unchanged at c=0.34640. Did not beat 0.3388. The
conjecture 1/3 is open.

Replay after certificates are stored:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05
cd ../q28
./build_solvers.sh
python3 verify_range.py --n-min 137 --n-max 137
```
