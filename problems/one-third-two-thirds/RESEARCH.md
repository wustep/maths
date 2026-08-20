# Research log — the 1/3–2/3 conjecture for posets

## 2026-08-17

Fetched and read tonight, in the order used.

### Status and surveys

- [Chan–Pak, *Linear extensions of finite posets*, arXiv:2311.02743v2](https://arxiv.org/abs/2311.02743) (26 Feb 2025; EMS Surv. Math. Sci. online 2025). Conjecture 13.1 is the $1/3$–$2/3$ statement, still open. Sorting-probability section 13; Kahn–Saks $\delta\to 1/2$ as width $\to\infty$ is Conjecture 13.4. PDF: https://www.math.ucla.edu/~pak/papers/LEsurvey11.pdf
- [Wikipedia, *1/3–2/3 conjecture*](https://en.wikipedia.org/wiki/1/3%E2%80%932/3_conjecture), oldid 1368808118, fetched 2026-08-17. Lists the known classes; cites Gupta 2026 for order 14; width-3 minimum $14/39$ through nine elements.
- [Brightwell, *Balanced pairs in partial orders*, Discrete Math. 201 (1999)](https://doi.org/10.1016/S0012-365X(98)00311-2). The survey Olson–Sagan and Chen quote.
- [Aires–Kahn, *Balancing extensions in posets of large width*, arXiv:2509.11549](https://arxiv.org/abs/2509.11549) (15 Sep 2025). $\delta\to 1/2$ if width $\Omega(n)$ or $|\min P|\gg\log n$; $\delta\ge 1/e-o(1)$ if width $\omega(\sqrt n)$ or height $o(n)$. Does **not** prove $1/3$–$2/3$. Kahn–Saks remains open.

### Finite census

- [Peczarski, *The Gold Partition Conjecture*, Order 23 (2006)](https://doi.org/10.1007/s11083-006-9033-1). GPC through 11; GPC implies $1/3$–$2/3$.
- [De Loof–De Baets–De Meyer, *Counting linear extension majority cycles…*, Comput. Math. Appl. 59 (2010)](https://doi.org/10.1016/j.camwa.2009.12.021). Mutual rank probabilities through 13; identifies worst balanced posets through 13.
- [Gupta, *The Gold Partition Conjecture holds through fourteen elements*, arXiv:2607.23926](https://arxiv.org/abs/2607.23926) (27 Jul 2026). GPC (hence $1/3$–$2/3$) through 14. Not a $\delta$-census at 14. Shard archive doi:10.5281/zenodo.21576030.
- [Peczarski, *The worst balanced partially ordered sets—ladders with broken rungs*, Exp. Math. 28 (2019)](https://doi.org/10.1080/10586458.2017.1368050). Global (all widths) worst indecomposable examples through 11 are broken ladders; numerical gap $\approx 0.348843$. This is *not* a width-3 census at 10: the global minimum at those orders is width 2.

### Structural theorems used tonight

- Linial 1984: width 2. Sah 2021 improves the width-2 constant.
- Trotter–Gehrlein–Fishburn 1992: height 2; also the width-3 $14/39$ statement through nine elements.
- Brightwell 1989: semiorders. Interval orders are not on the list.
- Brightwell–Wright 1992: 5-thin. Peczarski 2008: 6-thin, including GPC.
- Zaguia 2012: $N$-free. Zaguia 2016/2019: almost-twins; cover graph a forest.
- Ganter–Hafner–Poguntke 1987: nontrivial automorphism.
- Olson–Sagan, *On the 1/3–2/3 conjecture*, Order 2018, [arXiv:1706.04985](https://arxiv.org/abs/1706.04985). Automorphism 2-cycle $\Rightarrow\delta=1/2$; anti-automorphism with two fixed points $\Rightarrow\delta=1/2$; Boolean / partition / subspace lattices; all Young diagrams including skew and shifted; some dimension-2 pattern-avoiding posets. **Question 3.9: products of $k\ge 3$ chains. Question 5.2: all dimension-2 posets. Question 3.6: all distributive lattices.**
- Chen, *A family of posets with small balance constant*, EJC 25 (2018), [arXiv:1709.05753](https://arxiv.org/abs/1709.05753). Width-2 family with limit $\kappa=\frac1{32}(93-\sqrt{6697})\approx 0.348900$. Appendix A is the $E(m,n)$ table we replayed.
- Brightwell–Felsner–Trotter 1995: general bound $(5-\sqrt5)/10$. Kahn–Saks 1984: $3/11$.

### What we compare against

- Best general published constant: BFT $(5-\sqrt5)/10\approx 0.276393$. We do not touch this.
- Width-3 published finite record, before tonight: no example with $\delta<14/39$ on $\le 9$ elements (TGF 1992; Olson–Sagan 2018). Saks 1985 supplies the 7-element example attaining $14/39$. Tonight's $W_{10}$ has $\delta=6/17<14/39$ at 10 elements, independently checked.
- Three-chain products: Olson–Sagan Question 3.9, no later resolution found in Chan–Pak 2025, Aires–Kahn 2025, or Wikipedia tonight.
- Unrestricted finite order: Gupta 14, via GPC. We do not claim 15.

### False or unused claims

- No paper claiming a general proof of $1/3$–$2/3$ was treated as a resolution. Chan–Pak and Aires–Kahn still call it open.
- Aires–Kahn is real progress on Kahn–Saks, not on the $1/3$ constant.
