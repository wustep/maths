# q10 claim — thirteen schemes beyond the q9 census

Status: certified dent (2026-09-20). Selected leaf:
`q10: one-flip radius-three of the four q9 followup certificates`
in `../LEAVES.md`.

Let B be the set of 2,367 nonempty schemes in the published
`deg8.pcoms.txz` archive of Geiselmann et al., *Limits of combinatorial
patchworking*, arXiv:2602.06888v4, §4.3. Let A be the seventeen
independently verified schemes in `../certs/new_schemes.json`. Let Q
be the q8 scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩. Let N be the nine q9 schemes in
`../q9/certs/new_schemes.json`. The baseline is |B ∪ A ∪ Q ∪ N| = 2,394.

The verified predicate is the existence of certificates (T, h, s)
such that T is a primitive triangulation of the 45 lattice points of
8Δ₂, h is an exact strict convex lifting for T, s assigns a sign ±1
to every lattice point, and the recomputed real scheme S(T,s) is
not in B ∪ A ∪ Q ∪ N. Thirteen such certificates are in
`certs/new_schemes.json`. This establishes the exact inequality

    number of nonempty degree-eight T-curve schemes ≥ 2,407.

Witnesses, each with an integer lifting and independent Python/Rust
topology checks:

- ⟨1 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (16 ovals, (p,n) = (4,12))
- ⟨2 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (17 ovals, (p,n) = (5,12))
- ⟨3 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (18 ovals, (p,n) = (6,12))
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (17 ovals, (p,n) = (4,13))
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (19 ovals, (p,n) = (5,14))
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (20 ovals, (p,n) = (6,14))
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (17 ovals, (p,n) = (4,13))
- ⟨1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (15 ovals, (p,n) = (3,12))
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (18 ovals, (p,n) = (5,13))
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (19 ovals, (p,n) = (6,13))
- ⟨4 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (19 ovals, (p,n) = (7,12))
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (18 ovals, (p,n) = (4,14))
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩ (20 ovals, (p,n) = (5,15))

All 2,688 global strict lifting inequalities pass on each witness
(minimum slack 2, 2, 2, 8, 2, 2, 8, 8, 8, 8, 8, 8, 2 respectively).
Python's curve-segment computation and Rust's monochromatic-region
graph independently recover the same nesting forest. Each scheme is
absent from the archive's TYPE fields and filenames, the replayed B,
the seventeen additions A, Q, and N.

The two preferred targets were ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩. A regular patchwork realizing either would
also decide its algebraic realizability. No search failure will be
reported as an algebraic exclusion. Neither preferred target is
decided by this result.

Finite search domains:

1. One-flip radius-three balls of the four q9 followup certificates
   ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩, ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩,
   ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩, ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩.
   Plan hash `be9520910264e4bcdba6c03618384023d544804e4999a42516a391210e9bd320`.
   Each ball is one unimodular diagonal flip followed by all sign
   changes of Hamming weight at most three. All 106 finished
   (1,613,956 evaluations) and produced the first six witnesses.
2. One-flip radius-three balls of those six certificates: 169 balls,
   2,573,194 evaluations, seven further witnesses.

Falsifiers of a proposed certificate: a missing/extra lattice point,
nonprimitive or overlapping cells, a failed strict lifting inequality,
invalid sign, disagreement between two independently implemented
topology computations, or membership of the actual scheme in
B ∪ A ∪ Q ∪ N. A candidate rejected by either implementation does not
improve the bound. An incomplete search is residue.

`run_all.sh` must exit zero only when this existence predicate has
been verified, with both independent checks and rejection/forced-answer
controls. A successful baseline replay or absence of candidates must
not produce exit zero. Search coverage has a separate collect entry
point.
