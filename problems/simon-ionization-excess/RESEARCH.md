# Research log — simon-ionization-excess

Papers, OEIS, failed lookups. Cite every URL you opened, including the
ones that gave nothing. Forum numbers (MSE, Reddit, MathOverflow,
AlphaXiv) are leads, not citations. Append a stub with
`python3 scripts/arxiv_fetch.py <id> --research problems/simon-ionization-excess/RESEARCH.md`
or look up a sequence with `python3 scripts/oeis_lookup.py`.

## 2026-08-27

- (no lookups yet)
- [Nam, *New bounds on the maximum ionization of atoms*, arXiv:1009.2367v3](https://arxiv.org/abs/1009.2367) (26 Nov 2011). TODO: claimed result; verified how?
- [Hundertmark–Pattakos–Schulz, *On the Excess Charge Problem of Atoms*, arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487) (25 Apr 2025). Opened abs and [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/2504.18487). Theorem 2.2: $N_c<b(s)Z+c(s)Z^{1/3}$ for $s\in(1,3]$ with $b(s)=\max_{t\in[0,1]}(1+t^{s-1})/(1+t^s)$. Prop. 2.4 ($Z\ge2$): $N_c<\frac12(\sqrt2+1)Z+2.96Z^{1/3}$, and $1.2071<\frac12(\sqrt2+1)<1.2072$. Prop. 2.5 ($Z\ge4$): $N<b(3)Z+3.90Z^{1/3}+0.0134+0.184Z^{-1/3}+0.0196Z^{-2/3}$ with $1.1184<b(3)<1.1185$ and the closed form $b(3)=\frac23\sqrt[3]{1+\sqrt2}/((1+\sqrt2)^{2/3}-1)$. Simplified line $N_c<1.1185Z+4Z^{1/3}$ for all $Z\ge4$. Remark 2.6: Prop. 2.4 beats Lieb for $Z>5.3$ and Nam for all $Z\ge2$; (2.9) beats (2.8) for $Z\ge35.8$. Does not claim a $Z$-independent excess.
- [Nam, *On the number of electrons that a nucleus can bind*, arXiv:1209.3642v2](https://arxiv.org/abs/1209.3642) (7 Dec 2012). TODO: claimed result; verified how?
- [Solovej, *The Ionization Conjecture in Hartree-Fock Theory*, arXiv:math-ph/0012026v3](https://arxiv.org/abs/math-ph/0012026) (22 Apr 2004). TODO: claimed result; verified how?
- [Nam, *The ionization problem in quantum mechanics*, arXiv:2206.15393v1](https://arxiv.org/abs/2206.15393) (30 Jun 2022). TODO: claimed result; verified how?
- [Frank–Hundertmark–Jex–Nam, *The Lieb-Thirring inequality revisited*, arXiv:1808.09017v1](https://arxiv.org/abs/1808.09017) (27 Aug 2018). TODO: claimed result; verified how?
- [Frank, *The Lieb-Thirring inequalities: Recent results and open problems*, arXiv:2007.09326v1](https://arxiv.org/abs/2007.09326) (18 Jul 2020). TODO: claimed result; verified how?

## 2026-08-27 — small-Z replay sources

- [Høgaasen–Richard–Sorba, *Two-electron atoms, ions and molecules*, arXiv:0907.2614](https://arxiv.org/abs/0907.2614) ([HTML](https://ar5iv.labs.arxiv.org/html/0907.2614)). Chandrasekhar closed forms for $N,T,V$; H$^-$ minimum $\overline{E}\approx-0.5133$ at $a\approx1.039$, $b\approx0.283$; frozen $a=1$, $b\approx0.279$ already binds ($\approx-0.5126$); uncorrelated product binds only for $Z\ge 1.067$; helium Chandrasekhar $\approx-2.8757$ vs uncorrelated $\approx-2.8477$ vs NR $\approx-2.9037$. Table 1.
- [Nam, *The ionization problem in quantum mechanics*, arXiv:2206.15393v1](https://arxiv.org/abs/2206.15393) ([HTML](https://ar5iv.labs.arxiv.org/html/2206.15393)). Zhislin: binding for $N<Z+1$. Lieb: $N_c<2Z+1$ for all $Z>0$, and this "settles the ionization conjecture for the hydrogen atom." Nam $N_c<1.22Z+3Z^{1/3}$.
- [Lieb, *A bound on the maximum ionization of atoms and molecules*](https://inspirehep.net/literature/14268), Phys. Rev. A 29, 3018–3028 (1984). Abstract: $N_c<2Z+1$; for hydrogen $N_c=2$, so $\mathrm{H}^{--}$ is not stable. Full APS HTML was blocked by Cloudflare this session (`https://journals.aps.org/pra/abstract/10.1103/PhysRevA.29.3018`).
- [Nakashima–Nakatsuji, J. Chem. Phys. 127, 224104 (2007)](https://doi.org/10.1063/1.2801981); also the [QCRI PDF](https://qcri.or.jp/lab/wp-content/uploads/2011/07/p347.pdf) and the [Kyoto repository PDF](https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/d1030939-735b-4dea-950a-ddbad3f0d913/content). Infinite-mass NR helium $-2.90372437703411959831115924519440444669690537$; H$^-$ $-0.52775101654437719659081456674751138304502$. Comparison only; not replayed.
- [Sims–Hagstrom, Hylleraas-CI on helium $1^1S$, arXiv:1207.7284v3](https://arxiv.org/abs/1207.7284) ([HTML](https://arxiv.org/html/1207.7284v3)). Quotes the ICI helium number as the benchmark.
- [Turbiner–Lopez Vieyra–Olivares-Pilón, *Few-electron atomic ions in non-relativistic QED*, arXiv:1807.02457v5](https://arxiv.org/html/1807.02457v5). Treats Nakashima–Nakatsuji 2007 as the high-accuracy culmination for $Z=1$–$10$.
- [Nam, *New bounds on the maximum ionization of atoms*, arXiv:1009.2367v3](https://arxiv.org/abs/1009.2367). Abs page opened. $N_c<1.22Z+3Z^{1/3}$ for fermions. Not used as a small-$Z$ uniqueness statement.
- Failed: `https://arxiv.org/abs/0707.2101` is not Nakashima–Nakatsuji (Ward, QCD resummation). No arXiv id found for the 2007 JCP helium paper.
