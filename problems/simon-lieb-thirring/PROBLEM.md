# Lieb–Thirring conjecture (Simon 2000, #15)

- Slug: `simon-lieb-thirring`
- List: Simon 2000 #15
- Solver: Cursor Grok 4.6 xhigh
- Status: dent of FHJN 1.456. Certified family-A pair has $\mathcal{C}_1\le 0.373548$, hence $L_{1,1}/L_{1,1}^{\mathrm{cl}}\le 1.45576$ and $K_1/K_1^{\mathrm{cl}}\ge 0.47187$. Conjecture not claimed.
- Area: Mathematical physics / spectral theory
- Sources: Simon, *Schrödinger Operators in the Twenty-First Century* (Mathematical Physics 2000); Lieb–Thirring 1976
- Started: 2026-08-27

## In general

For a Schrödinger operator $-\Delta+V$ on $L^2(\mathbb{R}^d)$, write $E_j$ for the negative eigenvalues. The Lieb–Thirring inequality is

$$\sum_j |E_j|^\gamma \le L_{\gamma,d}\int_{\mathbb{R}^d} V(x)_-^{\gamma+d/2}\,dx.$$

The semiclassical (phase-space) constant is $L_{\gamma,d}^{\mathrm{cl}}$. Lieb and Thirring conjectured that the optimal $L_{\gamma,d}$ equals $\max(L_{\gamma,d}^{\mathrm{cl}},L_{\gamma,d}^{\mathrm{one}})$, the larger of the semiclassical constant and the one-bound-state (Sobolev) constant. Simon's 2000 problem #15 asks for a proof of that conjecture in the remaining one-dimensional window $\tfrac12<\gamma<\tfrac32$.

The physically important case is $\gamma=1$. Duality converts the $\gamma=1$ bound into a kinetic-energy inequality with constant $K_d$, related by

$$K_d\Bigl(1+\frac{2}{d}\Bigr)=\Bigl[L_{1,d}\Bigl(1+\frac{d}{2}\Bigr)\Bigr]^{-2/d}.$$

Laptev–Weidl proved the conjecture for every $d$ when $\gamma\ge\tfrac32$. Hundertmark–Lieb–Thomas / Weidl give the sharp one-dimensional value at $\gamma=\tfrac12$. The window $1\le\gamma<\tfrac32$ still has a gap between the one-bound-state lower bound and the best published upper bound.

## Precise statement

The published record for the $\gamma=1$ ratio, in every dimension, is Frank–Hundertmark–Jex–Nam, arXiv:1808.09017 (JEMS 23 (2021)):

$$
\frac{L_{1,d}}{L_{1,d}^{\mathrm{cl}}}\le 1.456,
$$

and, in one dimension, the more precise numerical claims $L_{1,1}/L_{1,1}^{\mathrm{cl}}\le 1.455786$ and $K_1/K_1^{\mathrm{cl}}\ge 0.471851$, coming from an explicit trial pair in their Lemma 11 with $\mathcal{C}_1\le 0.373556$. The one-bound-state (Sobolev) ratio in $d=1$ is $L_{1,1}^{\mathrm{So}}/L_{1,1}^{\mathrm{cl}}=2/\sqrt{3}\approx 1.154700$. Eden–Foias (1991), lifted by Dolbeault–Laptev–Loss (arXiv:0708.1165), had $\pi/\sqrt{3}\approx 1.8138$.

This folder attacks the FHJN variational handle $\mathcal{C}_1$: an explicit pair $(f,\varphi)$ with $\int f^2=\int\varphi=1$ produces a rigorous upper bound on $\mathcal{C}_1$ and therefore on $L_{1,1}/L_{1,1}^{\mathrm{cl}}$.

## What would count as a new bound

A verified finite improvement of a documented record, for example:

1. A smaller rigorous upper bound than the published $1.456$ on $L_{1,d}/L_{1,d}^{\mathrm{cl}}$ (equivalently, a certified $\mathcal{C}_1$ that converts to a ratio strictly below $1.456$).
2. A new certified test-function lower bound that moves a published numerical lower bound on $L_{1,1}/L_{1,1}^{\mathrm{cl}}$ or on $K_1/K_1^{\mathrm{cl}}$.
3. A reusable exact lemma that strictly tightens one of those conversions.

An incomplete numerical plot of $\mathcal{C}_1$, or a high-precision float with no independently replayable witness, is not a bound. The full Lieb–Thirring conjecture is not claimed unless it is proved.

## After 2026-08-27

FHJN Theorem 1 is still the published record to beat: $1.456$ in every dimension. Their Lemma 11 second pair really is $\mathcal{C}_1\approx 0.373553$ once the $t^{-3/2}$ tail is kept; the panel bound on that pair does not convert below $1.456$.

A different power-decay / compact-$\varphi$ pair (`compute/q1/opt_best_A.json`) has certified

$$
\mathcal{C}_1\le 0.373548,
$$

independently in Python (panel Darboux) and Rust (log substitution). Proposition 10 then gives

$$
\frac{L_{1,1}}{L_{1,1}^{\mathrm{cl}}}\le 1.45576,\qquad
\frac{K_1}{K_1^{\mathrm{cl}}}\ge 0.47187,
$$

and the same one-dimensional operator-valued lift as the paper sends the ratio to every $d$. Replay: `compute/q1/run_all.sh`. Lean proves only the conversion, not the integral. The Sobolev value $2/\sqrt{3}$ is untouched.
