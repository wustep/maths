# Cursor Grok 2026-08-28 — Caccetta leftover holes through n=138

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
New leftover SAT lives in `problems/caccetta-haggkvist-k3/compute/q29/`.
q28 stays the n=137 store. q4 stays the n=73–108 store and the
F₄ certificate.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). Do not treat 0.3388 as published.

Leftover n=138 is closed: d=46, cubes k=46..90, 45 stored DRATs
after `drat-trim -l` (largest core k=48, 16.4 MB). Independent
`python3 verify_range.py --n-min 138 --n-max 138` reports 45
checked, 0 failures. Parent F₄ at 0.34645 and the q4 CKLS-fork
certificate at 0.34640 both still replay. Encoder regression
(including n=21 d=6 SAT and cyclic soundness at n=73 d=24) is
0 failures.

n=139 is not stored. Residue, not a bound. F₄ unchanged at
c=0.34640. Did not beat 0.3388. The conjecture 1/3 is open.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05
cd ../q29
./build_solvers.sh
python3 verify_range.py --n-min 138 --n-max 138
python3 regression.py
```
