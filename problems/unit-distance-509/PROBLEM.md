# Shrink the 509-vertex five-chromatic unit-distance graph

- Slug: `unit-distance-509`
- List: P29
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort max`
- Status: open
- Area: Computational discrete geometry
- Sources: Parts arXiv:2010.12665; Voronov et al. Discrete Math. 2022
- Started: 2026-08-17

## Statement

The smallest published planar five-chromatic unit-distance graph has 509 vertices. Minimality is unknown. Any strictly smaller exact-coordinate 5-chromatic unit-distance graph is a new bound.

## Tonight

Start from a published 509-vertex exact-coordinate graph. Alternate SAT unsat-core extraction and vertex deletion. Emit a smaller exact-coordinate 5-chromatic subgraph, a 4-coloring-UNSAT certificate, and a unit-distance checker.

A 4-coloring of the 509-graph would refute the published claim (a stronger improvement). Do not invent coordinates. Do not claim Hadwiger-Nelson is 5 or 6.

## Tonight's incomplete search (2026-08-17)

The published 509-graph was fetched, rebuilt with exact arithmetic (2442 edges), and shown not 4-colorable by a `drat-trim`-verified proof. It is vertex-critical. Swaps against Parts' own lattice did not produce a strictly smaller 5-chromatic example. Details: `ATTACK.md`, `WALKTHROUGH.md`, `compute/search_summary.json`. Replay: `compute/run_verify.sh`.
