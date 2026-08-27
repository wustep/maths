# q1 — trial pairs for the FHJN functional C_1

Frank–Hundertmark–Jex–Nam, arXiv:1808.09017, Lemma 11 / Proposition 10.
An admissible pair $(f,\varphi)$ with $\int f^2=\int\varphi=1$ gives an
upper bound on $\mathcal{C}_1$, and at $d=1$

$$
\frac{K_1}{K_1^{\mathrm{cl}}}\ge\frac{16}{243\,\mathcal{C}_1^2},\qquad
\frac{L_{1,1}}{L_{1,1}^{\mathrm{cl}}}\le\frac{9\sqrt{3}}{4}\,\mathcal{C}_1.
$$

The published theorem is $L_{1,d}/L_{1,d}^{\mathrm{cl}}\le 1.456$.
That conversion drops below $1.456$ precisely when
$\mathcal{C}_1<1.456\cdot 4/(9\sqrt{3})\approx 0.373610$.

## Certified pair

`opt_best_A.json` / `certs/c1_opt_best.json`:

$$
f(t)=(1+\mu t^{\alpha})^{-\beta},\qquad
\varphi(t)=c\frac{(1-(t/S)^{\gamma})^{\delta}}{(1+\varepsilon t)^{\kappa}}\,1_{t\le S}
$$

with $(\alpha,\beta,\gamma,\delta,\varepsilon,\kappa,S)$ as in the JSON
and $\mu,c$ fixed by the two normalisations. Python panel bound
$\mathcal{C}_1\le 0.3735378$; Rust independent bound
$\mathcal{C}_1\le 0.3735472$. The number both support is
$\mathcal{C}_1\le 0.373548$, hence $L/L^{\mathrm{cl}}\le 1.45576$.

The paper's second pair is replayed in `certs/c1_lemma11_second.json`.
Its panel bound does not convert below $1.456$.

## Replay

```bash
./run_all.sh
```

`float_c1.py` prints a trapezoid estimate. It is not a bound.
