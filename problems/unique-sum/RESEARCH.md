# Research log — Sets with no unique sum mod p

## 2026-08-16

- [OEIS A398173](https://oeis.org/A398173) then had 14 terms through p=47: 3,4,5,7,7,8,9,10,11,11,12,13,13,13.
- [Bedert, arXiv:2303.15134](https://arxiv.org/abs/2303.15134); [Cao–Yuan, arXiv:2608.06728](https://arxiv.org/abs/2608.06728).
- The first recovered run used the wrong predicate ($r=1$ rather than $r\notin\{1,2\}$); memory commit `77d43c5`.
- The recoded `green_m_p.csv` matched A398173 through p=47.

## 2026-08-23

- Fetched and read [Bedert, arXiv:2303.15134v2](https://arxiv.org/abs/2303.15134). Definition 1 uses unordered-pair uniqueness; in ordered notation the paper states that a unique sum is exactly $1\le r_A(g)\le2$. Theorems 3 and 5 give $m(p)\ge\omega(p)\log p$, with $\omega(p)\gg\sqrt{\log^{(3)}p}/\log^{(4)}p$, and $m(p)\ll(\log p)^2$.
- Fetched and read [Cao–Yuan, arXiv:2608.06728v1](https://arxiv.org/abs/2608.06728). Theorem 1.1 gives $m(p)\gg\log p\log\log p$. Theorem 1.3 gives the independent upper construction with leading constant $1/(2(\log_2 3)^2)=0.1990361769\ldots$; the paper explicitly says all unsubscripted logarithms are natural.
- Reopened [OEIS A398173](https://oeis.org/A398173). It now has 15 terms through $p=53$, with $m(53)=14$ added by Paweł Kwaczyński on 2026-07-29. Thus $p=59$ is the first prime at which a finite computation here could extend the published table.

## 2026-09-05 — q4 source check

- Fetched [Bedert v2](https://arxiv.org/pdf/2303.15134v2) with
  `scripts/arxiv_fetch.py` and read Definition 1 and the ordered representation
  convention in section 2. Both multiplicities 1 and 2 are forbidden. Opened
  the [abstract](https://arxiv.org/abs/2303.15134) and
  [HTML](https://arxiv.org/html/2303.15134v2) as well.
- Fetched [Cao–Yuan v1](https://arxiv.org/pdf/2608.06728v1) with the same
  script and read the introduction and Theorems 1.1–1.3. The explicit
  asymptotic lower constant does not decide the boundary at 59. Opened the
  [abstract](https://arxiv.org/abs/2608.06728) and
  [HTML](https://arxiv.org/html/2608.06728v1). No asymptotic improvement is
  attempted here.
- [OEIS A398173](https://oeis.org/A398173): the browser fetch timed out;
  `scripts/oeis_lookup.py A398173` succeeded after network authorization,
  showing the sequence definition and its first 12 terms (the helper truncates
  output). The 15-term baseline supplied for this run is also in the notebook;
  all 15 saved witnesses passed the direct arithmetic verifier.
