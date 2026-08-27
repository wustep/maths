# Attack log — simon-lieb-thirring

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-27

Fetched the record (arXiv:1808.09017v1 / JEMS 23 (2021); surveys 2007.09326, 2203.06051; DLL 0708.1165). No later paper opened tonight states $L_{1,d}/L_{1,d}^{\mathrm{cl}}<1.456$ or $\mathcal{C}_1<0.373556$. Lemma 11 is the handle: an explicit pair $(f,\varphi)$ upper-bounds $\mathcal{C}_1$, and Proposition 10 converts that by $L_{1,1}/L_{1,1}^{\mathrm{cl}}=(9\sqrt{3}/4)\,\mathcal{C}_1$.

First numerical pass used `scipy.quad` on $(0,10^6]$ only. That printed $\mathcal{C}_1\approx 0.37172$ for the paper's second pair. The missing tail is almost the full $\int_{10^6}^\infty t^{-3/2}\,dt=2\cdot 10^{-3}$. Adding it recovers the paper's $0.373556$. The $0.37172$ float is not a bound.

A conservative panel-sum (monotone Darboux on $1-g=\int\varphi_{\mathrm{raw}}(1-f)/\int\varphi_{\mathrm{raw}}$, exact $\int t^{-3/2}$, near-zero power bound, tail $2T^{-1/2}$) was written in Python and independently in Rust (`u=\log t$, different $s$-grid, different $I_f$ partition). On the paper's second pair the panel bound sits at $\mathcal{C}_1\le 0.37368$, which does **not** convert below $1.456$. Residue on that pair.

Parametric search over
$f(t)=(1+\mu t^\alpha)^{-\beta}$,
$\varphi(t)=c(1-(t/S)^\gamma)^\delta/(1+\varepsilon t)^\kappa$ on $[0,S]$
found a better pair (family A in `compute/q1/opt_best_A.json`). Histogram search produced an invalid $g$-clip ($\mathcal{C}_1$ looked like $0.36$ until $f>1$ was forbidden); honest re-score did not beat family A.

Certified on the polished family-A pair (Python panel, then Rust recomputation):

- $\mathcal{C}_1\le 0.373548$
- $L_{1,1}/L_{1,1}^{\mathrm{cl}}\le 1.45576$
- $K_1/K_1^{\mathrm{cl}}\ge 0.47187$

That is a dent of the published $1.456$. It is not the Sobolev value $2/\sqrt{3}$ and it is not a closed form. Replay: `problems/simon-lieb-thirring/compute/q1/run_all.sh`. Lean proves only the algebraic conversion, in `lean/FhjnProp10Conversion.lean`.
