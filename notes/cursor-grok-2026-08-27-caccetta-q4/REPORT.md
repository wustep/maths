# Cursor Grok 2026-08-27 — Caccetta leftover holes from n=73

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
Search lives in `problems/caccetta-haggkvist-k3/compute/q4/`.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). Do not treat 0.3388 as published.

Exact leftover holes n=73 through n=108 are closed (1026 stored
pigeonhole DRATs). First remaining hole n=109. F₄ moved to
c=0.34640 via the CKLS 2015 fork (β<0.8616γ). Did not beat 0.3388.
The conjecture 1/3 is open.

Wrapped after merging `origin/main`. README keeps the later
notebook claims together with leftover CH through n=108 and
F₄ c=0.34640. n=109 was started and interrupted; not stored.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4
./build_solvers.sh
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05
./run_all.sh
```
