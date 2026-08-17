# Research log — Shrink the 509-vertex five-chromatic unit-distance graph

## 2026-08-17 — published record

- [Parts, *Graph minimization…*, arXiv:2010.12665](https://arxiv.org/abs/2010.12665) — 509 vertices, 2442 edges, type M6A, \(G=L_{374}\cup\rho S_{136}\). Vertex lists promised on the Polymath site. Minimization by expansion/reduction with SAT hyperedges.
- [Voronov–Neopryatnaya–Dergachev, *Constructing 5-chromatic unit distance graphs…*, Discrete Math. 2022 / arXiv:2106.11824](https://arxiv.org/abs/2106.11824) — cites 509 as the planar record after Heule’s 553 and 517.
- [MathWorld, Parts Graphs](https://mathworld.wolfram.com/PartsGraphs.html) — table: 509 vertices, 2442 edges, prior to 2020-03-07. Implemented as `GraphData["PartsGraph509"]`.
- [MathWorld, de Grey Graphs](https://mathworld.wolfram.com/deGreyGraphs.html) — as of August 2026, “the smallest of these remains the 509-vertex Parts graph (Parts 2020a, Haugland 2026)”.
- [Heule, *Computing Small Unit-Distance Graphs with Chromatic Number 5*, arXiv:1805.12181](https://arxiv.org/abs/1805.12181) — 553-vertex graphs; later 529, 517, 510. Method: DRAT-trim unsat cores.
- [marijnheule/CNP-SAT](https://github.com/marijnheule/CNP-SAT) — `vtx/510.vtx` and a Singular exact-distance checker `check/check_dist_one.py`. The 510-file has 2504 edges (MathWorld HeuleGraph510).
- [vasnesterov/HadwigerNelson](https://github.com/vasnesterov/HadwigerNelson) — Lean 4 formalization of the 510-graph. Stores `vtx/509_parts.vtx` (from the [Polymath16 fifteenth thread](https://dustingmixon.wordpress.com/2019/12/12/polymath16-fifteenth-thread-writing-the-paper-and-chasing-down-loose-ends/)) and `vtx/510_heule.vtx`. Notes that 509 contains nested radicals `Sqrt[(5*(7+Sqrt[33]))/2]`, which block their current `build_edge` tactic.
- [Polymath16 wiki](https://michaelnielsen.org/polymath1/index.php?title=Hadwiger-Nelson_problem) — project page; older tables still list 510 in places.
- No later published planar 5-chromatic unit-distance graph smaller than 509 was found in this screen. Haugland 2026 is a 2131-vertex *Moser-spindle-free* example, not a smaller unrestricted one.

## 2026-08-17 — files fetched

- `https://raw.githubusercontent.com/vasnesterov/HadwigerNelson/master/vtx/509_parts.vtx` — 509 coordinate pairs.
- `https://raw.githubusercontent.com/vasnesterov/HadwigerNelson/master/vtx/510_heule.vtx` — same 510-set as CNP-SAT `vtx/510.vtx`.
- `https://raw.githubusercontent.com/marijnheule/CNP-SAT/master/check/check_dist_one.py` — float-to-Singular rewrite, used only as a method reference. Our checker is exact in the degree-8 field and does not call Singular.
- `https://raw.githubusercontent.com/marijnheule/drat-trim/master/drat-trim.c` — compiled locally to `compute/drat-trim`.

## 2026-08-17 — independent checks (this folder)

- Exact rebuild of Parts 509: 509 vertices, 2442 edges, 0 float-near-unit false pairs. Split 374 + 135 matches \(L_{374}\cup\rho S_{136}\) with shared origin.
- Exact rebuild of Heule 510: 510 vertices, 2504 edges.
- 4-coloring of 509: UNSAT, DRAT verified by `drat-trim`.
- Vertex-criticality of 509: 509/509 of \(G-v\) SAT. Six explicit colorings for the degree-4 vertices.
- Lattice disk \(r\le 2.55\) covers all 509 published points. 677 unused points of unit-degree ≥ 4.
- Vertex 310 \(=(0,\sqrt{3})\) is replaceable by 6 lattice extras; the 514-vertex graph is 5-chromatic and vertex-critical.
- 10,155 one-extra / two-degree-4-vertex trials: 0 UNSAT. 2,925 trials restricted to extras of degree ≥ 6: 0 UNSAT. 68 trials of extras adjacent to two vertices of degree ≤ 5: 0 UNSAT.

No smaller 5-chromatic exact-coordinate unit-distance graph was produced. The published record used here is still 509.
