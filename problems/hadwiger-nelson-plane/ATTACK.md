# Attack log — hadwiger-nelson-plane

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-23

### Backwards map from a changed bound

The published interval must be established from the papers before any item
below can be called a result.  These are candidate finished objects, written
backwards from what a stranger would replay.

1. **Spawn from a published five-chromatic graph.**  Start with an exact
   de Grey, Heule, or Parts coordinate set, add exact unit-distance orbit
   points (and delete redundant old points), and ask SAT for a 5-coloring.
   The finished object is a coordinate file, its complete unit-distance edge
   list, a 5-coloring CNF, an UNSAT proof, and two independent verifiers.  A
   non-5-colorable finite unit-distance graph is 6-chromatic or worse and
   would prove $\chi(\mathbb R^2)\ge 6$.  Cheapest check: rebuild every unit
   edge exactly and run the 5-color SAT instance before doing any reduction.

2. **Exact Golomb or mosaic gadget.**  Compose small color-forcing gadgets at
   shared vertices using coordinates in a named algebraic number field.  The
   finished object is the exact coordinate list plus a machine-readable
   decomposition into gadgets, a complete pairwise unit-distance check, and
   a 5-coloring UNSAT certificate.  This would give the same lower-bound
   improvement without depending on a large published graph.  Cheapest
   check: enumerate squared distances in the exact field, then solve only the
   gadget boundary-color table; a surviving boundary assignment kills the
   composition before full SAT.

3. **Six colors for a named mosaic now documented only with seven.**  First
   identify a published named tiling or finite mosaic whose stated best
   coloring is still seven.  The finished object is a finite fundamental
   domain, translation rules, a six-color table, and a checker covering every
   unit-distance adjacency including wraparound.  It improves that named
   finite benchmark, even though it does not by itself change the global
   interval $5\le\chi(\mathbb R^2)\le7$.  Cheapest check: test the published
   seven-color cell complex against the proposed period and all boundary
   translates.  If the literature already gives six colors, this shape dies.

4. **Finite list-coloring amplifier.**  Replace every vertex of a small
   non-5-list-colorable template by an exact planar unit-distance equality or
   inequality gadget.  The finished object is the template, a coordinate
   embedding of every gadget with identified terminals, and a DRAT-checked
   5-coloring UNSAT instance.  It would be a finite 6-chromatic unit-distance
   graph and hence prove $\chi(\mathbb R^2)\ge6$.  Cheapest check: enumerate
   each gadget's terminal color relation independently; reject the design if
   any unintended terminal pattern remains.

5. **Symmetry-constrained algebraic orbit search.**  Choose a small exact
   unit-distance seed and close selected points under a finite dihedral group,
   solving the remaining unit equations in a fixed number field.  The
   finished object is an orbit recipe, expanded exact coordinates, and a
   5-coloring UNSAT proof whose symmetry assumptions are not used by the
   verifier.  It would again prove the lower bound six.  Cheapest check:
   quotient the 5-color SAT instance by the geometric automorphisms for the
   search, then replay the unquotiented instance for any hit.

6. **A patch of one triangular lattice.**  This dies immediately: coloring a
   lattice point $(a,b)$ by $a-b\pmod 3$ properly colors every unit edge of
   the triangular lattice.  Every finite subgraph is therefore 3-colorable,
   so no choice of patch from one such lattice can be the requested
   6-chromatic certificate.  Rotated or translated layers are essential; a
   larger one-layer search would only spend compute on an elementary
   obstruction.

### Published-record screen

- De Grey's final arXiv version is v3, not v1: the graph in Section 5 has
  1,581 vertices and chromatic number five. Parts' v2 Section 6, Table 1 gives
  the later 509-vertex, 2,442-edge graph. The latter counts were independently
  rebuilt from the published coordinates with exact field arithmetic.
  Haugland's 17 August 2026 paper still calls 509 the current order record.
  None of these is 6-chromatic.
- The interval remains $5\leq\chi(\mathbb R^2)\leq7$. A 2023 peer-reviewed
  introduction states both bounds, and the 2025 Sokolov–Voronov paper states
  the same interval before treating map-type colorings.
- Shape 3 is killed for polygonal tilings. Sokolov–Voronov Theorem 2 proves
  that there is no proper polygonal six-coloring of the plane. Parts'
  Pritikin–Pegg and honeycomb mosaics are therefore not six-color targets. No
  paper-backed named finite toroidal mosaic benchmark was found. A finite
  patch with no documented comparison would not move a record.
- Shape 2 has a concrete exact family: Voronov–Neopryatnaya–Dergachev build
  64,513-vertex, five-chromatic, Moser-spindle-free graphs from a rigid
  algebraic generator set. A larger-depth spawn would require exact
  coordinates, a complete unit-edge rebuild, 5-coloring UNSAT proof, and an
  explicit 6-coloring; their published five-chromatic cases are only seeds.
