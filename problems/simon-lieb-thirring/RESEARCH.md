# Research log — simon-lieb-thirring

Papers, OEIS, failed lookups. Only URLs opened this session.

## 2026-08-27

- [Simon, *Schrödinger operators in the twenty-first century*](http://www.math.caltech.edu/papers/bsimon/r40.pdf)
  (Caltech reprint of *Mathematical Physics 2000*, pp. 283–288). OCR of
  all seven pages. Problem 15: prove the Lieb–Thirring conjecture on
  their constants for ν=1 and 1/2 < γ < 3/2. Known then: Aizenman–Lieb
  for γ ≥ 2 (reprint: γ ≥ 2; modern surveys state γ ≥ 3/2 after
  Laptev–Weidl) and Hundertmark–Lieb–Thomas at γ = 1/2. Also open
  for ν ≥ 2 and 0 < γ < 3/2. Classical and one-bound-state lower
  bounds are defined in the reprint.

- [Wikipedia, Simon problems](https://en.wikipedia.org/wiki/Simon_problems)
  and [MathWorld, Simon's Problems](https://mathworld.wolfram.com/SimonsProblems.html).
  Map only. MathWorld points at the same 2000 paper (mp_arc 00-78).
  Neither is the record for a constant.

- [Frank–Hundertmark–Jex–Nam, arXiv:1808.09017](https://arxiv.org/abs/1808.09017)
  ([HTML](https://arxiv.org/html/1808.09017v1);
  [JEMS 23 (2021), 2583–2600](https://doi.org/10.4171/jems/1062)).
  Theorem 1: L(1,d)/Lcl(1,d) ≤ 1.456 for all d ≥ 1. Previous best
  quoted: π/√3 ≈ 1.814 (Eden–Foias; Dolbeault–Laptev–Loss). Expected
  one-dimensional value 2/√3 ≈ 1.155. Finer line in the text:
  L(1,1)/Lcl ≤ 1.455786 from K1/Kcl ≥ 0.471851.

- [Schimmer, arXiv:2203.06051](https://arxiv.org/abs/2203.06051)
  ([PDF](https://arxiv.org/pdf/2203.06051)). Title: *The state of the
  Lieb–Thirring conjecture*. Not a Frank paper. Still open for
  1/2 < γ < 3/2 in dimension 1. Best ratio for 1 ≤ γ < 3/2 still
  1.456, citing FHJN as [20] / JEMS 2021. Records that the
  conjecture fails in some (γ,d) outside Simon's slot
  (Frank–Gontier–Lewin). Cites Frank arXiv:2007.09326 as the
  comprehensive review.

- [Frank, arXiv:2007.09326](https://arxiv.org/abs/2007.09326).
  *The Lieb–Thirring inequalities: Recent results and open problems*.
  Same 1.456 (his Theorem 5 / display (18)). Open interval for
  dimension 1 stated explicitly. Equality for γ ≥ 3/2 and for
  (γ,d) = (1/2,1).

- Failed / not a constant: no OEIS lookup. No later arXiv id opened
  this session claims a ratio below 1.456. A web search for
  post-2018 improvements of that specific number returned only
  restatements of FHJN.

- Classical formula replayed from the surveys, not from a forum:
  Lcl(γ,d) = 2^{−d} π^{−d/2} Γ(γ+1)/Γ(γ+1+d/2). Checked
  Lcl(1,1) = 2/(3π) and Lcl(3/2,1) = 3/16 against Schimmer's
  Gardner–Greene–Kruskal–Miura / Laptev–Weidl discussion.
