# Grok 4.6 SuperGrok 2026-09-02 — Lieb–Thirring q3

Continuation of Simon 2000 #15. Search lives in
`problems/simon-lieb-thirring/compute/q3/`. Covering stayed frozen.
Branched from origin/main.

CCR, arXiv:2403.04347v2, remains the published later record:
$L/L^{\mathrm{cl}}\le 1.44655$ from $M_3=0.371185695$. The q2 Clausen
envelope is $1.4465531$ and does not beat that number. q1 family A is
still $1.45576$, a dent of FHJN $1.456$ only.

This run did not search another FHJN pair. It tried other conversions
and a 1D test-potential search.

- Weidl interpolation with HLT $L_{1/2,1}=1/2$: ratio $\approx 3.8385$.
- Seiringer–Solovej Airy $R_1$ after Hoffmann–Ostenhof: ratio $\approx 2.752$.
- Neumann covering at $\gamma=1$, $\alpha=3$: constant well $\approx 2.721$.
- Trial potentials: exact Keller $2/\sqrt{3}\approx 1.154701$; no discrete
  trial exceeded it. Two-sech at separation $4$ sat at $1.1507$ with two
  bound states.
- Empirical Eden–Foias $\kappa$ on Hermite blocks $\ge 2.717$; the proved
  $\kappa$ is still $1$.

Did not beat $1.44655$. Residue versus the later record. Conjecture open.

Replay:

```
cd problems/simon-lieb-thirring/compute/q3
./run_all.sh
```

That also replays `compute/q2/verify_m3.py`.
