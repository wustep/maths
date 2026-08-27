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
