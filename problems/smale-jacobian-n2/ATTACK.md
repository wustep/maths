# Attack log — Smale 16 / plane Jacobian conjecture

Chronological attempts, newest last. A finite search changes the record only
when its scope and certificate are both complete.

## 2026-08-27 — research before search

- Replayed the classical reductions and the current finite-degree literature.
  Moh's old boundary is 100; Nguyen gives 104; Guccione–Guccione–Horruitiner–
  Valqui prove that below 125 only \((72,108)\), up to transposition, survives.
- Chased a forum lead to Helali's immutable Git/Zenodo archive instead of
  trusting the forum number. A clean exact replay passed. Direct comparison
  with Theorem 2.1 and Proposition 4.3 confirmed the degree implication, both
  polygon pairs, the Laurent coordinate change, and the normalization.
- Kept the 2026 three-variable announcement separate. It is not community
  consensus, and neither accepting nor rejecting it changes the plane problem.

## 2026-08-27 — ten imagined end-states

The certificate was imagined first in each case; “die” names the earliest
check that would make the route unfit for a bound.

1. **Exclude the \((72,108)\) pair exactly.** Certificate: unit-ideal
   identities for both Proposition 4.3 systems plus an independently checked
   bridge to Theorem 2.1. It might work because the systems are finite; it dies
   if a polygon, branch, or normalization was omitted.
2. **Classify all homogeneous plane Keller perturbations.** Certificate: a
   coefficient theorem reducing \(F=I+H_d\) to a shear and a sparse exact
   inverse checker. It might work because the two homogeneous pieces of the
   determinant have different degrees; it dies as a record attack because
   this family is classical and contains no counterexample.
3. **Obstruct the tangent-sweep mechanism in the plane.** Certificate: a
   formal determinant identity for every polynomial parametrized curve,
   checked independently on generic coefficient arrays. It might work because
   a raw two-dimensional sweep has no spare coordinate; it dies as a full
   obstruction if a twisted or non-tangent construction evades the template.
4. **Re-enumerate every sub-125 degree pair from numerical semigroup data.**
   Certificate: a second program reproducing Theorem 2.1's unique exception.
   It might catch a missing degree pair; it dies if the paper's geometric
   admissibility tests cannot be reconstructed without importing its proof.
5. **Make the 89 MB hard identity compact.** Certificate: a deterministic
   modular seed plus rational reconstruction yielding the same exact
   multiplier vector. It might make review easier; it dies if reconstruction
   still needs essentially the full 1,925-coordinate solution.
6. **Classify cubic plane Keller maps coefficient by coefficient.**
   Certificate: a Gröbner basis and inverse for every component. It is finite;
   it dies as a dent because the degree lies far below the published record.
7. **Classify sparse Keller maps at maximum degree 125.** Certificate: a
   support-complete list and unit ideals for every non-automorphic support. It
   might reach the new frontier; it dies unless the support restriction follows
   from a published reduction.
8. **Bound the Bass–Connell–Wright inverse tree expansion.** Certificate: a
   vanishing theorem for all rooted-tree terms beyond an explicit index. It
   would prove polynomial invertibility in a reduced class; it dies when
   nilpotence cancels only sums of trees rather than individual trees.
9. **Turn one Magnus inner-polygon conjecture into a finite obstruction.**
   Certificate: exact inequalities eliminating every lattice vertex outside
   Lee–Li's proved region. It might narrow approximate roots; it dies while the
   remaining conjectural step is still equivalent to the original problem.
10. **Formalize the degree-125 bridge in Lean.** Certificate: a theorem from
    the two unit-ideal hypotheses to the degree inequality. It might remove
    prose ambiguity; it dies as the first move because importing the 89 MB
    algebraic-number-field certificate is the hard part.

## 2026-08-27 — selection and pruning

- Picked 1: it is the only route that can immediately improve the documented
  finite record, and an exact certificate already exists to be replayed.
- Picked 2: it gives an all-degree positive control family and a small exact
  inverse certificate, useful for testing every local algebra convention.
- Picked 3: it directly probes the new higher-dimensional mechanism while
  making a universal, finite, checkable statement in two variables.
- Pruned 4 and 5 because they duplicate the expensive parts of the two sources
  without strengthening the implication. Pruned 6 because degree 3 is already
  classical. Pruned 7 because sparsity is not justified. Pruned 8 and 9 at
  their still-conjectural steps. Deferred 10 until the external exact identity
  has a practical formal representation.

