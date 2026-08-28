# Cursor Grok 2026-08-28 — Caccetta leftover holes from n=135

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
New leftover SAT lives in `problems/caccetta-haggkvist-k3/compute/q26/`.
q25 stays the n=134 store. q4 stays the n=73–108 store and the
F₄ certificate.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). Do not treat 0.3388 as published.

Leftover n=135 is not stored: d=45, cubes k=45..88. Residue, not a
bound. F₄ unchanged at c=0.34640. Did not beat 0.3388. The
conjecture 1/3 is open.

Replay after certificates are stored:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05
cd ../q26
./build_solvers.sh
python3 verify_range.py --n-min 135 --n-max 135
```
