# q12 claim — leftover one-flip of three q11 followup certificates

Status: residue (2026-09-26). Selected leaf:
`q12: one-flip radius-three of the three q11 followup certificates`
in `../LEAVES.md`. The existence predicate below is not established.

Let B be the set of 2,367 nonempty schemes in the published
`deg8.pcoms.txz` archive of Geiselmann et al., *Limits of combinatorial
patchworking*, arXiv:2602.06888v4, §4.3. Let A be the seventeen
independently verified schemes in `../certs/new_schemes.json`. Let Q
be the q8 scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩. Let N be the nine q9 schemes in
`../q9/certs/new_schemes.json`. Let K be the thirteen q10 schemes in
`../q10/certs/new_schemes.json`. Let L be the eight q11 schemes in
`../q11/certs/new_schemes.json`. The baseline is
|B ∪ A ∪ Q ∪ N ∪ K ∪ L| = 2,415.

The attempted predicate was the existence of certificates (T, h, s)
such that T is a primitive triangulation of the 45 lattice points of
8Δ₂, h is an exact strict convex lifting for T, s assigns a sign ±1
to every lattice point, and the recomputed real scheme S(T,s) is
not in B ∪ A ∪ Q ∪ N ∪ K ∪ L. No such certificate is in
`certs/new_schemes.json`. This does not change the inequality

    number of nonempty degree-eight T-curve schemes ≥ 2,415.

The two preferred targets remain ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩. A regular patchwork realizing either would
also decide its algebraic realizability. No search failure is
reported as an algebraic exclusion. Neither preferred target is
decided.

Finite search domain:

1. One-flip radius-three balls of the three q11 followup certificates
   ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨10⟩⟩, ⟨1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩,
   ⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩.
   These three were produced by q11 followup and were never used as
   one-flip seeds. Plan hash `544498c92d5c94d04a0c087f8c6424080120da7420c4108a07a15691c744c912`.
   Each ball is one unimodular diagonal flip followed by all sign
   changes of Hamming weight at most three. All 93 finished
   (1,416,018 evaluations) and produced no scheme outside the
   baseline (`certs/coverage_leftover.json`).
2. One-flip of a new leftover certificate was not started: the
   leftover produced none.

Falsifiers of a proposed certificate: a missing/extra lattice point,
nonprimitive or overlapping cells, a failed strict lifting inequality,
invalid sign, disagreement between two independently implemented
topology computations, or membership of the actual scheme in
B ∪ A ∪ Q ∪ N ∪ K ∪ L. A candidate rejected by either implementation does not
improve the bound. This finished leftover with no new scheme is
residue, not a lower bound.

`run_all.sh` must exit zero only when the existence predicate has
been verified. Absence of candidates must not produce exit zero.
Search coverage has a separate collect entry point:
`python3 collect.py` then `python3 coverage.py`.
