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

## 2026-08-27 (later the same day)

Replayed q1 on this branch: `compute/q1/run_all.sh` exited 0. Paper Lemma 11 second pair still does not convert below $1.456$. Family A still certifies $\mathcal{C}_1\le 0.373548$, $L/L^{\mathrm{cl}}\le 1.45576$. Covering stayed frozen.

The 1.456 record was already beaten. Carvalho Corso–Ried, arXiv:2403.04347, v1 7 Mar 2024 and v2 21 Dec 2024 (“corrected a few typos”), Corollary 1.7 and Table 1.1 state $L_{1,1,1}/L^{\mathrm{cl}}\le 1.44655$ from $M_3=0.371185695$. The abstract does not contain $1.44655$; that is why the q1 title/abstract search missed it. Identification (1.12) is $\mathcal{C}_{1,1}=M_3$. They present this as the method ceiling.

A float replay of Theorem 1.3 / Lemma 4.6 (`compute/q2/replay_m3.py`) matches the table: $M_3=0.371185694940$, $L/L^{\mathrm{cl}}=1.446553086$. Their Lemma 11-style second pair is not involved.

Carvalho Corso, arXiv:2407.10117v2, Corollary 1.8, writes the same bound as

$$
\frac{L_{1,1,1}}{L^{\mathrm{cl}}}\le\frac{\pi}{3}\exp\Bigl(\frac{3\,\mathrm{CI}_2(2\pi/3)}{2\pi}\Bigr)
$$

and rounds it to $1.447$. The Clausen value is the sine series
$\mathrm{CI}_2(2\pi/3)=(\sqrt{3}/2)\sum_m\bigl(1/(3m+1)^2-1/(3m+2)^2\bigr)$.

`compute/q2/verify_m3.py` and `verify_m3.rs` (different $n$, different tail) enclose that series and convert. Joint claim, worse of the two codes:

- $M_3\le 0.371185695$
- $L/L^{\mathrm{cl}}\le 1.4465531$
- $K/K^{\mathrm{cl}}\ge 0.47789$

That is below q1 $1.45576$ and below $1.45$. It is not below CCR $1.44655$. Residue vs beating the later record. No new trial pair. No priority claim. Papers opened after CCR (Nam 2510.24148, Coulomb 2409.01291, spheres 2602.00725, Pauli 2404.09926, …) do not state a smaller Euclidean $\gamma=1$ ratio; 2510.24148 still calls FHJN the best known constant.

Replay: `problems/simon-lieb-thirring/compute/q2/run_all.sh`. Sobolev $2/\sqrt{3}$ untouched.

## 2026-09-02

CCR is the method ceiling of the FHJN/HKRV variational problem. This run did not search another nonnegative pair. It tried other published conversions and a 1D test-potential search, all in `compute/q3/`. RAM stayed light; one heavy job at a time.

Fetched and read again: CCR v2, Carvalho Corso 2407.10117v2, FHJN 1808.09017, DLL 0708.1165v2, Weidl quant-ph/9504013, Seiringer–Solovej 2303.04504v2, Nam 2012.12045v2, Levitt 1206.1473, Frank ICM 2109.13660, Bachmann–Froese–Schraven 2403.19023v3. No later Euclidean $\gamma=1$ ratio below $1.44655$.

Five handles:

1. Weidl’s real interpolation between HLT $L_{1/2,1}=1/2$ and Laptev–Weidl $3/16$, independently in Python and `rustc`. The Ky-Fan factor $M(1/2)=2$ forces $C(1/2)\approx 2.660$, so $L/L^{\mathrm{cl}}\approx 3.8385$. The $C=1$ Hadamard envelope $\sqrt{3/32}/L^{\mathrm{cl}}\approx 1.44287$ applies only to characteristic-function potentials (Weidl (23)), not to general $V$.
2. Seiringer–Solovej remainder (arXiv:2303.04504v2) after Hoffmann–Ostenhof absorption. The Airy zero is enclosed by a power series: $R_1\le 0.13203$, hence $L/L^{\mathrm{cl}}\le 2.752$. Weaker than CCR and weaker than Rumin $d/(d+4)=1/5$.
3. Weidl’s Neumann covering scored at $\gamma=1$ with partition $\alpha=l\int_I V=3$. A constant well already gives local ratio $1/\sqrt{3}$, i.e. $L/L^{\mathrm{cl}}\approx 2.721$. Random histograms, after the same $\alpha=3$ rescaling, did not exceed that. The covering cannot dent $1.44655$.
4. Dirichlet-grid search for a test potential with ratio above the one-bound-state value $2/\sqrt{3}\approx 1.154701$. Square wells, two-sech wells, Gaussian sums, and histograms. Best numeric two-sech (separation $4$, amplitude $3/4$) sat at $1.1507$ with two bound states. Exact Keller $V=(3/4)\mathrm{sech}^2$ replays $1.154701$. No trial exceeded $2/\sqrt{3}$. Not a new lower bound, and not an upper bound.
5. Empirical $T/\int\rho^3$ on Hermite and finite-well blocks: minimum $2.717$, above the $1.35$ that would convert Eden–Foias past CCR. The DLL Cauchy–Schwarz step still only proves $\kappa\ge 1$ (ratio $\pi/\sqrt{3}\approx 1.8138$). The empirical gap is not a bound.

Joint claim: no alternative conversion or trial potential moved $1.44655$. Residue versus the later record. Replay: `problems/simon-lieb-thirring/compute/q3/run_all.sh`. The q2 Clausen envelope is replayed at the end of that script. Sobolev $2/\sqrt{3}$ untouched.
