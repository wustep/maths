# q14 — finite-range reweighting at the aspect-10 split

The frozen q13 certificate proves the discrete mid-radius Rayleigh
quotient is at least $0.9119$ for aspect $R=10$ and $n=37$ geometric
bins. Its continuous reweighting step used the coarse range

$$
f_{\min}\leq\lambda_i\leq1,
\qquad
P(1-f_{\min}),\qquad P=\frac{q-1}{q+1},\quad q=10^{1/37}.
$$

The same proof has a smaller finite range. If $F_{ij}$ is the minimum
of $f(t)=(1+t^3)/(1+t^2)$ on a bin pair, then

$$
f_{\min}\leq F_{ij}\leq f(q^2/10)<1.
$$

Indeed, below the minimizer of $f$, each bin-pair right endpoint is at
least $q^2/10$; above it, each left endpoint is at most $1/q$; and
interval arithmetic checks $f(1/q)<f(q^2/10)$. Every row average is a
convex combination of entries of $F$.

The point that was missed in the earlier finite-range probe is that
$F_{ii}$ is a minimum over the whole same-bin ratio interval
$[1/q,1]$. Thus $F_{ii}=f(1/q)$, not $f(1)=1$.

More explicitly, let $p$ be the mid-radius weights and let
$\widetilde p$ be their reweighting by factors in $[1/q,q]$. The sharp
elementary comparison is

$$
\operatorname{TV}(p,\widetilde p)\leq\frac{q-1}{q+1}=P.
$$

The difference of the two expectations is at most total variation
times the range, so the loss is only

$$
P\bigl(f(q^2/10)-f_{\min}\bigr).
$$

This gives

$$
\beta_3>0.9089554231,\qquad \beta_3^{-1}<1.100164,
$$

and the mass-stationary cut $10/11$ still lies above this compact
bound. The HPS Section 7 chain therefore gives the printed inequality

$$
N_c<1.1002Z+3.932\,Z^{1/3}\qquad (Z\geq4).
$$

This strictly improves q13's printed $1.1006$ leading coefficient. It
reuses the completed $137{,}438{,}953{,}471$-face Gray certificate;
there is no new giant face dump. Python interval arithmetic, a
stdlib-only Decimal reconstruction, and an independent Rust program
replay the smaller reweighting loss. Each path deducts an additional
$10^{-12}$ for the frozen matrix's decimal representation, far above
the measured $6\times10^{-16}$ relative rebuild difference. The
bounded-excess conjecture remains open.

## Replay

```bash
PYTHON=/path/to/python-with-mpmath-and-scipy \
  problems/simon-ionization-excess/compute/q14/run_all.sh
```

The driver first validates q13's frozen matrix, face summary, and
aspect-cut premise, then verifies the q14 span estimate twice
independently and reruns the interval Section 7 printer. Exit 0
certifies the displayed inequality.
