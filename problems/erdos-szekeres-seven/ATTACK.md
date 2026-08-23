# Attack log — erdos-szekeres-seven

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-23

### Backward plan, ranked by cheapest first check

1. **Audit the proposed 32-point construction.** Finished object: exact
   integer coordinates and a standalone verifier checking all triples for
   general position and all 7-subsets for non-convexity. It would prove
   ES(7) > 32, but is a dent only if that lower bound or witness is absent
   from the papers. Cheapest check: read the published lower-bound theorem
   and distinguish “no seven in convex position” from “no empty convex
   heptagon.” The latter does not imply the former.
2. **Replay one strictly smaller slice from arXiv:2512.24061.** Finished
   object: the paper's input instance, solver output, and an independent
   checker modeled on the ES(6) = 17 certificate pipeline. It beats the
   record only if the slice closes the last case required by the paper's
   reduction. Cheapest check: identify an explicitly named unresolved slice
   and its precise implication before writing an encoder.
3. **Test a symmetry-class obstruction at 33.** Finished object: a short
   exact certificate proving that one named order-type family at 33 always
   contains a convex 7-set. This is residue unless the families cover every
   case. Cheapest check: enumerate the relevant orbit representatives at a
   toy size and compare them with a direct convexity test.
4. **Encode a named finite family at 33 in SAT or oriented-matroid form.**
   Finished object: DIMACS, an UNSAT proof, and a checker, together with the
   exact map from satisfying assignments to uniform rank-3 chirotopes. A
   partial family exclusion is residue; a complete family elimination moves
   the upper bound. Cheapest check: validate chirotope axioms and convex-7
   clauses against exhaustive order types for a small n.
5. **Search beyond 32 points.** Finished object: exact coordinates for 33 or
   more points with no seven in convex position, plus two independent
   verifiers. This would raise a published lower bound of 33 if that remains
   the record. Cheapest check: compare against the universal lower-bound
   construction and run local mutations only after exact verification of
   the seed.
6. **Certificate-carrying allowable-sequence reduction.** Finished object:
   a finite list of allowable-sequence states, a transition table, and an
   independent dynamic-programming checker proving that every terminal
   state has a convex 7-set. If the state quotient is exhaustive, it could
   certify the 33-point upper bound; otherwise it is residue. Cheapest
   check: reproduce ES(6) at 17 with the same state definition and no
   geometry-specific exceptions.

The first check is the literature replay: it can kill item 1 as a new
result and determine whether item 5 is even logically available.
