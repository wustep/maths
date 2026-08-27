# Smale 16 — the plane Jacobian conjecture

- Slug: `smale-jacobian-n2`
- Status: open — dent: an exact replay excludes the published exceptional
  degree pair \((72,108)\), giving

  $$
  \max\{\deg P,\deg Q\}\ge 125
  $$

  for every hypothetical plane counterexample. This does not prove the
  conjecture.
- Area: affine algebraic geometry; polynomial automorphisms; computer algebra
- Started: 2026-08-27

## In general

Let \(F=(P,Q):\mathbb C^2\to\mathbb C^2\) be a polynomial map. The plane
Jacobian conjecture says that if

$$
\det JF=P_xQ_y-P_yQ_x\in\mathbb C^*,
$$

then \(F\) is invertible and its inverse is polynomial. Linear changes and a
rescaling reduce the nonzero constant to 1.

The conjecture remains open in two variables. The 2026 announcements of
higher-dimensional counterexamples are not treated here as settled, and in
any case do not settle the plane problem.

## Published finite record

Moh excluded plane counterexamples through degree 100. Guccione, Guccione,
Horruitiner and Valqui subsequently proved that a counterexample must satisfy
one of

$$
\max\{\deg P,\deg Q\}\ge125,
\qquad
(\deg P,\deg Q)\in\{(72,108),(108,72)\}.
$$

Their Proposition 4.3 turns the exceptional pair into two explicit systems of
Laurent-polynomial coefficient equations with bracket \([P,Q]=x^2\). A 2026
archive by Billel Helali gives exact characteristic-zero certificates that both
systems generate the unit ideal. The q1 verifier pins that archive, replays all
of its identities, and independently checks the bridge from the published
Newton polygons to the coefficient systems.

## Precise finite question attacked here

Are either of the two Laurent systems in Proposition 4.3 consistent over an
algebraically closed field of characteristic zero? If both are inconsistent,
the exceptional degree pair disappears and the next possible maximum degree
is at least 125.

## What would count as a new bound

The record before this attack still allowed maximum degree 108. A dent is an
exact, reproducible exclusion of both \((72,108)\) systems, together with a
check of the reduction and normalization that connect them to the published
degree list. The resulting inequality must be written as

$$
\max\{\deg P,\deg Q\}\ge125.
$$

An unfinished Gröbner-basis calculation, a modular inconsistency, or a search
over only part of either coefficient system is residue and changes no bound.

## Sources

- [Keller, *Ganze Cremona-Transformationen* (1939)](https://doi.org/10.1007/BF01695502)
- [Bass–Connell–Wright, degree reduction and formal inverse (1982)](https://doi.org/10.1090/S0273-0979-1982-15032-7)
- [Moh, *On the Jacobian conjecture and the configurations of roots* (1983)](https://doi.org/10.1515/crll.1983.340.140)
- [Guccione–Guccione–Horruitiner–Valqui, arXiv:2204.14178v1](https://arxiv.org/abs/2204.14178v1)
- [Helali, exact \((72,108)\) certificate archive](https://doi.org/10.5281/zenodo.21479814)
