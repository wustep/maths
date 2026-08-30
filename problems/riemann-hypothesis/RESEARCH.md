# Research log — Riemann hypothesis

Papers, leads, and failed lookups. arXiv is the record; GitHub repositories
are implementation leads.

## 2026-08-30 — primary record

- [Clay Mathematics Institute, *Riemann hypothesis*](https://www.claymath.org/millennium/riemann-hypothesis/).
  Read the official problem page; CMI lists RH as unsolved.
- [Rodgers–Tao, *The De Bruijn-Newman constant is non-negative*,
  arXiv:1801.05914v5](https://arxiv.org/abs/1801.05914). Fetched with
  `scripts/arxiv_fetch.py`. The paper proves $\Lambda\geq0$ and recalls that
  RH is equivalent to $\Lambda\leq0$.
- [Polymath 15, *Effective approximation of heat flow evolution of the
  Riemann $\xi$ function, and a new upper bound for the de Bruijn-Newman
  constant*, arXiv:1904.12438v2](https://arxiv.org/abs/1904.12438). Fetched
  with the helper. Theorem 1.1 states $\Lambda\leq0.22$. Theorem 1.2 is the
  effective height/asymptotic-region/barrier criterion. Section 10, Table 1
  prints the later $0.20$ parameter row.
- [Platt–Trudgian, *The Riemann hypothesis is true up to $3\cdot10^{12}$*,
  arXiv:2004.09765v1](https://arxiv.org/abs/2004.09765). Fetched with the
  helper. Theorem 1 verifies RH through height $3{,}000{,}175{,}332{,}800$,
  covering the lowest $12{,}363{,}153{,}437{,}138$ zeros. Corollary 2 states
  $\Lambda\leq0.2$ using Polymath 15.

## 2026-08-30 — identifier corrections and failed lookups

- [arXiv:2007.02194, *30 Years of Software Refactoring Research: A Systematic
  Literature Review*](https://arxiv.org/abs/2007.02194). The supplied
  Platt–Trudgian identifier resolves to this unrelated computer-science paper.
  It was fetched before the mismatch was noticed and is not an RH source.
- [arXiv:0809.1846, *A removal lemma for systems of linear equations over
  finite fields*](https://arxiv.org/abs/0809.1846). A guessed identifier for
  the Saouter–Gourdon–Demichel paper was unrelated. No arXiv version of that
  paper was located.

## 2026-08-30 — Lehmer-pair lower bound

- [Saouter–Gourdon–Demichel, *An improved lower bound for the de Bruijn-Newman
  constant*, Math. Comp. 80 (2011), 2281–2287](https://www.ams.org/journals/mcom/2011-80-276/S0025-5718-2011-02472-5/S0025-5718-2011-02472-5.pdf).
  Fetched the official AMS PDF. The paper proves the historical bound
  $\Lambda>-1.14541\cdot10^{-11}$ from a Lehmer pair near height
  $7.954\cdot10^{12}$. The four printed ordinates and Theorem A formula were
  replayed in `compute/q1/`. Rodgers–Tao's later $\Lambda\geq0$ dominates it.

## 2026-08-30 — implementation leads

- [Jude Gomila, `dbn-lambda-01787854-candidate-audit`](https://github.com/judegomila/dbn-lambda-01787854-candidate-audit),
  commit [`a74738d`](https://github.com/judegomila/dbn-lambda-01787854-candidate-audit/commit/a74738deb6d5e0f76887cb36901da08b68dca705).
  The repository proposes $\Lambda\leq0.1787854$ and explicitly labels the
  assembly as not yet peer reviewed. It is off arXiv, so this notebook treats
  it as a lead. The stored assembly passed; fresh tail, error, and barrier
  lanes were regenerated, and a fresh finite-producer run matched the first
  sealed row. The full finite range and analytic bridge were not independently
  replayed.
- [K. M., `dbn_upper_bound`](https://github.com/km-git-acc/dbn_upper_bound).
  Opened as an older implementation lead for the Polymath 15 computation. No
  number from this repository was promoted into the record.
