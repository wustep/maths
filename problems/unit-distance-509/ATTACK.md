# Attack log — Shrink the 509-vertex five-chromatic unit-distance graph

## 2026-08-17 — start

- Target: a strictly smaller exact-coordinate 5-chromatic unit-distance graph than Parts 509, with a 4-coloring-UNSAT certificate and a unit-distance checker. Or a 4-coloring of the published 509-graph (would refute it).
- Published record still 509 as of MathWorld / de Grey Graphs page (August 2026): "the smallest of these remains the 509-vertex Parts graph (Parts 2020a, Haugland 2026)".
- Do not invent coordinates. Do not claim Hadwiger–Nelson is 5 or 6.

## 2026-08-17 — fetch published graph

- Parts arXiv:2010.12665: 509 vertices, 2442 edges, type M6A, $G = L_{374} \cup \rho S_{136}$. Coordinates live in $\mathbb{Q}[\sqrt{3},\sqrt{11}]$ after embedding the hexagonal lattice, plus a rotation $\rho = \exp(i\arccos(7/8))$ of the small subgraph. Vertex lists promised on the Polymath site.
- Lean formalization [vasnesterov/HadwigerNelson](https://github.com/vasnesterov/HadwigerNelson) stores `vtx/509_parts.vtx` sourced from the Polymath16 fifteenth thread, and `vtx/510_heule.vtx` from [marijnheule/CNP-SAT](https://github.com/marijnheule/CNP-SAT).
- Downloading both into `compute/`.
- `509_parts.vtx`: 509 unique Mathematica coordinate pairs, no trailing newline. Radicals used: `√3, √5, √11, √15, √33, √55, √165, √(11/3)`, plus two nested forms `√((5/2)(7±√33))`.
- Those nested radicals denest in the same field:
  - `√((5/2)(7+√33)) = (√15+√55)/2`
  - `√((5/2)(7−√33)) = (√55−√15)/2`
- Field: $\mathbb{Q}(\sqrt{3},\sqrt{5},\sqrt{11})$, degree 8. Implemented as 8-integer coefficient vectors in `compute/udg.py`. No invented coordinates.
- Heule `510.vtx` from CNP-SAT and the Lean-repo `510_heule.vtx` are the same 510-point set.

## 2026-08-17 — exact unit-distance rebuild

- `verify_graph.py` parses the published `.vtx` and tests every pair for squared distance exactly 1.
- Parts 509: **n=509, m=2442**. Matches arXiv:2010.12665 (509 vertices, 2442 edges). 0 float-near-unit pairs that fail the exact test.
- Split: 374 vertices in $\mathbb{Q}(\sqrt{3},\sqrt{11})$ (no √5) and 135 with a √5 factor. That is exactly $L_{374}\cup\rho S_{136}$ with the origin shared: $374+136-1=509$.
- Heule 510: **n=510, m=2504**. Matches MathWorld `HeuleGraph510` (2504 edges, 2019-08-08). Split 375 + 135.
- Degree range on 509: min 4, max 36 (the origin). Six degree-4 vertices.

## 2026-08-17 — 4-coloring UNSAT of the published 509

- Encoding: 4 colors, at-least-one color per vertex, different colors on each unit edge, triangle `(0, 149, 152)` pinned to colors 0,1,2. 2036 vars, 10280 clauses.
- Cadical 1.9.5: **UNSAT in 2.46s**. The published 509-graph is not 4-colorable, so it is not a refutation.
- DRAT proof `color509.drat` (132579 lines). `drat-trim` (compiled from Heule's upstream `drat-trim.c`): **s VERIFIED** in 2.17s. Clause core 9170/10280. All 509 vertices still appear in the clause core (no free vertex deletion from the proof core alone).

## 2026-08-17 — 509 is vertex-critical

- Exhaustive single-vertex deletion, Cadical, 4 workers, 90s wall: **509/509 of the graphs `G-v` are 4-colorable**. Tally in `shrink_singles.jsonl`. SAT times 0.01–6.7s (median 0.33s).
- Deletion alone cannot produce a smaller 5-chromatic subgraph. The published 509-graph is vertex-critical under an independently rebuilt unit-distance graph.
- Selector-based `get_core` was too slow to be useful; the exhaustive SAT scan is the certificate of criticality.

## 2026-08-17 — lattice reserve and swaps

- Every 509 vertex is an exact unrotated lattice point `(a+b√33+ic√3+id√11)/12` or a ρ-rotate of one. Disk r≤2.55 covers all 509. About 156k unused lattice/ρ points in that disk.
- 677 unused points have exact unit-degree ≥ 4 into G; max degree 10 (`candidates.json`).
- Adding the 12 highest-degree extras and dropping one low-degree original: 24/24 SAT (`expand_reduce.jsonl`). Those extras do not replace the cheapest originals.
- `(G-v) ∪ {all 677 extras}` is the stronger one-vertex swap: more extras can only add constraints.

## 2026-08-17 — one vertex is replaceable, but only by six extras

- `(G - v_{310}) ∪ {all 677 extras}` is UNSAT (n=1185, m=7426, 7.9s). Vertex 310 is the lattice point `(0, √3)`, degree 4.
- Binary-chunk reduction of the extra set: 677 → 6 extras, all unrotated lattice points. Log `swap_reduce.jsonl`. Result `swap_v310_e6.vtx`: n=514, m=2478, exact rebuild, 0 near-misses.
- 514-graph is also vertex-critical: 514/514 deletions SAT (`shrink_514.jsonl`). So this is an alternative 5-chromatic unit-distance graph, not a smaller one.
- 12-extra / one-original swaps: 24/24 SAT (`expand_reduce.jsonl`). Those 12 high-degree extras cannot replace any of the 24 cheapest originals by themselves.

## 2026-08-17 — 1-for-2 swaps against the reserve

A strict dent needs $509 - k + \ell < 509$. Cheapest: drop two originals, keep one extra.

- Degree ≥ 6 extras × all 15 degree-4 pairs: **2925 SAT, 0 hits** (`double_swap_noadj.jsonl`).
- All 677 extras of degree ≥ 4 × those 15 pairs: **10155 SAT, 0 hits** (`double_swap_deg4.jsonl`).
- Require-adj on two degree-4 vertices: empty job list (no extra of degree ≥ 6 touches two degree-4 vertices).
- Require-adj on two vertices of degree at most 5, extras of degree ≥ 4: **68 SAT, 0 hits** (`double_swap_d5adj.jsonl`). Only 68 extras even touch two such vertices.

No dent. The published record is still 509.

## 2026-08-17 — certificates written

- Unit-distance checker: `verify_graph.py` (exact field arithmetic).
- 4-coloring UNSAT: `color509.cnf` + `color509.drat`; `check_certificate.py` rebuilds both from the `.vtx` and runs `drat-trim`. Replay: `run_verify.sh`.
- Vertex-criticality witnesses: `coloring_Gminus_{310,313,316,319,322,325}.txt` plus `check_gv_coloring.py`.
- Totals: `search_summary.json`.


