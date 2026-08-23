# The Erdős–Szekeres number ES(7)

- Slug: `erdos-szekeres-seven`
- List: Green P45
- Solver: GPT-5.6 Sol
- Status: residue — the published interval was replayed, but the 33-vertex SAT run was unknown
- Area: Discrete and computational geometry
- Sources: Green P45; arXiv:2512.24061; JCTA 222 (2026), 106195
- Started: 2026-08-23

## Statement

Let ES(k) be the least integer N such that every set of N points in the
plane in general position, meaning no three are collinear, contains k points
in convex position. The first unknown value is ES(7). The Erdős–Szekeres
conjecture predicts ES(7) = 33.

The published interval is

$$
33 \leq ES(7) \leq 113.
$$

The lower bound is witnessed by the classical 32-point construction. The
upper bound is the k = 7 specialization of the Mojarrad–Vlachos bound. The
2026 Baek–Balko paper proves the conjectured threshold for decomposable point
sets and for split polygons, but does not improve either end of the interval
for arbitrary point sets.

## What would count as a new bound

Exact coordinates for 33 points in general position with no seven in convex
position would prove ES(7) >= 34. Any complete proof of ES(7) <= 112 would
improve the upper bound; in particular, a complete independently checked
UNSAT certificate at 33 would prove ES(7) = 33.

A new 32-point example only reproduces the known lower bound. A point-set
certificate must check every seven-subset in exact arithmetic. An empty
convex heptagon, or 7-hole, is a different object and does not certify the
required property. A restricted-family exclusion, an unfinished SAT run, or
a timeout does not change the published interval.
