# Lieb–Thirring conjecture (Simon 2000, #15)

- Slug: `simon-lieb-thirring`
- List: Simon 2000 #15
- Solver: Cursor Grok 4.6 xhigh
- Status: residue vs CCR 1.44655. Later record is Carvalho Corso–Ried, arXiv:2403.04347v2, ratio $1.44655$ from \(M_3=0.371185695\). Independent Clausen envelope \(M_3\le 0.371185695\) and \(L/L^{\mathrm{cl}}\le 1.4465531\). Did not beat 1.44655. The q1 family-A pair remains a dent of FHJN 1.456 only. Conjecture not claimed.
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

The published record for the $\gamma=1$ ratio, in every dimension, is no longer the 2018 trial pair. Carvalho Corso–Ried, arXiv:2403.04347v2 (v1 already 7 Mar 2024), solve the FHJN/HKRV variational problem and get

$$
\frac{L_{1,1,1}}{L_{1,1,1}^{\mathrm{cl}}}\le 1.44655
$$

from Table 1.1, $M_3=0.371185695$, and identification (1.12), $\mathcal{C}_{1,1}=M_3$. The same one-dimensional lift as FHJN sends the ratio to every $d$. Carvalho Corso, arXiv:2407.10117v2, Corollary 1.8, writes the same bound as a Clausen value and rounds it to $1.447$.

Frank–Hundertmark–Jex–Nam, arXiv:1808.09017 (JEMS 23 (2021)), Theorem 1 had $1.456$, with Lemma 11 $\mathcal{C}_1\le 0.373556$ converting to $1.455786$. The one-bound-state (Sobolev) ratio in $d=1$ is $2/\sqrt{3}\approx 1.154700$. Eden–Foias (1991), lifted by Dolbeault–Laptev–Loss (arXiv:0708.1165), had $\pi/\sqrt{3}\approx 1.8138$.

This folder first attacked the FHJN handle $\mathcal{C}_1$ by trial pairs. After CCR, a new pair cannot beat $M_3$. The leftover handle is a different method, or a certified evaluation of the CCR/Clausen form.

## What would count as a new bound

A verified finite improvement of a documented record, for example:

1. A smaller rigorous upper bound than the published CCR $1.44655$ on $L_{1,d}/L_{1,d}^{\mathrm{cl}}$ (equivalently, a certified $\mathcal{C}_1$ or $M_3$ that converts to a ratio strictly below $1.44655$). An envelope of $1.44655$ is a replay, not a new bound.
2. A new certified test-function lower bound that moves a published numerical lower bound on $L_{1,1}/L_{1,1}^{\mathrm{cl}}$ or on $K_1/K_1^{\mathrm{cl}}$.
3. A reusable exact lemma that strictly tightens one of those conversions.

An incomplete numerical plot of $\mathcal{C}_1$, or a high-precision float with no independently replayable witness, is not a bound. The full Lieb–Thirring conjecture is not claimed unless it is proved.

## After 2026-08-27

The published record to cite is Carvalho Corso–Ried, arXiv:2403.04347v2: $L/L^{\mathrm{cl}}\le 1.44655$. The abstract does not contain that number; Corollary 1.7 and Table 1.1 do. v1 already has it. No later paper opened in this folder states a smaller Euclidean $\gamma=1$ ratio. Carvalho Corso, arXiv:2407.10117v2, restates the same bound as $1.447$.

Independently, the Clausen series for $\mathrm{CI}_2(2\pi/3)$ converts to

$$
M_3\le 0.371185695,\qquad
\frac{L_{1,1,1}}{L_{1,1,1}^{\mathrm{cl}}}\le 1.4465531,\qquad
\frac{K_1}{K_1^{\mathrm{cl}}}\ge 0.47789.
$$

Python and Rust agree. Replay: `compute/q2/run_all.sh`. That is an envelope of the published value, not a dent of it.

The q1 family-A pair (`compute/q1/opt_best_A.json`) is still a dent of FHJN $1.456$ only:

$$
\mathcal{C}_1\le 0.373548,\qquad
\frac{L_{1,1}}{L_{1,1}^{\mathrm{cl}}}\le 1.45576.
$$

Replay: `compute/q1/run_all.sh`. Their Lemma 11 second pair does not convert below $1.456$. Lean proves only the conversion. The Sobolev value $2/\sqrt{3}$ is untouched. CCR present $M_3$ as the method ceiling: no FHJN trial pair goes below it.
