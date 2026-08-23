# Chromatic number of the plane

- Slug: `hadwiger-nelson-plane`
- Solver: GPT-5.6 Sol
- Status: residue — no lower-bound improvement
- Area: Discrete geometry; graph coloring; SAT
- Sources: de Grey arXiv:1804.02385v3; Parts arXiv:2010.12665v2;
  Sokolov–Voronov arXiv:2502.01958v1
- Started: 2026-08-23

## In general

Color every point of the Euclidean plane so that points at distance one have
different colors. The least possible number of colors is the chromatic number
of the plane, denoted by $\chi(\mathbb R^2)$. The published interval is

$$
5\leq\chi(\mathbb R^2)\leq7.
$$

De Grey's final arXiv version constructs a 1,581-vertex unit-distance graph
with chromatic number five; the earlier 1,567 count was corrected before the
final version. Parts later reduced the smallest published five-chromatic
example to 509 vertices and 2,442 edges. That 509-coordinate file has been
rebuilt in exact arithmetic in this checkout. Smaller five-chromatic graphs
are interesting but do not move the plane's lower bound.

## Precise statement

Find a finite set $V\subset\mathbb R^2$ with exact coordinates such that the
graph joining every pair of points of $V$ at distance one has chromatic number
six. Equivalently, produce both a checkable proof that five colors do not
suffice and an explicit proper six-coloring. Such a graph would prove

$$
6\leq\chi(\mathbb R^2)\leq7.
$$

## What would count as a new bound

A dent is an exact finite unit-distance graph with a verified 5-coloring
UNSAT certificate and a checked 6-coloring. Its coordinates, complete unit
edge set, coloring formula, proof, and independent verifiers must all replay.
This would improve de Grey's published lower bound from five to six.

A second permitted dent is a verified six-coloring of a specifically named
finite mosaic for which a paper documents seven as the best known coloring.
The fundamental domain, translations, boundary convention, and every
unit-distance conflict must be checked. Sokolov–Voronov's Theorem 2 rules
this out for a proper polygonal coloring of the whole plane, so no ordinary
polygonal tiling is a surviving candidate.

A SAT timeout, unfinished enumeration, numerical near-unit construction, or
unverified UNSAT report is residue. A new five-chromatic graph, including a
smaller one, does not improve the Hadwiger–Nelson bound attacked here.
