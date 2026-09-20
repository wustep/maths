# q10 claim — schemes beyond the q9 census

Status: open hunt (2026-09-20). Selected leaf:
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
not in B ∪ A ∪ Q ∪ N. Certificates, if any, live in
`certs/new_schemes.json`. This would establish the exact inequality

    number of nonempty degree-eight T-curve schemes ≥ 2,394 + k

for k the number of distinct verified schemes outside the baseline.

The two preferred targets remain ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩. A regular patchwork realizing either would
also decide its algebraic realizability. No search failure will be
reported as an algebraic exclusion.

Finite search domain:

1. One-flip radius-three balls of the four q9 followup certificates
   ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩, ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩,
   ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩, ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩.
   These four were produced by q9 followup and were never used as
   one-flip seeds. Plan hash `be9520910264e4bcdba6c03618384023d544804e4999a42516a391210e9bd320`,
   106 balls, 1,613,956 evaluations counting repetitions.
2. If (1) produces a new certificate, one-flip radius-three balls of
   that certificate, recorded separately.

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
