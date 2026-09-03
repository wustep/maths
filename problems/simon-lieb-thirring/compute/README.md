# compute — simon-lieb-thirring

Replay the later record first:

```bash
cd problems/simon-lieb-thirring/compute/q2
./run_all.sh
```

That replays the three-lines integral (float, not a bound) and a
Clausen-series envelope of Carvalho Corso–Ried \(M_3\). Independent
Python and Rust both give

$$
M_3\le 0.371185695,\qquad
\frac{L_{1,1,1}}{L_{1,1,1}^{\mathrm{cl}}}\le 1.4465531.
$$

That matches arXiv:2403.04347v2 Corollary 1.7 (\(1.44655\)) and does
not go below it. Certificate: `q2/certs/m3_ccr.json`.

The q1 family-A pair is a separate, weaker handle:

```bash
cd problems/simon-lieb-thirring/compute/q1
./run_all.sh
```

That recertifies the paper's Lemma 11 second pair and the family-A pair
in `q1/opt_best_A.json`, writes slim JSON under `certs/c1_*.json`, and
runs an independent `rustc` verifier on each. Claimed number there:

$$
\mathcal{C}_1\le 0.373548,\qquad
\frac{L_{1,1}}{L_{1,1}^{\mathrm{cl}}}\le 1.45576.
$$

A trapezoid float (`q1/float_c1.py`) is not a bound. Lean conversion
only: `../lean/FhjnProp10Conversion.lean`.

Other conversions, versus the same record:

```bash
cd problems/simon-lieb-thirring/compute/q3
./run_all.sh
```

Weidl interpolation with the sharp $\gamma=1/2$ endpoint, Seiringer–Solovej
Airy absorption, a Neumann covering at $\gamma=1$, and a 1D test-potential
search. None of those beat $1.44655$. The script replays the q2 Clausen
envelope at the end.
