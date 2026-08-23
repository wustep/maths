# Research log — hadwiger-nelson-plane

Papers, OEIS, failed lookups. Cite every URL you opened, including the
ones that gave nothing. Forum numbers (MSE, Reddit, MathOverflow,
AlphaXiv) are leads, not citations. Append a stub with
`python3 scripts/arxiv_fetch.py <id> --research problems/hadwiger-nelson-plane/RESEARCH.md`
or look up a sequence with `python3 scripts/oeis_lookup.py`.

## 2026-08-23

- [de Grey, *The chromatic number of the plane is at least 5*,
  arXiv:1804.02385v3](https://arxiv.org/abs/1804.02385) (30 May
  2018) — Section 5 constructs the 1,581-vertex unit-distance graph
  $G$ and reports independent standard-SAT checks that its chromatic number is
  five.  Figure 9 calls it a 1,581-vertex non-4-colorable graph.  Earlier in
  the paper the first construction has 20,425 vertices.  These are different
  graphs, so the two counts must not be conflated.
- [Parts, *Graph minimization, focusing on the example of 5-chromatic
  unit-distance graphs in the plane*, arXiv:2010.12665v2](https://arxiv.org/abs/2010.12665)
  (28 June 2022) — Section 6, Table 1 gives the M6A graph with 509
  vertices and 2,442 edges.  The text decomposes it into a 374-vertex large
  subgraph and a 136-vertex small subgraph sharing one vertex.  An exact
  rebuild in this checkout independently found 509 distinct vertices, 2,442
  unit edges, a $374+135$ field split, and no floating-point near-unit pair
  rejected by exact arithmetic.
- [Heule, *Computing Small Unit-Distance Graphs with Chromatic Number 5*,
  arXiv:1805.12181v1](https://arxiv.org/abs/1805.12181) (30 May
  2018) — Sections 3.1 and 4.3 describe the coloring CNF, DRAT
  unsatisfiable-core method, and several 553-vertex five-chromatic graphs.
  The paper's 553 count is not the later 509 record.
- [Parts, *The chromatic number of the plane is at least 5: a
  human-verifiable proof*, arXiv:2010.12661v1](https://arxiv.org/abs/2010.12661)
  (23 October 2020) — gives a manual finite forcing proof of the already
  known lower bound five.  It supplies gadget ideas but claims no lower bound
  six.
- [Sokolov–Voronov, *On the chromatic number of the plane for map-type
  colorings*, arXiv:2502.01958v1](https://arxiv.org/abs/2502.01958)
  (4 February 2025) — the introduction states the classical interval
  $5\leq\chi(\mathbb R^2)\leq7$.  Theorem 2 proves that a proper polygonal
  coloring of the whole plane needs seven colors.  Thus the proposed
  six-color named-tiling shape is impossible for polygonal tilings; a surviving
  candidate would need genuinely non-polygonal boundaries outside that
  theorem.
- [MathWorld, *Hadwiger–Nelson Problem*](https://mathworld.wolfram.com/Hadwiger-NelsonProblem.html)
  — current secondary screen, opened 23 August 2026.  It says that the Parts
  509 remains the smallest known planar five-chromatic unit-distance graph and
  that no planar unit-distance graph with chromatic number above five is
  known.  This is a current survey check, not the paper of record.
- [Soifer, *Chromatic Number of the Plane: The Problem*, in *The New
  Mathematical Coloring Book*](https://ideas.repec.org/h/spr/sprchp/978-1-0716-3597-1_2.html)
  (2024) — current survey chapter metadata and DOI were accessible, but the
  full chapter was not.  Its abstract says the problem remains open after 73
  years; it exposes no finite-graph count, so no number here is based on it.
- [Bogomolny, *Chromatic Number of the Plane*](https://www.cut-the-knot.org/proofs/ChromaticNumber.shtml)
  — secondary screen.  It names Parts 509 as the smallest known
  five-chromatic graph but still displays the stale theorem
  $4\leq\chi\leq7$ before mentioning de Grey.  It is not used for the
  baseline.
- [Kürtösi–Pach, *Note on the chromatic number of Minkowski
  planes*](https://cs.bme.hu/jh2023/kotet23.pdf) — failed lookup: the browser
  returned HTTP 502 and command-line TLS verification failed.  A search
  excerpt mentioned 509, but that excerpt is not treated as a citation.
- [Frankl–Hubai–Pálvölgyi, *Almost-Monochromatic Sets and the Chromatic
  Number of the Plane*](https://link.springer.com/article/10.1007/s00454-023-00526-9)
  (Discrete & Computational Geometry, 2023) — the peer-reviewed introduction
  states de Grey's lower bound five and Isbell's upper bound seven, and gives
  the corrected 1,581 count. It does not claim a lower bound six.
- [Heule, *Trimming Graphs Using Clausal Proof Optimization*,
  arXiv:1907.00929v2](https://arxiv.org/abs/1907.00929) — reports the
  intermediate 529-vertex, 2,670-edge five-chromatic graph and the clausal
  proof-optimization method. This is not the current 509 record.
- [Parts, *What percent of the plane can be properly 5- and 6-colored?*,
  arXiv:2010.12668v1](https://arxiv.org/abs/2010.12668) — Section 2.4 and
  Figure 4 give Pritikin–Pegg, honeycomb, and curved Reuleaux-separator
  seven-color patterns. In 2020 a proper six-color tiling remained open. The
  same paper gives a partial six-coloring covering more than 99.985698% of the
  plane and proves that every planar unit-distance graph on at most 6,992
  vertices is six-colorable. The construction coordinates are numerical, not
  an exact certificate. [Journal DOI](https://doi.org/10.1016/j.disc.2022.112954).
- [Manta, *On the chromatic number of the plane*,
  arXiv:1909.02708](https://arxiv.org/abs/1909.02708) — Theorems 2.2 and 2.3
  are earlier seven-color lower bounds for restricted polygonal/triangular
  colorings. Sokolov–Voronov now gives the broader polygonal obstruction used
  here.
- [Voronov–Neopryatnaya–Dergachev, *Constructing 5-chromatic unit distance
  graphs embedded in the Euclidean plane and two-dimensional spheres*,
  arXiv:2106.11824v4](https://arxiv.org/abs/2106.11824) — Sections 5–8 build
  fourteen 64,513-vertex five-chromatic, Moser-spindle-free planar graphs.
  Proposition 5 places the coordinates in
  $\mathbb Q(i,\sqrt2,\sqrt3,\sqrt5)$; the published cases are explicitly
  five-colorable, so they are seeds rather than a new lower bound. The
  [authors' data and Sage code](https://github.com/vsvor/dist-graphs) were
  opened, but no 5-coloring UNSAT proof for a larger spawn was present.
  [Journal DOI](https://doi.org/10.1016/j.disc.2022.113106).
- [Haugland, *A Moser-spindle-free 5-chromatic unit distance graph on 2131
  vertices in the plane*, arXiv:2608.04542v4](https://arxiv.org/abs/2608.04542v4)
  (17 August 2026) — the introduction calls Parts 509 the current order
  record. Sections 2–3 construct an unrelated seven-fold heptagon/heptagram
  path lattice and a 2,131-vertex, 12,530-edge five-chromatic graph. Lemma 2.2
  relies on a double-precision exhaustive separation check, and the reported
  SAT results have no attached proof artifact; exact replay is therefore a
  prerequisite, not an established local baseline. The current
  [MathWorld Haugland graphs page](https://mathworld.wolfram.com/HauglandGraphs.html)
  was also opened as a secondary screen.
- Fetching arXiv:2010.12668, 2106.11824, and 2608.04542 through
  `scripts/arxiv_fetch.py` hit HTTP 429 at the arXiv API. Their arXiv abstract,
  HTML/PDF, version histories, and journal/code links above were opened
  directly instead.
