# q2 — Carvalho Corso–Ried \(M_3\)

Replay:

```bash
cd problems/simon-lieb-thirring/compute/q2
./run_all.sh
```

That runs a trapezoid replay of the three-lines integral in
`replay_m3.py` (not a bound), then a directed Clausen-series envelope
in Python and an independent `rustc` recomputation.

The published later record is Carvalho Corso–Ried, arXiv:2403.04347v2,
Corollary 1.7:

$$
\frac{L_{1,1,1}}{L_{1,1,1}^{\mathrm{cl}}}\le 1.44655
$$

from \(M_3=0.371185695\). Carvalho Corso, arXiv:2407.10117v2,
Corollary 1.8 writes the same bound as a Clausen value and rounds it to
\(1.447\). This folder independently encloses that Clausen value. It
does not claim a number below \(1.44655\).

q1 family-A certificates stay under `../certs/c1_*.json`. This folder
writes `certs/m3_ccr.json` so the q1 glob does not pick it up.
