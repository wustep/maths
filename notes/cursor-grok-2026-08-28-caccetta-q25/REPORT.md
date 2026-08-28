# Cursor Grok 2026-08-28 — Caccetta leftover holes from n=134

Continuation of the Caccetta–Häggkvist directed-triangle campaign.
New leftover SAT lives in `problems/caccetta-haggkvist-k3/compute/q25/`.
q24 stays the n=133 store. q4 stays the n=73–108 store and the
F₄ certificate.

Published unrestricted threshold is still HKN 0.3465
(arXiv:0908.2791v4, Theorem 1.2). Do not treat 0.3388 as published.

Leftover n=134 is closed: d=45, cubes k=45..87, 43 stored DRATs.
Independent replay `python3 verify_range.py --n-min 134 --n-max 134`
reports 43 checked, 0 failures, every row `drat==VERIFIED`. Largest
core is k=46 at 15.5 MB. First remaining hole n=135, δ⁺=45.
n=135 is not stored: residue, not a bound. F₄ unchanged at
c=0.34640. Did not beat 0.3388. The conjecture 1/3 is open.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q4
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json --margin 0.05
cd ../q25
./build_solvers.sh
python3 verify_range.py --n-min 134 --n-max 134
```
