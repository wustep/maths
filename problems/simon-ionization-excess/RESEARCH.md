# Research log — simon-ionization-excess

Papers, OEIS, failed lookups. Cite every URL opened this session. Forum
numbers are leads, not citations.

## 2026-08-27 — record

- [Wikipedia, *Simon problems*](https://en.wikipedia.org/wiki/Simon_problems) and the [mobile page](https://en.m.wikipedia.org/wiki/Simon_problems). Map only. 2000 #9: prove $N_0(Z)-Z$ bounded as $Z\to\infty$. 1984 10(a): $\Delta E(N-1,Z)\ge\Delta E(N,Z)$. Definitions of $H(N,Z)$, $E(N,Z)$, $N_0(Z)$.
- [MathWorld, *Simon's Problems*](https://mathworld.wolfram.com/SimonsProblems.html). Map. Points to Simon 2000, mp_arc 00-78.
- [HandWiki, *Simon problems*](https://handwiki.org/wiki/Simon_problems). Same map.
- [Simon, *Fifteen problems in mathematical physics* (1984 PDF)](http://www.math.caltech.edu/SimonPapers/R27.pdf). Fetch timed out this session.
- [Nam, *New bounds on the maximum ionization of atoms*, arXiv:1009.2367v3](https://arxiv.org/abs/1009.2367) (26 Nov 2011). $N_c<1.22Z+3Z^{1/3}$ for fermions; $\beta\in[0.8218,0.8705)$; Lemma 1 and Proposition 1. Beats Lieb for $Z\ge6$. Replay in `compute/q1/replay_nam_beta.py`.
- [Nam, *On the number of electrons that a nucleus can bind*, arXiv:1209.3642v2](https://arxiv.org/abs/1209.3642) (7 Dec 2012). Survey. Ionization conjecture $N_c\le Z+1$ or $Z+2$. Zhislin: binding for $N<Z+1$. Bosons: $N_c/Z\to t_c\approx1.21$.
- [Nam, *The ionization problem in quantum mechanics*, arXiv:2206.15393v1](https://arxiv.org/abs/2206.15393) (30 Jun 2022). Lieb settles hydrogen. Convexity of $E_N$ and “binding of $N$ implies binding of $N-1$” still open. Lenzmann–Lewin: no eigenvalue if $N\ge4Z+1$.
- [Hundertmark–Pattakos–Schulz, *On the Excess Charge Problem of Atoms*, arXiv:2504.18487v1](https://arxiv.org/abs/2504.18487) (25 Apr 2025). Opened abs and [HTML](https://arxiv.org/html/2504.18487v1). Theorem 2.2: $N_c<b(s)Z+c(s)Z^{1/3}$ for $s\in(1,3]$, $b(s)=\max_{t\in[0,1]}(1+t^{s-1})/(1+t^s)$. Prop. 2.4 ($Z\ge2$): $N_c<\frac12(\sqrt2+1)Z+2.96Z^{1/3}$. Prop. 2.5 ($Z\ge4$): $N<b(3)Z+3.90Z^{1/3}+0.0134+0.184Z^{-1/3}+0.0196Z^{-2/3}$ with $1.1184<b(3)<1.1185$. Simplified $N_c<1.1185Z+4Z^{1/3}$ for $Z\ge4$. This is the published non-asymptotic record to beat. Independently replayed in `compute/q1/`.
- [Solovej, *The Ionization Conjecture in Hartree-Fock Theory*, arXiv:math-ph/0012026v3](https://arxiv.org/abs/math-ph/0012026) (22 Apr 2004). HF excess and ionization energy stay bounded as $Z\to\infty$. Does not apply to the many-body Schrödinger operator.
- [Lewin, *Some open mathematical problems concerning charged quantum particles*](https://doi.org/10.5802/crphys.249), [PDF](https://comptes-rendus.academie-sciences.fr/physique/item/10.5802/crphys.249.pdf). Open Problem 1: $N_{\max}\le Z+CM$. Notes that even a huge $C$ is unknown for the Schrödinger operator. Cites Lieb $N_{\max}<2Z+M$ as the then-best explicit bound (pre-HPS).
- [Nam, *The Ionization Problem*, EMS Newsletter](https://ems.press/content/serial-article-files/12081). Same conjectures; LSST compactness; Fefferman–Seco / SSS $Z+O(Z^{5/7})$.
- [Frank–Hundertmark–Jex–Nam, *The Lieb–Thirring inequality revisited*, arXiv:1808.09017v1](https://arxiv.org/abs/1808.09017) (27 Aug 2018). $L_{1,d}/L_{1,d}^{\mathrm{cl}}\le1.456$. This is the factor HPS uses in $\kappa$. Not replaced.
- [Frank, *The Lieb–Thirring inequalities: Recent results and open problems*, arXiv:2007.09326v1](https://arxiv.org/abs/2007.09326) (18 Jul 2020). Survey; 1.456 still the cited bound for $1\le\gamma<3/2$.
- [Benguria–González-Brantes–Tubino, *New bounds on the excess charge for atomic systems*, arXiv:2207.08328v2](https://arxiv.org/abs/2207.08328) (updated 3 Nov 2025). Comment on the abs page: “This version is not definite and has errors.” Not used as a record. HTML 404 this session; PDF 404.
- [Lieb, Phys. Rev. A 29, 3018 (1984)](https://inspirehep.net/literature/14268). Abstract: $N_c<2Z+1$; hydrogen $N_c=2$. APS HTML blocked by Cloudflare this session.

## 2026-08-27 — small-Z replay sources

- [Høgaasen–Richard–Sorba, arXiv:0907.2614](https://arxiv.org/abs/0907.2614) ([HTML](https://ar5iv.labs.arxiv.org/html/0907.2614)). Chandrasekhar closed forms. Comparison for the H$^-$ open-shell trial.
- [Nakashima–Nakatsuji, J. Chem. Phys. 127, 224104 (2007)](https://doi.org/10.1063/1.2801981). Published NR benchmarks for He and H$^-$. Comparison only; not replayed. No arXiv id found (`0707.2101` is unrelated).
- Failed: Simon 2000 Imperial College chapter was not fetched (book, not arXiv). Wikipedia is the map to its statement.

## What the record does not say

No published paper opened this session proves $N_c\le Z+C$ for a $Z$-independent $C$ in the many-body Schrödinger theory. HPS 1.1185 is a leading coefficient, not a bounded excess. Nam’s $\beta\ge0.8218$ is a lower bound on a classical variational constant, not a new ionization coefficient beyond 1.22.
