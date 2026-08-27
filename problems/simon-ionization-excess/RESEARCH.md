# Research log — simon-ionization-excess

Papers, OEIS, failed lookups. Only URLs opened this session.

## 2026-08-27

- [Simon, *Schrödinger operators in the twenty-first century*](http://www.math.caltech.edu/papers/bsimon/r40.pdf).
  OCR of all seven pages. Problem 9: prove N0(Z) − Z bounded as
  Z → ∞. Reprint cites Ruskai, Sigal, Lieb (N0 < 2Z),
  Lieb–Sigal–Simon–Thirring (N/Z → 1), Zhislin (N0 ≥ Z). Guess:
  N0 is always Z or Z+1.

- [Simon, *Fifteen problems in mathematical physics*](http://www.math.caltech.edu/SimonPapers/R27.pdf)
  (1984 Oberwolfach volume, pp. 423–454). Opened the PDF. Image
  scan; used together with Lewin and Coley for the 10(a)/10(c)
  pointer, not as a source of a numerical bound.

- [Wikipedia, Simon problems](https://en.wikipedia.org/wiki/Simon_problems)
  and [MathWorld, Simon's Problems](https://mathworld.wolfram.com/SimonsProblems.html).
  Map only.

- [Lewin, *Some open mathematical problems concerning charged quantum particles*](https://doi.org/10.5802/crphys.249)
  (*C. R. Physique* 26 (2025), 369–380;
  [PDF](https://comptes-rendus.academie-sciences.fr/physique/item/10.5802/crphys.249.pdf)).
  Open Problem 1: Nc ≤ Z + C M, still open even for huge C.
  Quotes Lieb Nc < 2Z+M and Nam Nc < 1.22 Z + 3 Z^{1/3}.
  Identifies the ask with Simon 1984 10(c). Open Problem 2 is
  convexity / 1984 10(a), still open for integer nuclear charge
  (a Coulomb counterexample exists only for tiny non-integer
  charges on six distant nuclei).

- [Nam, arXiv:1009.2367](https://arxiv.org/abs/1009.2367)
  ([HTML](https://ar5iv.labs.arxiv.org/html/1009.2367), v3).
  Theorem 1: if E(N,Z) is an eigenvalue then N = 1 or
  N < 1.22 Z + 3 Z^{1/3}. Beats Lieb for Z ≥ 6. Also
  limsup Nc/Z ≤ 1.22 in magnetic / pseudo-relativistic variants.
  Does not prove a Z-independent excess.

- [Nam, arXiv:2206.15393](https://arxiv.org/abs/2206.15393)
  (*The ionization problem in quantum mechanics*, Lieb 90th-birthday
  chapter). Restates the conjecture Nc ≤ Z + C. Quotes Nam 2012
  as Theorem 5. Does not claim a later linear coefficient.

- [Nam, *The ionization problem* (LMU chapter PDF)](https://www.math.lmu.de/~nam/Ionization-Lieb-Collection.pdf).
  Same survey text; opened for the printed 1.22 Z + 3 Z^{1/3} and
  the β ≥ 0.82 remark (1/β ≈ 1.22).

- [Hundertmark–Pattakos–Schulz, arXiv:2504.18487](https://arxiv.org/abs/2504.18487)
  ([HTML](https://arxiv.org/html/2504.18487v1)).
  Abstract: Nc(Z) < 1.1185 Z + O(Z^{1/3}) with an explicit
  remainder. Proposition 2.4 (s=2, Z ≥ 2):
  Nc < ((√2+1)/2) Z + 2.96 Z^{1/3}, and
  1.2071 < (√2+1)/2 < 1.2072.
  Proposition 2.5 (s=3, Z ≥ 4): the b(3) expansion displayed in
  PROBLEM.md, with 1.1184 < b(3) < 1.1185 and the closed form
  (2/3) (1+√2)^{1/3} / ((1+√2)^{2/3}−1).
  Coarser: N < 1.12 Z + 4 Z^{1/3} for Z ≥ 4, and
  Nc < 1.1185 Z + 4 Z^{1/3}.
  They remark that (2.9) beats (2.8) for Z ≥ 35.8, and that
  Prop. 2.4 already beats Nam for all Z ≥ 2.
  Fermion/boson distinction: bosonic lim Nc/Z = tc ≈ 1.21.

- [Coley, arXiv:1710.02105](https://arxiv.org/abs/1710.02105).
  Reprints 1984 problems as examples; not a bound on Nc.

- Failed: no OEIS sequence for Nc(Z). Did not obtain a free PDF of
  Lieb, *Phys. Rev. A* 29 (1984), 3018–3028; the statement
  Nc < 2Z+1 is taken from Nam, Hundertmark–Pattakos–Schulz, and
  Lewin, each of whom quote that display. Simon's reprint writes
  the slightly weaker N0 < 2Z.