- Shape 5 has a genuinely different seed in Haugland's 21-vertex,
  seven-fold-symmetric heptagon/heptagram graph. The paper builds a
  2,131-vertex five-chromatic graph from path-lattice arcs. A retained
  campaign must output an exact cyclotomic coordinate expansion, complete
  edge list, 5-coloring proof, and 6-coloring. The paper uses double-precision
  exhaustive deduplication in one lemma and reports SAT outcomes without a
  proof artifact, so those steps must be independently exactified before any
  number is trusted.

### q1: exact Parts spawns — residue

- Rebuilt the Parts graph from 509 exact coordinates and recovered all 2,442
  unit edges. The first spawn is $G\cup\rho G$ for Parts' rotation
  $\rho=(7+i\sqrt{15})/8$. Deduplication gives 933 vertices and exact
  all-pairs rebuilding gives 4,651 unit edges.
- CaDiCaL found a proper 5-coloring of the 933-vertex spawn in 0.015 seconds.
  The committed color classes have sizes 211, 203, 203, 165, 151.
- The second spawn adds all 677 exact points retained by the earlier
  radius-2.55 lattice/reserve enumeration. This process did not rerun the
  larger universe enumeration: that attempt exceeded the shared process
  memory after emitting the first spawn. It instead copies the finite source
  table, reconstructs every coordinate exactly, and independently checks that
  each added point lies in the disk and has at least four exact unit neighbors
  in $G$.
- The reserve union has 1,186 vertices and 7,440 exact unit edges. CaDiCaL
  found a proper 5-coloring in 2.89 seconds, with class sizes 259, 251, 225,
  220, 231. Exact Python rebuilding and a separate C edge/color checker both
  replay the two stored colorings.
- This is residue, not a lower bound: the coloring of the full reserve
  union restricts to a coloring of $G\cup S$ for every subset $S$ of the 677
  added vertices. Thus none of those $2^{677}$ add-only spawns is
  6-chromatic. Searches that delete base vertices or introduce coordinates
  outside this reserve remain open.

### q2: a third exact rotation layer — residue

- Built $G\cup\rho G\cup\rho^2G$ with the same exact field arithmetic. The
  three layers contribute 509, 424, and 424 new vertices after deduplication,
  for 1,357 vertices total. Exact all-pairs rebuilding finds 6,860 unit edges.
- CaDiCaL found a proper 5-coloring in 0.025 seconds. Its class sizes are 298,
  296, 278, 254, 231. A second exact rebuild and the C edge/color checker both
  accept the committed model.
- The model restricts to every add-only subgraph of the 848 points supplied
  by $\rho G\cup\rho^2G$, excluding all $2^{848}$ subsets as 6-chromatic
  witnesses. It does not cover combinations with q1's 677-point reserve,
  deletions from $G$, or a fourth rotation layer.

### q3: combine both exact Parts spawns — residue

- Merged the full 677-point reserve with
  $G\cup\rho G\cup\rho^2G$. Twenty-four reserve points already occur in a
  rotated layer, leaving 1,501 distinct non-base vertices and 2,010 vertices
  in the combined graph.
- The two previously replayed induced graphs supply their internal edges.
  An exact check of all $653\times824$ pairs between the disjoint added parts
  finds 50 further unit edges, for 11,766 edges total. The verifier repeats
  this decomposition after q1 and q2 independently rebuild the pieces.
- CaDiCaL found a proper 5-coloring in 0.18 seconds, with class sizes 405,
  386, 407, 403, 409. Exact Python verification and the independent C
  edge/color checker both accept it.
- This model subsumes the earlier add-only exclusions: every graph formed by
  adjoining any subset of these 1,501 exact points to Parts 509 is
  5-colorable. None of the $2^{1501}$ graphs is a 6-chromatic witness. The
  residue leaves base-vertex deletion, a fourth rotation, points beyond the
  retained reserve, and other algebraic families open.

### q4: fourth exact Parts rotation layer — residue

- Adjoined $\rho^3G$ to q3's combined reserve and three-layer graph. Of the
  509 rotated source vertices, 85 already occur in q3 and 424 are new. The
  resulting exact graph has 2,434 vertices.
- Retained q3's independently replayed induced edge set and compared every
  new vertex with every earlier vertex in exact field arithmetic. This finds
  2,209 edges incident to the extension and 13,975 unit edges in total.
- CaDiCaL found a proper 5-coloring in 1.13 seconds, with class sizes 553,
  430, 449, 522, 480. The parent replay verifies q1–q3, a separate q4 Python
  program reconstructs the exact extension, and the C edge/color checker
  accepts the stored model.
- The same model closes base-vertex deletion for this fixed family. Deleting
  any subset of the 509 Parts vertices while retaining any subset of the
  1,925 reserve/rotation vertices produces a subgraph of the verified q4
  graph and is therefore 5-colorable. A deletion-and-replacement construction
  using coordinates outside this union is not covered.
- This is residue, not a lower bound. The record remains
  $5\leq\chi(\mathbb R^2)\leq7$; fifth and later rotation layers, a larger
  exact reserve, and different algebraic families remain open.
