# Determine R(5,5)

- Slug: `ramsey-r55`
- List: P41
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Ramsey theory
- Sources: Radziszowski Small Ramsey Numbers revision 18 (2026); Angeltveit–McKay R(5,5)<=46
- Started: 2026-08-17

## Statement

The diagonal Ramsey number satisfies 43 <= R(5,5) <= 46 as of the April 2026 dynamic survey. Deciding any of the three remaining gaps is open.

## Tonight

A certified 43-vertex Ramsey graph, a nonexistence proof at 45 with an independently checkable log, or a documented incomplete search. Isolated SAT timeouts are not a new bound. Fetch the current Radziszowski bounds before searching.

## Status (2026-08-27)

Published record still $43\le R(5,5)\le 46$ (Radziszowski rev. 18, 24 April 2026; Angeltveit–McKay). No endpoint moved. Residue in `compute/q1/`: none of the 4080 one-flip neighbours of the 656 extend; no legal-degree Cayley $(5,5)$-graph on any group of order 44 or 45; no strongly regular graph on 43 vertices in the legal degree window; $C_7$ SAT at 42 and 43 timed out. See `ATTACK.md`, `WALKTHROUGH.md`, `RESEARCH.md`.


## Status (2026-08-28)

Published record still $43\le R(5,5)\le 46$. No endpoint moved. Residue in
`compute/q2/`: complete two-edit ball around the 656 does not extend; listed
prime-order automorphism cycle types on 43 vertices are DRAT-UNSAT; a
radius-6 ball around a score-2 near graph is DRAT-UNSAT. Small-prime SAT
timeouts remain UNKNOWN. See `ATTACK.md` and `compute/q2/README.md`.

## Status (2026-08-29)

Published record still $43\le R(5,5)\le46$. No endpoint moved. Residue in
`compute/q3/`: checked DRAT/DRUP certificates exclude every order-7
automorphism cycle type on 43 vertices. Together with q2, a hypothetical
$(5,5,43)$-graph has automorphism-group order with prime divisors only among
2, 3, and 5. The maximum-cycle order-2, order-3, and order-5 instances remain
`UNKNOWN`, and their other cycle types are not exhaustively searched. This is
an automorphism restriction, not a bound on $R(5,5)$.

## Status (2026-08-29, q4)

Published record still $43\le R(5,5)\le46$. No endpoint moved. Residue in
`compute/q4/`: checked DRAT certificates exclude automorphism cycle types
$5^6 1^{13}$ and $5^7 1^8$ on 43 vertices. The maximum-cycle order-2,
order-3, and order-5 instances remain `UNKNOWN`, and the other leftover
2/3/5 cycle types are not exhaustively searched. This is an automorphism
restriction, not a bound on $R(5,5)$.

## Status (2026-08-29, leftover 2/3/5 after 5^6 and 5^7)

Published record still $43\le R(5,5)\le46$. No endpoint moved. Residue in
`compute/q5/`: a checked DRAT certificate excludes automorphism cycle type
$5^4 1^{23}$ at $k\in\{0,4\}$ on 43 vertices. The maximum-cycle order-2,
order-3, and order-5 instances remain `UNKNOWN` at thirty minutes, and the
other leftover 2/3/5 cycle types are not exhaustively searched. This is an
automorphism restriction, not a bound on $R(5,5)$.

## Status (2026-08-29, leftover 2/3/5 after 5^4 at k=4)

Published record still $43\le R(5,5)\le46$. No endpoint moved. Residue in
`compute/q6/`: a checked DRAT certificate excludes automorphism cycle type
$5^5 1^{18}$ at $k\in\{2,3\}$ on 43 vertices. The other neighbour count on
that type, the five maximum-cycle order-2/3/5 instances, and the rest of
the leftover 2/3/5 list remain unfinished. This is an automorphism
restriction, not a bound on $R(5,5)$.

## Status (2026-08-29, leftover 2/3/5 after 5^5 at k=2)

Published record still $43\le R(5,5)\le46$. No endpoint moved. Residue in
`compute/q7/`: $5^5 1^{18}$ at $k=1$ returned kissat UNSAT after 7575s, but
the trimmed DRAT is 3.9GB and was not stored; the independent check was
stopped at wrap. $5^2 1^{33}$ at $k=2$ and $3^{12}1^{7}$ at $k=5$ timed
out at sixty minutes. No new independently replayed certificate. This is
not a bound on $R(5,5)$.
