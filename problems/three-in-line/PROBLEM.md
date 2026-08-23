# No-three-in-line at n=71

- Slug: `three-in-line`
- Solver: Codex `gpt-5.6-sol` Max (2026-08-16 search; 2026-08-23 replay). Grok watched only.
- Status: $D(71)=142$ (Heule 2026; independently replayed)
- Area: Discrete geometry
- Sources: Green 100 #72; Dudeney 1900 / Guy–Kelly 1968; Prellberg, arXiv:2602.07751; Heule 2026 (Flammenkamp database); MathWorld
- Started: 2026-08-16
- Campaign: recover and independently replay a 142-point certificate on the $71\times 71$ grid

## In general

Place as many points as possible on the $n\times n$ grid
$\{0,\dots,n-1\}^2$ so that no three are collinear (any slope, not
just axis-aligned). Pigeonhole on rows gives $D(n)\le 2n$. The
no-three-in-line problem asks whether $D(n)=2n$ for every $n$, or
only for small $n$. Green #72 records both the finite question and
the asymptotic one (Guy–Kelly suggested $\sim(\pi/\sqrt{3})n\approx 1.81n$,
so $2n$ would eventually fail; Hall-type constructions still give
almost $2n$ for infinitely many $n$).

The finite record moved fast in 2026. Prellberg (arXiv:2602.07751)
used symmetry-reduced CP-SAT to get $D(n)=2n$ for all $n\le 60$.
Flammenkamp's dated database then recorded Prellberg configurations at
$n=61,62,63,64,66,68,74$ and Heule configurations at
$n=65,67,69,70,72,76$. On 17 August 2026 Heule found an rct4
configuration at $n=71$, followed by $n=73$ on 19 August. Thus $2n$ is
now known for every $n\le74$ and for $n=76$; the first current hole is
$n=75$.

This folder remains scoped to $n=71$. The external database code has been
decoded to 142 coordinates and checked by two exact implementations. Odd
order cannot use clean $C_4$ (`rot4`) orbits—the rotation centre is a lattice
point—so the relevant symmetry is Flammenkamp's **rct4**, with four-orbits
off the diagonal and half-turn pairs on it.

## Precise statement

A set $P\subseteq\{0,1,\dots,70\}^2$ is *no-three-in-line* if no
three distinct points of $P$ are collinear in $\mathbb{R}^2$:
equivalently, for all distinct $a,b,c\in P$,
$$
(b_x-a_x)(c_y-a_y)-(c_x-a_x)(b_y-a_y)\ne 0.
$$
**Finite result.** The certificate in `compute/n71-142.txt` has
$|P|=142$ and no collinear triple. The original database entry is rct4.
Together with the row bound, this gives $D(71)=142$.

A SAT/CP encoding: one Boolean per cell (or per rct4 orbit);
for every line that meets the grid in $k\ge 3$ points, at most
two of those points are selected. Cardinality: exactly 142 points
(or exactly $142/|G|$ orbits, with diagonal orbits handled
carefully).

## What a solution looks like

- **Found and replayed.** `compute/n71-142.txt` stores one `x y` pair per
  line. `compute/q3/run_all.sh` checks the pinned database code and runs both
  the Python determinant verifier and the independent Rust normalized-line
  verifier. `figures/n71-142.png` displays the certificate.
- **Not found.** The CNF or CP model under `compute/`, the symmetry
  reduction, solver + version, wall-clock / timeout, and whether the
  result was timeout, unsat (on the restricted symmetry), or
  inconclusive. Unsat on rct4 is an incomplete search, not a proof that
  $D(71)<142$.
- Do not claim $D(71)=142$ without a checked point list. Do not
  claim $D(71)<142$ without a complete (not symmetry-restricted)
  unsat proof. Do not start an asymptotic campaign from this folder.

## Related

- [Ben Green, *100 Open Problems*, Problem 72](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Guy–Kelly, *The no-three-in-line problem*, Canad. Math. Bull. 1968](https://doi.org/10.4153/CMB-1968-007-3)
- [Prellberg, *Constraint Satisfaction Programming for the No-three-in-line Problem*, arXiv:2602.07751](https://arxiv.org/abs/2602.07751)
- [Flammenkamp, no-three-in-line database (Heule 2026 entries)](http://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html)
- [MathWorld, *No-Three-in-a-Line Problem*](https://mathworld.wolfram.com/No-Three-in-a-LineProblem.html)
- [formal-conjectures #1692, Green #72](https://github.com/google-deepmind/formal-conjectures/issues/1692)

## Campaigns so far

- The 16 August rct4 CP-SAT and SAT runs ended `UNKNOWN`; their generated CNF
  was not preserved in this checkout.
- On 23 August the current database certificate decoded and passed both exact
  verifiers, proving $D(71)=142$.

## Figures

![Heule's 142-point rct4 configuration at n=71](figures/n71-142.png)
