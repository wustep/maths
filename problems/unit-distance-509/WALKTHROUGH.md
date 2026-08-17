# Walkthrough — shrinking the 509-vertex five-chromatic unit-distance graph

## 0. What was actually missing

The published record is a concrete point set, not a proof that 509 is minimal. A dent is any strictly smaller exact-coordinate unit-distance graph that is still not 4-colorable, or else a 4-coloring of the published 509-set (which would refute it). The missing degree of freedom was a vertex subset, or a swap against Parts’ own lattice, that preserved the 4-coloring obstruction.

Coordinates were not to be invented. The work starts only after the published `.vtx` file is in hand.

## 1. Named false starts

**Selector cores.** Cadical with a presence selector on every vertex, then `get_core`, sat for minutes without returning. The DRAT clause core of the ordinary 4-coloring CNF still mentioned all 509 vertices. Core extraction did not delete anything.

**Naive expansion-then-greedy-delete.** The graph is already not 4-colorable, so \(G\) plus extra lattice points reduces back to \(G\) by throwing the extras away. Adding vertices and deleting greedily cannot beat 509.

**Twelve highest-degree extras for one original.** Drop any one of the 24 lowest-degree originals and add the 12 unused lattice/ρ points of degree 9–10 into \(G\). All 24 instances were 4-colorable.

**One extra for two degree-4 originals, adjacency required.** No unused point of degree at least 6 is unit-adjacent to two distinct degree-4 vertices of \(G\). The job list was empty.

**Rebuilding the unit-distance graph on every SAT call.** Exact \(O(n^2)\) edge search is 2.5 seconds. A 3,000-call swap search is then hours. The working encoding reuses \(G\)’s edge list and only adds the extra’s exact neighbours.

## 2. The useful failure

Every single-vertex deletion of the published graph is 4-colorable. The SAT times are small (median 0.33s, max 6.7s). So \(G\) is vertex-critical: deletion alone cannot produce a smaller 5-chromatic subgraph.

That failure names the only remaining move. A smaller graph has to *swap*. Drop \(k\) originals, keep \(\ell\) extras from the published lattice, and finish with \(509-k+\ell<509\). The cheapest dent is \(k=2\), \(\ell=1\).

A second failure made the cost of a swap visible. Vertex 310, which is the lattice point \((0,\sqrt{3})\) and has degree 4, *can* be replaced, but only by several extras at once. Binary-chunk reduction of the 677-point reserve cut the extra set to 6 points. The resulting 514-vertex graph is itself vertex-critical. One original out, six extras in, is a different 5-chromatic unit-distance graph, not a smaller one.

## 3. The click

Two clicks, neither of them a dent.

The first was algebraic, not combinatorial. The published 509 file contains four nested radicals \(\sqrt{(5/2)(7\pm\sqrt{33})}\). They denest in \(\mathbb{Q}(\sqrt{3},\sqrt{5},\sqrt{11})\):

\[
\sqrt{\tfrac52(7+\sqrt{33})}=\frac{\sqrt{15}+\sqrt{55}}{2},\qquad
\sqrt{\tfrac52(7-\sqrt{33})}=\frac{\sqrt{55}-\sqrt{15}}{2}.
\]

Every published coordinate is then an 8-integer vector. Squared distance 1 is an exact equality, not a float tolerance. The rebuilt graph has 509 vertices and 2442 edges, matching Parts, with 374 unrotated points and 135 ρ-rotates (plus the shared origin).

The second click was that the lattice reserve is large enough to replace a vertex and too coarse to replace two cheap ones. \((G-v_{310})\cup R\) is unsatisfiable for the full 677-point reserve \(R\), so extras *can* carry the obstruction. But no single point of \(R\) makes \((G-\{v,w\})\cup\{e\}\) non-4-colorable for any pair of degree-4 vertices \(v,w\).

## 4. The argument, in the order it was found

