# No-three-in-line at n=71

- Slug: `three-in-line`
- Solver: Codex `gpt-5.6-sol` Max (2026-08-16 overnight). Grok watched only.
- Status: open
- Area: Discrete geometry
- Sources: Green 100 #72; Dudeney 1900 / Guy–Kelly 1968; Prellberg, arXiv:2602.07751; Heule 2026 (Flammenkamp database); MathWorld
- Started: 2026-08-16
- Tonight: finite-cex, cost M — SAT-search a 142-point configuration on the $71\times 71$ grid

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
Heule then found $2n$ configurations for $n=65,67,69,70,72$
(June 2026) and later $n=76$; Prellberg found $n=74$. Combined
with the classical range, $2n$ is known for every $n\le 70$ and
for $72,74,76$. **$n=71$ is the first hole.** Odd order cannot
use clean $C_4$ (rot4) orbits — the rotation centre is a lattice
point — so the natural symmetry is Flammenkamp's **rct4** (quarter-turn
except on the long diagonals; $D_4$ on the rest). Known odd
solutions at $n=65,67,69$ are rct4.

Tonight is only $n=71$. Find 142 points, or record a precise SAT
residue. Do not wander into the asymptotic $1.5n$ / Guy–Kelly
problem.

## Precise statement

A set $P\subseteq\{0,1,\dots,70\}^2$ is *no-three-in-line* if no
three distinct points of $P$ are collinear in $\mathbb{R}^2$:
equivalently, for all distinct $a,b,c\in P$,
$$
(b_x-a_x)(c_y-a_y)-(c_x-a_x)(b_y-a_y)\ne 0.
$$
**Tonight's finite subquestion.** Decide whether there exists a
no-three-in-line $P$ with $|P|=142$. Prefer an rct4-symmetric
search (the symmetry class of every known odd $2n$ solution for
$n\ge 33$ in the Flammenkamp/Heule database). If a configuration
is found, save the point list and a grid PNG. If not, record the
encoding, the solver, the timeout or unsat residue, and which
symmetry was enforced.

A SAT/CP encoding: one Boolean per cell (or per rct4 orbit);
for every line that meets the grid in $k\ge 3$ points, at most
two of those points are selected. Cardinality: exactly 142 points
(or exactly $142/|G|$ orbits, with diagonal orbits handled
carefully).

## What a solution looks like

- **Found.** `compute/n71-142.txt` (one `x y` per line), a verifier
  that checks $|P|=142$ and no three collinear, and
  `figures/n71-142.png` via `/maths/src/maths/figures.py`. Independently
  re-run the verifier.
- **Not found.** The CNF or CP model under `compute/`, the symmetry
  reduction, solver + version, wall-clock / timeout, and whether the
  result was timeout, unsat (on the restricted symmetry), or
  inconclusive. Unsat on rct4 is a residue, not a proof that
  $D(71)<142$.
- Do not claim $D(71)=142$ without a checked point list. Do not
  claim $D(71)<142$ without a complete (not symmetry-restricted)
  unsat proof. Do not start an asymptotic quest.

## Related

- [Ben Green, *100 Open Problems*, Problem 72](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Guy–Kelly, *The no-three-in-line problem*, Canad. Math. Bull. 1968](https://doi.org/10.4153/CMB-1968-007-3)
- [Prellberg, *Constraint Satisfaction Programming for the No-three-in-line Problem*, arXiv:2602.07751](https://arxiv.org/abs/2602.07751)
- [Flammenkamp, no-three-in-line database (Heule 2026 entries)](http://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html)
- [MathWorld, *No-Three-in-a-Line Problem*](https://mathworld.wolfram.com/No-Three-in-a-LineProblem.html)
- [formal-conjectures #1692, Green #72](https://github.com/google-deepmind/formal-conjectures/issues/1692)

## Quests so far


## Figures

None yet. If a configuration is found, embed `figures/n71-142.png` here.
