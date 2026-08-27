# Cursor Grok 2026-08-27 — Caccetta leftover holes from n=124

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
New leftover SAT lives in `problems/caccetta-haggkvist-k3/compute/q15/`.
q14 stays the n=123 store. q4 stays the n=73–108 store and the
F₄ certificate.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). Do not treat 0.3388 as published.

Exact leftover hole n=124 is closed (39 stored pigeonhole DRATs).
First remaining hole n=125. F₄ unchanged at c=0.34640. Did not beat
0.3388. The conjecture 1/3 is open.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05
cd ../q15
./build_solvers.sh
python3 verify_range.py --n-min 124 --n-max 124
```
