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
- [Gupta, *The Gold Partition Conjecture holds through fourteen elements*, arXiv:2607.23926v1](https://arxiv.org/abs/2607.23926v1) (27 Jul 2026). GPC (hence $1/3$–$2/3$) through 14. Not a $\delta$-census. This is the version the 17 August note cited.
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

## 2026-08-27

Opened tonight, in the order used.

- [Gupta, *Balance Constants, Majority Cycles, and the Gold Partition Conjecture through Fourteen Elements*, arXiv:2607.23926v2](https://arxiv.org/abs/2607.23926) (30 Jul 2026). Full exact-balance census of all $1{,}338{,}193{,}159{,}771$ unlabelled 14-element posets. Least $\delta>1/3$ is $37/106$; least non-ordinal-sum is $254/725=L_{14,1,9}$; no value in the printed gap $(1/3,0.348843)$; 128 equality classes, all Aigner sums; longest majority cycle length 8 (30 classes). GPC through 14 unchanged from v1. HTML v2 and abs opened. Compact aggregate [census-n14.txt](https://github.com/agupta/gold-partition-conjecture/blob/main/data/census-n14.txt) opened; Zenodo 10.5281/zenodo.21696940 cited there, not re-downloaded. Width-3 $6/17$ appears as 29 ordinal sums; every strictly smaller tail value is width 2.
- [Chan–Pak, arXiv:2311.02743v2](https://arxiv.org/abs/2311.02743) re-opened. Conjecture 13.1 still open. Does not cite Gupta v2 (Feb 2025).
- [Olson–Sagan, arXiv:1706.04985v2](https://arxiv.org/abs/1706.04985) re-opened. Question 3.9 (products of $k\ge 3$ chains) still stated as open. Fig. 13 A already has $\delta=6/17$ (width 2).
- [Aires–Kahn, arXiv:2509.11549v1](https://arxiv.org/abs/2509.11549) re-opened. Large-width Kahn–Saks progress, not a $1/3$ proof. They record the guess that $\delta>1/3$ when width $\ge 3$.
- [Aires–Kahn, *Variance vs. range…*, arXiv:2510.26134v1](https://arxiv.org/abs/2510.26134) (30 Oct 2025). Kahn–Saks for large variance and bounded width; implies the large-$\pi(x)$ form. Does not prove $1/3$–$2/3$.
- [Wikipedia, *1/3–2/3 conjecture*](https://en.wikipedia.org/wiki/1/3%E2%80%932/3_conjecture) re-opened. Still lists the conjecture as open; cites Gupta 2026 for order 14.
- [Peczarski research page](https://mimuw.edu.pl/~marpe/research/index.html) opened for the ladder definition and figures. Paper: Exp. Math. 28 (2019).
- [agupta/gold-partition-conjecture](https://github.com/agupta/gold-partition-conjecture) README and `scripts/census_witness.py` opened for the Peczarski §1 formula ($x_i<x_{i+2}$ rails, $x_i<x_{i+3}$ rungs) and the published encodings.
- Zenodo 18985094 / 18985093 (Silva Alvarado, Mar 2026) claim a general proof. Not arXiv; Lean is conditional on an extra axiom; unaffiliated. Treated as a lead, not a record. Chan–Pak and Gupta v2 still call the conjecture open.

Failed or unused: no later arXiv paper closing Olson–Sagan Question 3.9, interval orders, or dimension 2. No width-3 $\delta<6/17$ in Gupta's published tail.

## 2026-08-27, q2

Opened tonight, in the order used.

- [Gupta arXiv:2607.23926v2](https://arxiv.org/abs/2607.23926) re-opened (abs and HTML). Still the order-14 $\delta$-census. Least $\delta>1/3$ is $37/106$; least non-sum is $254/725$. No later version.
- [Chan–Pak arXiv:2311.02743v2](https://arxiv.org/abs/2311.02743) re-opened. Conjecture 13.1 still stated. Does not cite Gupta v2.
- [Olson–Sagan arXiv:1706.04985v2 HTML](https://arxiv.org/html/1706.04985) re-opened. Question 3.9 still asks whether a product of $k\ge 3$ chains is $1/3$-balanced.
- [Aires–Kahn arXiv:2509.11549v1](https://arxiv.org/abs/2509.11549) and [arXiv:2510.26134v1](https://arxiv.org/abs/2510.26134) re-opened. Kahn–Saks progress, not a $1/3$ proof.
- [Wikipedia, *1/3–2/3 conjecture*](https://en.wikipedia.org/wiki/1/3%E2%80%932/3_conjecture), raw wikitext fetched 2026-08-27 (`last-modified` 26 Aug 2026). Still an unsolved problem; cites Gupta 2026 for order 14. Lists semiorders, not interval orders. Width-3 example still given as Saks $14/39$.
- [agupta/gold-partition-conjecture](https://github.com/agupta/gold-partition-conjecture) README re-opened. Order-14 GPC and balance census; no $n=22$ ladder table.
- [OEIS A367494](https://oeis.org/A367494) via `scripts/oeis_lookup.py` (API). Number of $(2+2)$-free naturally labelled posets on $[n]$: $1,1,2,7,37,272,2637,32469,493602,9062503,197409097,\ldots$. Exact match for the interval-order census through $n=10$.

Failed or unused: no arXiv paper since Gupta v2 closing the conjecture, Question 3.9, interval orders, or dimension 2. No published $n=22$ broken-rung minimum to compare against. The Wikipedia width-3 $14/39$ line is the 1992 record, not Gupta's $6/17$ tail.
