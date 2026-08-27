# Research log — Smale 16 / plane Jacobian conjecture

Papers, exact source checks, and failed lookups. Forum posts were used only to
find primary artifacts; no forum number is treated as a citation.

## 2026-08-27 — classical record

- Keller, [*Ganze Cremona-Transformationen*](https://doi.org/10.1007/BF01695502),
  *Monatshefte für Mathematik und Physik* 47 (1939), 299–306. The Springer
  landing page opened, but the article scan was paywalled. The bibliographic
  record was cross-checked against the University of Halle
  [Keller bibliography](https://disk.mathematik.uni-halle.de/history/keller/index.html).
  This is the conventional 1939 source of the conjecture.

- Bass, Connell and Wright,
  [*The Jacobian conjecture: reduction of degree and formal expansion of the inverse*](https://doi.org/10.1090/S0273-0979-1982-15032-7),
  *Bull. AMS* 7 (1982), 287–330. The
  [AMS/CiNii record and PDF link](https://cir.nii.ac.jp/crid/1363670319632054016)
  and an [author-uploaded full text](https://www.researchgate.net/publication/38390367_The_Jacobian_Conjecture_Reduction_of_degree_and_formal_expansion_of_the_inverse)
  were opened. The relevant reduction replaces a general Keller map, after
  stabilization, by \(X-H\) with \(H\) cubic homogeneous and \(JH\)
  nilpotent; the paper also gives the rooted-tree expansion of the formal
  inverse.

- Drużkowski,
  [*An effective approach to Keller's Jacobian conjecture*](https://doi.org/10.1007/BF01459126),
  *Math. Ann.* 264 (1983), 303–313. The original scan was fetched from the
  [Göttinger Digitalisierungszentrum](https://gdz.sub.uni-goettingen.de/id/PPN235181684_0264).
  Drużkowski further reduces the general problem to cubic-linear maps
  \(X+(AX)^{*3}\). This raises the dimension and is not a low-degree
  classification in the original two variables.

- Moh,
  [*On the Jacobian conjecture and the configurations of roots*](https://doi.org/10.1515/crll.1983.340.140),
  *J. Reine Angew. Math.* 340 (1983), 140–212. The publisher metadata opened,
  but the scan did not. Moh's
  [author page](https://www.math.purdue.edu/~ttm/jacobian.html) explicitly
  records the computer-assisted exclusion through degree 100 and the
  approximate-root/Diophantine-tree data. Later papers note that the full
  case analysis is difficult to replay from the printed article, so this
  notebook uses the later explicit degree enumeration as its immediate input.

- Appelgate and Onishi,
  [*The Jacobian conjecture in two variables*](https://doi.org/10.1016/0022-4049%2885%2990099-4),
  *J. Pure Appl. Algebra* 37 (1985), 215–227. The publisher endpoint rejected
  an automated PDF request; the
  [bibliographic summary](https://portal.mardi4nfdi.de/wiki/Item%3AQ1061790)
  records their result that the conjecture holds if either coordinate degree
  is a product of at most two primes. The follow-up
  [Nowicki–Nakai paper](https://doi.org/10.1016%2F0022-4049%2888%2990115-6)
  was opened as a check on the cited lemmas.

## 2026-08-27 — finite degree frontier

- Nguyen,
  [*Some classes satisfying the 2-dimensional Jacobian conjecture and a proof of the complex conjecture until degree 104*](https://arxiv.org/abs/1902.05923v5),
  updated 27 March 2025 and published in *Quaestiones Mathematicae* 48(2).
  The HTML and abstract were replayed. It claims the complex plane conjecture
  through degree 104. This is compatible with, but weaker than, the more
  explicit degree-pair result below.

- Guccione, Guccione, Horruitiner and Valqui,
  [*Increasing the degree of a possible counterexample to the Jacobian Conjecture from 100 to 108*](https://arxiv.org/abs/2204.14178v1),
  29 April 2022. The abstract, Theorem 2.1, and Proposition 4.3 were checked in
  the [arXiv HTML](https://arxiv.org/html/2204.14178). Theorem 2.1 says that a
  counterexample has maximum degree at least 125 or degree pair \((72,108)\),
  up to transposition. Proposition 4.3 reduces that exception to exactly two
  Newton-polygon systems with \([P,Q]=x^2\).

- Billel Helali,
  [*Exact certificate replay for the JC2 degree pair (72,108)*](https://github.com/bilLkarkariy/jc2-72-108-exact-certificates),
  archived at [Zenodo DOI 10.5281/zenodo.21479814](https://doi.org/10.5281/zenodo.21479814).
  The Git repository was checked out at commit
  `c530fe44e5f53b17840110931803e7c7c5a24cde`. Its 86 MB replay bundle has
  SHA-256
  `232204bdb598cc2ea0368e154c8573e18bbfdc69fa631c8878de4b884b38bb18`.
  A direct Zenodo page request failed, so the DOI, metadata, archive hash, and
  license were checked through the pinned Git source and its release bundle.

- Clean exact replay in a fresh Python 3.14 virtual environment passed every
  serialized unit-ideal certificate, the independent `gmpy2` arithmetic
  path, the branch involution, and both hard identities. The terminal markers
  were `ALL_SERIALIZED_EXACT_CERTIFICATES_PASS`, `GMPY2_EXACT_PASS`,
  `BRANCH1_EXACT_IDENTITY_PASS`, `BRANCH2_EXACT_IDENTITY_PASS`, and
  `JC2_72_108_EXACT_REPLAY_PASS`. The independent arithmetic path evaluated
  13,410 number-field products, or 335,250 scalar products.

- The transcription was checked directly against Proposition 4.3. Its Case 1
  polygons contain 61 and 125 lattice points; Case 2 contains 25 and 47. With
  \(t=xy^2\) and \(z=y^{-1}\), the identities \([t,z]=-1\) and
  \(x^2=t^2z^4\) reproduce the archive's five coefficient equations. The
  three chosen nonzero vertex coefficients can be normalized because the
  corresponding exponent matrix is nonsingular over an algebraically closed
  field. These checks are reimplemented in q1 in both Python and Rust.

## 2026-08-27 — recent approaches and claims

- Lee and Li,
  [*On the two-dimensional Jacobian conjecture: Magnus' formula revisited, IV*](https://arxiv.org/abs/2408.01279v1),
  2 August 2024. The paper bounds the northeastern vertex of inner Newton
  polygons and proves special cases of several proposed reductions. It does
  not give a general inverse or a stronger finite degree bound.

- Zwart,
  [*Mathieu's approach to the Jacobian Conjecture*](https://arxiv.org/abs/2511.16561v2),
  21 November 2025. This is an expository account of a Lie-theoretic
  conjecture implying the Jacobian conjecture. The implication is not a proof
  of the plane case.

- Rodríguez Díaz,
  [*On the origin of the Jacobian conjecture*](https://arxiv.org/abs/2512.23614v1),
  29 December 2025. The paper traces the statement to Kraus (1884), identifies
  the last step of Kraus's proof as flawed, and frames ramification at infinity
  as the unresolved obstruction.

- Meng and Yang,
  [*A five-variable counterexample to the Hessian conjecture, and the low-dimensional status of the Jacobian and Hessian conjectures*](https://arxiv.org/abs/2607.22198v2),
  27 July 2026, and Gao,
  [*Counterexamples to the Jacobian conjecture in dimensions greater than two*](https://arxiv.org/abs/2608.00222v1),
  31 July 2026, build on Alpöge's announced three-variable example. These are
  recent preprint claims, not community consensus in this notebook. Both say
  explicitly that the two-variable conjecture remains open. Gao's tangent-line
  sweep motivated q3, which checks why the raw sweep cannot itself be Keller
  in two dimensions.

