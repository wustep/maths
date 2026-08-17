# Research log — Chowla's cosine problem

## 2026-08-17

- [Ben Green, *100 Open Problems*, Problem 81](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) (Dec 2025 update). Statement: `∑_{a∈A} cos(aθ) ≤ −c √n`? Comments record Ruzsa `exp(−c √log n)` as the pre-2025 record and Bedert / JMTZ as the 2025 polynomial bounds, quoting Bedert as any exponent `< 1/7` (that is the v2 exponent; v3 is `1/5−o(1)`).
- [Open Problem Garden, *Chowla's cosine problem*](https://www.openproblemgarden.org/op/chowlas_cosine_problem).
- [Bedert, *Polynomial bounds for the Chowla Cosine Problem*, arXiv:2509.05260v3](https://arxiv.org/abs/2509.05260) (24 Jul 2026). `K(n) ≫ n^{1/5−o(1)}`; §5 gives `n^{1/12}`; §7 gives `n^{1/7}` then the log-improved `|B_t|`. No numerical `c`. Lemma 7.2 is the 32-window table we re-checked.
- [Jin–Milojević–Tomon–Zhang, *From small eigenvalues to large cuts, and Chowla's cosine problem*, arXiv:2509.03490v2](https://arxiv.org/abs/2509.03490). `n^{1/10−o(1)}`. Spectral-graph method; no numerical `c`.
- [Ruzsa, *Negative values of cosine sums*, Acta Arith. 111 (2004)](http://eudml.org/doc/278427). `K(n) ≥ exp(c' (log n)^{1/2})`. Lemma 4.2 / 3.1 is the AP bound we instantiate as `L ≤ 8K^2+8`.
- [Roth, *On cosine polynomials corresponding to sets of integers*, Acta Arith. 24 (1973)](https://doi.org/10.4064/AA-24-1-87-98). Energy lemma (Bedert Lemma 4.1).
- [McGehee–Pigno–Smith, *Hardy's inequality and the L¹-norm of exponential sums*, Ann. of Math. 113 (1981)](https://doi.org/10.2307/2007000); Konyagin, Izv. Akad. Nauk SSSR 45 (1981). `L¹ ≫ log n`, hence `K(n) ≫ log n`. Steen notes: `A = 128` is an admissible `L¹` constant.
- [Brazitikos, *Sharp estimates for conjugate functions*, arXiv:2605.18087](https://arxiv.org/abs/2605.18087) (18 May 2026). Cites Bedert `n^{1/7−o(1)}` and JMTZ `n^{1/10−o(1)}`; no better Chowla exponent and no explicit `c`.
- [Quanta, 28 Jan 2026](https://www.quantamagazine.org/networks-hold-the-key-to-a-decades-old-problem-about-waves-20260128/) — popular account of the 2025 polynomial bounds (quotes Bedert `n^{1/7}` as of that date).
- Sidon-difference construction (Bedert §1, following the classical example): `K(n) ≪ √n`. Chowla 1965 conjectured this is sharp.

No source found tonight states an explicit numerical `c` in `K(n) ≥ c n^α` for a fixed `α > 0`.
