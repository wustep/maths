# Walkthrough — simon-lieb-thirring

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.

0. What was actually missing — The q1 handle was a better FHJN trial pair. That was the wrong degree of freedom. Carvalho Corso–Ried had already solved the variational problem. The leftover work was to find that paper (the number is not in the abstract), replay $M_3$, and certify the closed form rather than shave another $10^{-4}$ off a nonnegative pair.

1. Named false starts — Treating FHJN 1.456 as the record after a title/abstract search that returned 2403.04347 and did not open it. The abstract says “best possible upper bounds … achievable by the method” and never writes 1.44655. A Lipschitz panel envelope of the three-lines integral, splitting $N=\sinh(ky)\cos(kx)-ky$ into two huge cancelling pieces, produced $\mathrm{Re}\,\theta\in\pm 900$ and was not a bound. Family-C two-scale search in q1 had already hit the $\alpha_1=10$ wall at a float near $1.453$, still above $M_3$.

2. The useful failure — q1’s certified pair at $1.45576$ is a dent of FHJN 1.456 and a residue relative to CCR. The panel bound on Lemma 11’s second pair still does not convert below 1.456. Once $M_3$ is the exact infimum of the $L^2$ problem, a new nonnegative pair cannot be the large jump. The imagined certificate written first (a certified $A=\lVert h_{-2/3}\rVert_\infty$ and $B=\lVert h_{-1}\rVert_2$) is the right witness class, but the oscillatory integral is the hard way to evaluate it.

3. The click — Open Corollary 1.7 and Table 1.1, not the abstract. $M_3=0.371185695$ converts by the same $(9\sqrt{3}/4)$ factor to $1.44655$. Carvalho Corso’s follow-up (arXiv:2407.10117v2, Corollary 1.8) evaluates the three-lines ratio as a Clausen function. At $d=s=1$ that is $(\pi/3)\exp(3\,\mathrm{CI}_2(2\pi/3)/(2\pi))$, and $\mathrm{CI}_2(2\pi/3)$ is a positive sine series. The imagined $A,B$ witness and the Clausen series are the same number.

4. The argument — Theorem 1.3 writes $h=B_\gamma e^{\theta_\gamma}$. Formula (1.4) at $\gamma=3$ is $M_3=(16\pi/81)H^3$ with $H=\lVert h_{-2/3}\rVert_\infty/\lVert h_{-1}\rVert_2^{2/3}$. Lemma 4.6 (the proof, not the introduction display) has the minus sign on $\mathrm{Re}\,\theta$. A trapezoid replay of that integral matches the table to $6\times 10^{-11}$. Independently, $\mathrm{CI}_2(2\pi/3)=(\sqrt{3}/2)\sum_{m\ge 0}(1/(3m+1)^2-1/(3m+2)^2)$. A finite prefix plus $\sum_{m\ge N}t_m<1/(18(N-1)^2)$ is an upper bound. Push it through $\exp$ and the two published conversions. FHJN Proposition 10 writes $f,\varphi\ge 0$; CCR (1.11) is over $L^2$. They identify the problems. This folder does not claim a new nonnegative pair at $0.37118$.

5. Computer search — `replay_m3.py` is the integral float. `verify_m3.py` sums $N=20000$ terms with a directed pad. `verify_m3.rs` uses $N=15000$, a split even/odd sum, and a coarser tail. Both write $M_3\le 0.371185695$ and $L/L^{\mathrm{cl}}\le 1.4465531$, not below $1.44655$. q1 `run_all.sh` still exits 0 on the family-A pair. No new pair search was the point.

6. Proven vs still open — Proven here: an independent envelope of the published CCR value, and a replay that q1’s pair does not beat it. Still open: the conjecture $L_{1,1}=L_{1,1}^{\mathrm{So}}$ (ratio $2/\sqrt{3}$). CCR is the method ceiling for the FHJN handle. A number below $1.44655$ needs a different method.
