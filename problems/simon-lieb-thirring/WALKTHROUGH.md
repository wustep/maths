# Walkthrough — simon-lieb-thirring

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.

0. What was actually missing — Frank–Hundertmark–Jex–Nam already reduced the $\gamma=1$ ratio to a one-dimensional calculus problem: minimise $\mathcal{C}_1$ over pairs $(f,\varphi)$. Their Lemma 11 pair is a four-exponent ansatz, not the infimum. The published theorem rounds the conversion to $1.456$. A better explicit pair, with a remainder that is actually an upper bound, is the leftover handle.

1. Named false starts — Treating a `scipy.quad` value on $(0,10^6]$ as $\mathcal{C}_1$. The integrand tends to $t^{-3/2}$, so the omitted tail is $\approx 0.002$ in $I$ and $\approx 0.0018$ in $\mathcal{C}_1$. That is exactly the gap between $0.37172$ and the paper's $0.373556$. A histogram search that clipped $g$ at $1$ while allowing $f>1$ reported $\mathcal{C}_1\approx 0.36$; the clip zeroed $(1-g)^2$ and the honest re-score was worse than the paper.

2. The useful failure — The paper's $0.373556$ is not a lazy rounding of $0.3717$. It is what you get once the tail is present. Beating $1.456$ therefore needs a genuinely better pair, or a tighter remainder on the same pair. The panel bound on their second pair lands at $0.37368$ and does not convert below $1.456$.

3. The click — Keep the same proof, change the trial. The first Lemma 11 pair is the Section 2 optimiser $f(t)=(1+\mu t^{3/2})^{-1}$ times a compact $\varphi$. The second pair already relaxes the exponents. A slightly different $(\alpha,\beta,\gamma,\delta,\varepsilon,\kappa,S)$ lowers the *true* integral by about $10^{-4}$, which is enough to push a conservative panel bound through the $1.456$ threshold $1456/1000\cdot 4/(9\sqrt{3})\approx 0.373610$.

4. The argument — For $f(t)=(1+\mu t^\alpha)^{-\beta}$ decreasing and $\varphi\ge 0$ compactly supported, $g$ is decreasing and $0\le g\le 1$, so $(1-g)^2$ is increasing. On a $t$-panel freeze $(1-g)^2$ at the right endpoint and integrate $t^{-3/2}$ exactly. Bound $1-g=\int\varphi_{\mathrm{raw}}(1-f)/\int\varphi_{\mathrm{raw}}$ by a left-$\varphi$ / right-$(1-f)$ Darboux sum. Near zero use $1-g(t)\le \beta\mu (St)^\alpha$. Tail $\int_T^\infty t^{-3/2}=2T^{-1/2}$. Take $\mu$ large enough that $\int f^2\le 1$; enlarging $f$ to unit $L^2$ only decreases $\mathcal{C}_1$, so the value at $\mu_{\mathrm{upper}}$ is still an upper bound on the admissible pair. Convert by the $d=1$ identity $L/L^{\mathrm{cl}}=(9\sqrt{3}/4)\,\mathcal{C}_1$, which is the Lean file.

5. Computer search — `optimize_parametric.py` (differential evolution + L-BFGS on family A and a two-scale family). Winner is family A in `opt_best_A.json`. `verify_c1.py` writes the slim certificates. `verify_c1.rs` recomputes with $u=\log t$, a different $s$-count, and a different $I_f$ partition. `float_c1.py` is a trapezoid estimate, not a bound: paper pair $\approx 0.373553$, family A $\approx 0.373445$, both below the certified $0.373548$.

6. Proven vs still open — Proven: $\mathcal{C}_1\le 0.373548$ for an explicit pair, hence $L_{1,d}/L_{1,d}^{\mathrm{cl}}\le 1.45576$ by the same lifting FHJN already used. Still open: the conjecture $L_{1,1}=L_{1,1}^{\mathrm{So}}$ (ratio $2/\sqrt{3}$), and the true infimum of $\mathcal{C}_1$ (only $\mathcal{C}_1\ge 1/3$ is elementary).
