# SuperGrok / Grok 4.6, 2026-08-27

Caccetta–Häggkvist directed triangles, `problems/caccetta-haggkvist-k3/compute/q1`.

Published unrestricted threshold is still HKN 0.3465. The stored F4
certificate at c=0.34645 still replays. Did not beat 0.34645. Did not
treat 0.3388 as published.

Exact statement at n=18, δ⁺=6: sequential-counter encoding, split on
k=|N⁻(0)|. Cubes k=1 and k=6..11 are DRAT-unsatisfiable (k=1 is a
1.2 GB proof, hashed, not stored). Cubes k=2..5 unsatisfiable with
verified-then-dropped large proofs. Leftover: k=0 with
t=|N⁺(1) ∩ U|=6. Incomplete SAT is not a bound.

Replay:

```
cd problems/caccetta-haggkvist-k3/compute
python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
cd q1 && ./build_solvers.sh && ./run_all.sh
```
