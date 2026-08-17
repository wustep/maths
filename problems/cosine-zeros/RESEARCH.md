# Research log — zeros of integer cosine sums

## 2026-08-17

- [Ben Green, *100 Open Problems*, Problem 82](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) (Dec 2025 update), pp. 38–39. Statement: for `|A|=n`, how many `θ ∈ ℝ/ℤ` have `∑ cos(aθ) = 0`? Comments record BEFL `n^{5/6+o(1)}`, Juškevičius–Sahasrabudhe `O(n^{2/3} log^{2/3} n)`, Sahasrabudhe `(log log log n)^{1/2−o(1)}`, Bedert `(log log n)^{1-o(1)}`.
- [Bedert, *On the zeros of reciprocal Littlewood polynomials*, arXiv:2312.04454](https://arxiv.org/abs/2312.04454) — the source listed in `PROBLEM.md`. This is `Z_L(N) → ∞` for reciprocal `±1` polynomials, not the cosine-sum bound Green quotes as [27].
- [Bedert, *An improved lower bound for a problem of Littlewood on the zeros of cosine polynomials*, arXiv:2407.16075v2](https://arxiv.org/abs/2407.16075) (7 Jan 2025); published [Israel J. Math., 30 Nov 2025](https://link.springer.com/article/10.1007/s11856-025-2872-5). `Z(N) ≥ (log log N)^{1-o(1)}`. Theorem 1.3 is the precise form with unspecified `c>0`. Prop. 3.1 is the structured `L¹` bound; Prop. 4.4 is the period/`K` structure; §5 is the one-page combination.
- [Erdélyi, *Improved lower bound for the number of unimodular zeros…*, arXiv:1702.05823](https://arxiv.org/abs/1702.05823) / *Acta Arith.* 192 (2020). Theorem 1.7: Littlewood with constant `1/30` on `[0,2π]`. Lemmas 3.7–3.8: explicit `m`, `d_m < 3^m`, `log q`. Theorem 2.1 is the weaker `(log log log |P(1)|)/(log log log log |P(1)|)` bound.
- [Sahasrabudhe, *Counting zeros of cosine polynomials*, arXiv:1610.07680v3](https://arxiv.org/abs/1610.07680) / *Adv. Math.* 343 (2019). Lemmas 10–11: windows, periods `≤ 16 t log log(t+3)`, `φ(n) ≥ n/(8 log log n)` for `n>3`.
- [Juškevičius–Sahasrabudhe, *Cosine polynomials with few zeros*, arXiv:2005.01695v3](https://arxiv.org/abs/2005.01695) / *Bull. Lond. Math. Soc.* 53 (2021). Construction `f = D_n − g`, `𝔼 Z = Θ(n log m / √m + m)`, optimum `O((n log n)^{2/3})`. Deterministic Lemma 3.1: `Z` vs `|E(g)|`.
- [Konyagin, *On zeros of sums of cosines*, Math. Notes 108 (2020)](https://www.mathnet.ru/php/archive.phtml?wshow=paper&jrnid=mzm&paperid=12828&option_lang=eng) — independent `O((N log N)^{2/3})`.
- [Borwein–Erdélyi–Ferguson–Lockhart, *Ann. of Math.* 167 (2008)](http://www.cecm.sfu.ca/~pborwein/PAPERS/P205.pdf) — original `O(N^{5/6} log N)` counterexample to Littlewood's `N−1`.
- [McGehee–Pigno–Smith, *Ann. of Math.* 113 (1981)](https://annals.math.princeton.edu/1981/113-3/p09); DeVore–Lorentz book proof (Erdélyi's `1/30`). [Stegeman, *Math. Ann.* 261 (1982)](https://eudml.org/doc/182864) has `4/π³` for unweighted exponential sums; we used Erdélyi's `1/30` because it includes general coefficients `∑ |a_j|/j`.
- [MathOverflow 312265](https://mathoverflow.net/questions/312265/a-conjecture-of-littlewood) — Stegeman / Bloom comments on the Littlewood `L¹` constant.
- No source found tonight states a numerical `c` in `Z(N) ≥ c log log N / log log log N`, nor a construction beating `O((N log N)^{2/3})`. Later 2025–26 papers touching cosine polynomials (Erdélyi arXiv:2607.21877, Stankov, Brazitikos arXiv:2605.18087) do not improve `Z(N)`.

## Adjacent work tonight

- `problems/chowla-cosine` extracted `K(n) ≥ n^{1/7}/18` from a different Bedert paper (arXiv:2509.05260). Not reused except as a style template for an explicit-constant certificate. That folder was not modified.
