# Clay Millennium Prize Problems (2000)

Clay Mathematics Institute, Paris, 24 May 2000. Seven problems, one million
dollars each. Official list:
[The Millennium Prize Problems](https://www.claymath.org/millennium-problems/).

Status cutoff 2026-08-30. "Resolved" means CMI has accepted a solution.
Six remain open. Poincaré is the only prize that has been awarded
(announced 2010; Perelman declined).

This notebook already has Hilbert, Landau, Smale, and Simon lists. Riemann
is Hilbert 8(a) and Smale 1. Navier–Stokes is Smale 15. P vs NP is Smale 3.
Landau 3 (Legendre) in `problems/landau-legendre/` is an RH-conditional
explicit gap bound, not the Clay problem.

| # | Problem | Status | Note |
| ---: | --- | --- | --- |
| 1 | [Birch and Swinnerton-Dyer](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/) | Open | Rank equals analytic rank, with the usual leading-term formula. Many individual curves are checked; the conjecture is not. |
| 2 | [Hodge](https://www.claymath.org/millennium/hodge-conjecture/) | Open | Hodge classes on a non-singular complex projective variety are rational linear combinations of algebraic cycle classes. No finite-handle record in the style of this notebook. |
| 3 | [Navier–Stokes existence and smoothness](https://www.claymath.org/millennium/navier-stokes-equation/) | Open | Also Smale 15. 3D incompressible; Fefferman's Clay write-up. 2D is known. Tao's averaged model blows up; that does not settle the true equations. |
| 4 | [P vs NP](https://www.claymath.org/millennium/p-vs-np/) | Open | Also Smale 3. Circuit lower bounds and the τ-conjecture (Smale 4) are neighbouring finite questions; they are not a resolution. |
| 5 | [Poincaré](https://www.claymath.org/millennium/poincare-conjecture/) | Resolved (yes) | Perelman 2002–03, Ricci flow with surgery. CMI prize 2010. |
| 6 | [Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/) | Open | Also Hilbert 8(a) and Smale 1. First campaign for this list: see below. |
| 7 | [Yang–Mills existence and mass gap](https://www.claymath.org/millennium/yang-mills-the-maths-gap/) | Open | Construct quantum Yang–Mills on R^4 with a mass gap. No finite-handle record here. |

Order follows CMI's page, not Hilbert numbering.

## First campaign: Riemann

Among the six open Clay problems, this is the one with a living finite
handle. A dent here is a verified finite improvement of a published
explicit record, not a proof of RH.

Published records to replay before claiming anything (arXiv is the
record; blogs and GitHub audits are leads):

- Rodgers–Tao: the de Bruijn–Newman constant satisfies Λ ≥ 0
  ([arXiv:1801.05914](https://arxiv.org/abs/1801.05914), *Forum Math. Pi* 2020).
  RH is equivalent to Λ ≤ 0.
- Polymath 15 instantiated an effective heat-flow criterion for an
  *upper* bound. With the Platt–Trudgian verified-height input this
  has been used to get Λ ≤ 0.2 (Polymath 15 itself printed 0.22;
  later instantiations used the larger height). A later unofficial
  claim of 0.1787854 is a lead, not a citation, until it is on arXiv
  and independently replayed.
- Platt–Trudgian: RH verified for all zeros with imaginary part at
  most 3,000,175,332,800 ([arXiv:2004.09765](https://arxiv.org/abs/2004.09765),
  *Bull. LMS* 2021).
- Landau 3 in this notebook is RH-conditional (δ ≥ 0.22525) and does
  not move the Clay problem.

Current folder: [`problems/riemann-hypothesis/`](../../problems/riemann-hypothesis/).
The first computation replayed the published $0.2$ arithmetic and fresh parts
of the off-arXiv $0.1787854$ lead. The full finite producer and analytic review
remain, so the published explicit window is still $0\leq\Lambda\leq0.2$.

A failed search is residue, not a lower bound.
