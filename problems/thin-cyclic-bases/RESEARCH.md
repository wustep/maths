# Research log — thin cyclic additive bases

## Status (accessed 2026-08-17)

- [Green, *100 Open Problems*, Problem 33](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025 update): **OPEN**. “Potentially yes, but I’m not sure I
  know how to construct such sets.” Prime-modulus variant equivalent
  to a near-optimal direction set on the parabola in $\mathbb F_p^2$.
- Granville via Croot–Lev, Problem 5.2 (CRM 43, 2007): smallest
  direction-determining set in $\mathbb F^r$. Counting
  $\sqrt2\,q^{(r-1)/2}$; Konyagin matches up to a constant via a
  difference basis.
- Caprace–de la Harpe, [arXiv:1807.04992](https://arxiv.org/abs/1807.04992),
  Confluentes Math. 12 (2020): $n_p>\sqrt{2p}$,
  $n_p\le2\lceil\sqrt p\rceil+1$ (Fitch–Jamison). Exact $n_p$ open.

## Published record on $\mathrm{SS}(n,2)=\min\{|A|:A+A=\mathbb Z/n\mathbb Z\}$

| quantity | bound | source |
| --- | --- | --- |
| all $n$, counting | $\mathrm{SS}(n,2)\ge(-1+\sqrt{1+8n})/2$ | pair count |
| all $n$, elementary | $\mathrm{SS}(n,2)<2\sqrt n+O(1)$ | interval + AP |
| all large $n$ | any $c>\sqrt3\approx1.732$ | Jia–Shen, SIDMA 31 (2017) |
| infinitely many $n$ | $\liminf\mathrm{SS}(n,2)/\sqrt n\le\sqrt{8/3}\approx1.63299$ | Bevan–Erskine–Lewis, arXiv:1506.04962, Cor. 18 |
| interval bases (hence cyclic) | $\sqrt{3.5}\approx1.871$ | Mrose |
| difference cover | $\Delta[\mathbb Z_n]/\sqrt n\to1$ along Singer/Bose | Banakh–Gavrylkiv arXiv:1702.02631 |
| exact small $n$ | cyclic through $n=67$ at size 13; all abelian through 85 | Haanpää, JIS 7 (2004); Fitch–Jamison through 54 |

No later improvement of BEL’s liminf, or of Jia–Shen’s universal
$\sqrt3+\varepsilon$, found after those papers (search through
2026-08-17, including Lewis’s 2021 thesis and Erskine’s later
degree-diameter work). Vetrík’s $L^-(2)\ge8/9$ is for general
directed Cayley graphs, not cyclic groups; it would violate the
sum-cover counting bound if it were cyclic.

## Independent checks (this folder)

```bash
python3 compute/make_bel_certs.py
python3 compute/haanpaa_replay.py
python3 compute/verify.py
```

- BEL $q=7,13,19,31,37,43,61$: product-group cover and cyclic
  `A+A` both hold. Ratios $1.932\to1.660$, consistent with
  $\sqrt{8/3}$. Certificates in `compute/certs/bel_q*.json`.
  Greedy deletion on $q=13,19$ drops nothing.
- Haanpää Table 3, cyclic rows: all twelve covers verify. Isolated
  small-$n$ ratios $1.15$–$1.59$ are **not** a dent.

## What we did not beat

- Green’s $(\sqrt2+o(1))\sqrt q$ for infinitely many $q$.
- BEL’s liminf $\sqrt{8/3}$.
- Jia–Shen’s universal $\sqrt3+\varepsilon$.
- Caprace–de la Harpe’s exact $n_p$.

Failed templates (logs in `compute/`): equal-length 3-AP families;
Singer/Bose interval and AP repairs; Singer greedy completion;
two-AP deletion; quadratic windows; geometric progressions; local
search at Haanpää scale. Search residue is not a bound.

## Did not claim

The Green problem. An improvement of $\sqrt{8/3}$. A finite table
as an asymptotic density.
