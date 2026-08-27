# Hilbert 16(b) — the Hilbert number H(n)

- Slug: `hilbert16-limit-cycles`
- List: Hilbert 16 (second part); Smale 13 (1998)
- Solver: Grok 4.6
- Status: open. Published lower bounds still stand. Hilbert
  16(b) itself is untouched.
- Area: Qualitative theory of planar polynomial ODEs
- Sources: Shi, Sci. Sinica 23 (1980); Chen–Wang 1979; Bautin
  1952/54; Li–Liu–Yang, JDE 246 (2009); Christopher–Lloyd,
  Proc. R. Soc. A 450 (1995); Han–Li, JDE 252 (2012);
  Prohens–Torregrosa, Nonlinearity 32 (2019); Gasull–Santana,
  arXiv:2407.13465; Eshkobilov–Kadyrov–Mamayusupov,
  arXiv:2604.12883
- Started: 2026-08-27

This folder is Hilbert 16(b): isolated periodic orbits of planar
polynomial vector fields. It is not the existing
`problems/hilbert16-degree-8/` folder, which is 16(a) for real
plane octics.

## In general

A planar polynomial vector field of degree n is a system

$$
\dot x = P(x,y),\qquad \dot y = Q(x,y)
$$

with P, Q real polynomials and max(deg P, deg Q) = n. A limit
cycle is an isolated periodic orbit. The Hilbert number H(n) is
the supremum of the number of limit cycles over all such fields
of degree at most n (the value +∞ is allowed). Hilbert asked
for a uniform finite upper bound in n and for the possible
configurations. Smale restated the upper-bound half as Problem
13 and called it, after RH, the most elusive of Hilbert's
problems.

Ilyashenko and Écalle independently proved that each individual
polynomial field has finitely many limit cycles. That is
finiteness per system, not a uniform H(n). Bamon (1986) had
already proved per-system finiteness in degree 2. It is still
not known whether H(2) itself is finite. Green–Smale 13 and
the Ilyashenko/Écalle theorems are context, not the table.

A quadratic formula H(n) = 2(n−1)(4(n−1)−2) appeared in
Entropy 26 (2024) and is not the record: it is quadratic in n,
which contradicts the Christopher–Lloyd n² log n lower bound
(Buzzi–Novaes, arXiv:2411.09594).

## Published record (fetched 2026-08-27)

Lower bounds are constructions. arXiv and the journals below
are the record; forum numbers are leads.

Small n, still cited as best in 2023–2026 papers that we
opened:

- H(1) = 0 (linear fields).
- H(2) ≥ 4, Shi Songling, Sci. Sinica 23 (1980), and
  independently Chen–Wang (1979). Configuration (3,1): three
  small cycles from a order-3 weak focus and one large cycle.
  Bautin proved that a quadratic focus has cyclicity at most 3,
  so four small cycles at one focus are excluded.
- H(3) ≥ 13, Li–Liu–Yang, J. Differ. Equations 246 (2009).
  Configuration (5:1|1:5) plus one surrounding cycle, via
  zeros of Abelian integrals. Local cyclicity M(3) ≥ 12
  (Giné–Gouveia–Torregrosa, JDE 275, 2021) is weaker than 13
  as a global lower bound.
- H(4) ≥ 28, H(5) ≥ 37, H(6) ≥ 53, H(7) ≥ 74, H(8) ≥ 96,
  H(9) ≥ 120, H(10) ≥ 142, Prohens–Torregrosa, Nonlinearity 32
  (2019), three-nest simultaneous Hopf from reversible Darboux
  centers.

Asymptotics:

- Christopher–Lloyd, Proc. R. Soc. A 450 (1995): H(n) grows
  at least as fast as n² log n, and the four-fold step
  H(2n+1) ≥ 4 H(n).
- Han–Li, J. Differ. Equations 252 (2012):
  liminf H(n) / ((n+2)² log(n+2)) ≥ 1/(2 log 2), and a table
  of explicit seeds (H(11) ≥ 153, H(14) ≥ 194, H(15) ≥ 345,
  H(19) ≥ 503, …).

Gasull–Santana, arXiv:2407.13465v2: if H(n) is finite then it
is attained by a structurally stable field with only hyperbolic
cycles, and H(n+1) ≥ H(n)+1.

Eshkobilov–Kadyrov–Mamayusupov, arXiv:2604.12883v1 (14 Apr
2026): separable Chebyshev pullback

$$
H(nm+m-1)\ge m^2 H(n)\qquad(m\ge 2).
$$

Combined with the Han–Li and Prohens–Torregrosa seeds they
record H(14) ≥ 252, H(29) ≥ 1080, H(31) ≥ 1380, H(39) ≥ 2012.
Those four numbers are theorem-only lifts of unreplayed seeds.
This folder replays the pullback identity and the arithmetic;
it does not independently reconstruct the Prohens–Torregrosa
or Han–Li centers.

Restricted families (not H(n) itself): Kolmogorov local
cyclicity M_K(3) ≥ 6, M_K(4) ≥ 13, M_K(5) ≥ 22
(Carvalho–Cruz–Gouveia, arXiv:2304.05111). Piecewise quadratic
H_p(2) ≥ 16 is a different number.

## Precise statement

Move a published H(n) lower bound by a verified construction,
or prove a new exact finite upper bound for some n or for a
documented restricted family, or produce a reusable exact
lemma that a stranger can replay.

## What would count as a new bound

A dent is a verified finite improvement of a published H(n),
or a new exact upper bound. Write the inequality and the
record it beats.

An incomplete search (numerical integration, SAT UNKNOWN, a
Poincaré–Bendixson picture without a certificate) is residue,
not a lower bound.

Replaying Shi's 4, Li–Liu–Yang's 13, or the 2026 Chebyshev
arithmetic is not a new bound. A lift H(nm+m−1) ≥ m² L_pub(n)
is not an independent lower bound unless the seed L_pub(n) is
itself replayed here.

## What does not count

- Hilbert 16(a), including anything in
  `problems/hilbert16-degree-8/`.
- Green–Smale 13 restated.
- Ilyashenko/Écalle per-system finiteness.
- Piecewise, discontinuous, or delay analogues, unless the
  claim is clearly labelled as a different function.
- The Entropy 2024 quadratic formula.