Fetch `509_parts.vtx` from the Lean Hadwiger–Nelson repository, which cites the Polymath16 fifteenth thread as Parts’ source. Parse the Mathematica lines into \(\mathbb{Q}(\sqrt{3},\sqrt{5},\sqrt{11})\). Test every pair for squared distance exactly 1. Obtain 2442 edges, minimum degree 4, maximum 36 (the origin). Heule’s 510-file, fetched as a control, rebuilds to 2504 edges.

Encode 4-coloring with a triangle \((0,149,152)\) pinned. Cadical reports UNSAT in 2.5s. The DRAT proof is 132,579 lines. Heule’s `drat-trim`, compiled from upstream C, prints `s VERIFIED`. The published 509-graph is not 4-colorable. It is not a refutation.

Delete each vertex in turn. All 509 of the graphs \(G-v\) are 4-colorable. Store explicit colorings of the six degree-4 deletions. Independently check that \(G-310\) has no monochromatic unit edge.

Generate every legal lattice point \((a+b\sqrt{33}+ic\sqrt{3}+id\sqrt{11})/12\) of Euclidean radius at most 2.55, and every ρ-rotate. This disk covers the published 509. Of the unused points, 677 have exact unit-degree at least 4 into \(G\).

Test swaps, in this order:

- 12 best extras, drop one low-degree original: 24 SAT.
- All 677 extras, drop vertex 310: UNSAT. Reduce the extras by binary chunks to 6. The 514-vertex graph has 2478 exact unit edges and is vertex-critical (514/514 deletions SAT).
- One extra of degree at least 6, drop two degree-4 originals: 2,925 SAT.
- One extra of degree at least 4, drop two degree-4 originals: 10,155 SAT.
- One extra adjacent to both of a pair of degree-at-most-5 originals: 68 SAT.

No trial produced a 5-chromatic graph on fewer than 509 vertices.

## 5. Computer residue

| object | where | what it shows |
| --- | --- | --- |
| `compute/509_parts.vtx` | published coordinates | 509 points, not invented |
| `compute/verify_509.json` | exact rebuild | \(n=509\), \(m=2442\) |
| `compute/color509.cnf` + `color509.drat` | Cadical proof | 4-coloring UNSAT |
| `compute/drat-trim` | Heule’s checker | `s VERIFIED` |
| `compute/shrink_singles.jsonl` | 509 SAT calls | \(G\) is vertex-critical |
| `compute/coloring_Gminus_*.txt` | six 4-colorings | degree-4 vertices are necessary |
| `compute/candidates.json` | lattice reserve | 677 extras, max degree 10 |
| `compute/swap_v310_e6.vtx` | 514-point swap | 6 extras replace \((0,\sqrt{3})\) |
| `compute/shrink_514.jsonl` | 514 SAT calls | that swap graph is also critical |
| `compute/double_swap_deg4.jsonl` | 10,155 SAT calls | no 1-for-2 swap on degree-4 pairs |
| `compute/double_swap_d5adj.jsonl` | 68 SAT calls | no 1-for-2 swap of adjacent deg-≤5 pairs |
| `compute/search_summary.json` | totals | no dent |

Replay the certificate with `compute/run_verify.sh`.

## 6. Proven, and still open

What is proved here is finite and checkable:

- The fetched Parts coordinates determine a strict unit-distance graph with 509 vertices and 2442 edges in \(\mathbb{Q}(\sqrt{3},\sqrt{5},\sqrt{11})\).
- That graph is not 4-colorable. The claim is the CNF plus a `drat-trim`-verified DRAT proof, not an appeal to the paper.
- The graph is vertex-critical. Each \(G-v\) has an explicit or SAT-logged 4-coloring.
- No 1-for-2 swap of a degree-4 pair against the radius-2.55 lattice/ρ reserve produces a smaller 5-chromatic example.
- Replacing \((0,\sqrt{3})\) by six lattice extras yields a 514-vertex 5-chromatic unit-distance graph that is also vertex-critical. It does not beat 509.

What is not proved: that 509 is the global minimum. The reserve is one disk and one rotation. Pairs of degree 5 and higher were not exhaustively swapped. New vertices off this lattice were not considered, and were not allowed. The Hadwiger–Nelson number is still one of 5, 6, or 7. This search does not claim otherwise.

The published record remains 509 vertices.
