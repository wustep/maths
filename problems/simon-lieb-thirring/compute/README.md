# compute — simon-lieb-thirring

Replay entry point:

```bash
cd problems/simon-lieb-thirring/compute/q1
./run_all.sh
```

That recertifies the paper's Lemma 11 second pair and the family-A pair
in `q1/opt_best_A.json`, writes slim JSON under `certs/`, and runs an
independent `rustc` verifier on each certificate.

The claimed number is the worse of the two codes:

$$
\mathcal{C}_1\le 0.373548,\qquad
\frac{L_{1,1}}{L_{1,1}^{\mathrm{cl}}}\le 1.45576,\qquad
\frac{K_1}{K_1^{\mathrm{cl}}}\ge 0.47187.
$$

Certificates: `certs/c1_opt_best.json`, `certs/c1_lemma11_second.json`.
A trapezoid float (`q1/float_c1.py`) is not a bound. Lean conversion
only: `../lean/FhjnProp10Conversion.lean`.
