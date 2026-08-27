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

## 2026-08-27 — q1: exceptional pair, executed backwards

- Imagined certificate: two exact unit-ideal identities; an exhaustive split
  for Case 1; a hash-bound artifact; and a small verifier connecting its
  variables to Proposition 4.3 and Theorem 2.1.
- First contradiction check: compared the source polygons rather than the
  archive's prose. They agree vertex for vertex. Independent lattice
  enumeration gives \((61,125)\) points in Case 1 and \((25,47)\) in Case 2.
- Checked the coordinate change \(t=xy^2\), \(z=y^{-1}\). Python and Rust both
  derive \([t,z]=-1\), \(x^2=t^2z^4\), and the same five coefficient
  identities. They also give determinant 14 for the three-vertex
  normalization matrix, so no forbidden division by a variable coefficient is
  hidden there.
- Bound the large certificate to commit
  `c530fe44e5f53b17840110931803e7c7c5a24cde` and archive SHA-256
  `232204bdb598cc2ea0368e154c8573e18bbfdc69fa631c8878de4b884b38bb18`.
  Eight central internal hashes also matched.
- Ran the entire archive in a fresh Python 3.14 environment. All serialized
  certificates passed. The separate `gmpy2` evaluation checked 13,410
  number-field products, equivalent to 335,250 scalar products. Both hard
  branch identities and the branch involution passed.
- Result: dent. The exact computation makes both Proposition 4.3 systems
  inconsistent. Combined with Theorem 2.1, every hypothetical plane
  counterexample satisfies

  $$
  \max\{\deg P,\deg Q\}\ge125.
  $$

  This is a finite degree improvement, not a proof of the plane Jacobian
  conjecture. As with any computer-assisted result built on a published
  reduction, specialist review of that reduction remains welcome.

## 2026-08-27 — q2: homogeneous perturbations

- Started with the inverse certificate. For a linear form \(l=ax+by\), the
  maps

  $$
  F=(x+cb l^d,\ y-ca l^d),
  \qquad
  F^{-1}=(x-cb l^d,\ y+ca l^d)
  $$

  preserve \(l\), which makes both compositions and the determinant immediate.
- Worked backwards from a general homogeneous perturbation \(I+H_d\).
  Homogeneous degree separation forces both the divergence and \(\det JH_d\)
  to vanish. The first makes \(H_d\) Hamiltonian; the second gives a binary
  form with zero Hessian. The binary Hessian lemma makes that form a power of
  one linear form, recovering exactly the displayed family.
- The exact sparse verifier passed at degrees 2, 3, 7, and 125. The last case
  is a useful high-degree sign and overflow check, but the classification is
  classical and gives no finite-record improvement. Dropped as a bound route.

## 2026-08-27 — q3: raw tangent sweeps

- Imagined obstruction: the determinant of every raw tangent sweep in the
  plane has a visible parameter factor.
- For \(S(w,\gamma)=K(w)+\gamma K'(w)\), its Jacobian columns are
  \(K'+\gamma K''\) and \(K'\). Exact expansion gives

  $$
  \det JS=\gamma\det(K'',K').
  $$

- A formal-coefficient implementation verified the identity for generic
  polynomial curves of every degree from 1 through 12. The formula itself is
  degree-free. Thus a raw two-dimensional tangent sweep has zero or
  nonconstant determinant and cannot be Keller.
- This is a checkable obstruction to one template, not to all possible plane
  constructions. Extra twists and parameters are outside its scope. No bound
  changed; the broader search is residue.
