# q11 claim — eight schemes beyond the q10 census

Status: certified dent (2026-09-22). Selected leaf:
`q11: one-flip radius-three of the seven q10 followup certificates`
in `../LEAVES.md`.

Let B be the set of 2,367 nonempty schemes in the published
`deg8.pcoms.txz` archive of Geiselmann et al., *Limits of combinatorial
patchworking*, arXiv:2602.06888v4, §4.3. Let A be the seventeen
independently verified schemes in `../certs/new_schemes.json`. Let Q
be the q8 scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩. Let N be the nine q9 schemes in
`../q9/certs/new_schemes.json`. Let K be the thirteen q10 schemes in
`../q10/certs/new_schemes.json`. The baseline is
|B ∪ A ∪ Q ∪ N ∪ K| = 2,407.

The verified predicate is the existence of certificates (T, h, s)
such that T is a primitive triangulation of the 45 lattice points of
8Δ₂, h is an exact strict convex lifting for T, s assigns a sign ±1
to every lattice point, and the recomputed real scheme S(T,s) is
not in B ∪ A ∪ Q ∪ N ∪ K. Eight such certificates are in
`certs/new_schemes.json`. This establishes the exact inequality

    number of nonempty degree-eight T-curve schemes ≥ 2,415.

Witnesses, each with an integer lifting and independent Python/Rust
topology checks:

- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ (18 ovals, (p,n) = (4,14))
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ (19 ovals, (p,n) = (5,14))
- ⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (16 ovals, (p,n) = (3,13))
- ⟨1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (16 ovals, (p,n) = (3,13))
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩ (19 ovals, (p,n) = (4,15))
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨10⟩⟩ (19 ovals, (p,n) = (4,15))
- ⟨1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (17 ovals, (p,n) = (3,14))
- ⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ (17 ovals, (p,n) = (3,14))

All 2,688 global strict lifting inequalities pass on each witness
(minimum slack 8, 8, 8, 4, 8, 8, 8, 8 respectively).
Python's curve-segment computation and Rust's monochromatic-region
graph independently recover the same nesting forest. Each scheme is
absent from the archive's TYPE fields and filenames, the replayed B,
the seventeen additions A, Q, N, and K.

The two preferred targets were ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩. A regular patchwork realizing either would
also decide its algebraic realizability. No search failure will be
reported as an algebraic exclusion. Neither preferred target is
decided by this result.

Finite search domains:

1. One-flip radius-three balls of the seven q10 followup certificates
   ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩, ⟨1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩,
   ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩, ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩,
   ⟨4 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩, ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩,
   ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩.
   Plan hash `43c0f0d9227d1672f9521e9d3cc7cb8d9a04113be47a827a60826614ee10b31a`.
   Each ball is one unimodular diagonal flip followed by all sign
   changes of Hamming weight at most three. All 205 finished
   (3,121,330 evaluations) and produced the first five witnesses.
2. One-flip radius-three balls of those five certificates: 150 balls,
   2,283,900 evaluations, three further witnesses.

Falsifiers of a proposed certificate: a missing/extra lattice point,
nonprimitive or overlapping cells, a failed strict lifting inequality,
invalid sign, disagreement between two independently implemented
topology computations, or membership of the actual scheme in
B ∪ A ∪ Q ∪ N ∪ K. A candidate rejected by either implementation does not
improve the bound. An incomplete search is residue.

`run_all.sh` must exit zero only when this existence predicate has
been verified, with both independent checks and rejection/forced-answer
controls. A successful baseline replay or absence of candidates must
not produce exit zero. Search coverage has a separate collect entry
point.
