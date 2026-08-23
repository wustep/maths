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
