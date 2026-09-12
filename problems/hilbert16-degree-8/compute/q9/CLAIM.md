# q9 claim — nine schemes beyond the q8 census

Status: certified dent (2026-09-12). Selected leaf:
`q9: remaining 1,108 balls of the q8 one-flip radius-three domain`
in `../LEAVES.md`.

Let B be the set of 2,367 nonempty schemes in the published
`deg8.pcoms.txz` archive of Geiselmann et al., *Limits of combinatorial
patchworking*, arXiv:2602.06888v4, §4.3. Let A be the seventeen
independently verified schemes in `../certs/new_schemes.json`. Let Q
be the q8 scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩ in `../q8/certs/new_schemes.json`.
The baseline is |B ∪ A ∪ Q| = 2,385.

The verified predicate is the existence of certificates (T, h, s)
such that T is a primitive triangulation of the 45 lattice points of
8Δ₂, h is an exact strict convex lifting for T, s assigns a sign ±1
to every lattice point, and the recomputed real scheme S(T,s) is
not in B ∪ A ∪ Q. Nine such certificates are in
`certs/new_schemes.json`. This establishes the exact inequality

    number of nonempty degree-eight T-curve schemes ≥ 2,394.

Witnesses, each with an integer lifting and independent Python/Rust
topology checks:

- ⟨3 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ (20 ovals, (p,n) = (5,15))
- ⟨5 ⊔ 1⟨2⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ (20 ovals, (p,n) = (8,12))
- ⟨5 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (20 ovals, (p,n) = (8,12))
- ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (19 ovals, (p,n) = (7,12))
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (18 ovals, (p,n) = (6,12))
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (17 ovals, (p,n) = (5,12))
- ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (20 ovals, (p,n) = (7,13))
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (19 ovals, (p,n) = (6,13))
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (18 ovals, (p,n) = (5,13))

All 2,688 global strict lifting inequalities pass on each witness
(minimum slack 16, 8, 2, 2, 2, 8, 2, 2, 2 respectively). Python's
curve-segment computation and Rust's monochromatic-region graph
independently recover the same nesting forest. Each scheme is absent
from the archive's TYPE fields and filenames, the replayed B, the
seventeen additions A, and Q.

The two preferred targets were ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩. A regular patchwork realizing either would
also decide its algebraic realizability. No search failure will be
reported as an algebraic exclusion. Neither preferred target is
decided by this result.

Finite search domains:

1. The 1,108 unsearched balls of the q8 plan (tasks 82 through 1,189).
   Plan and seed hashes match `../q8/certs/coverage.json`. Each ball
   is one unimodular diagonal flip followed by all sign changes of
   Hamming weight at most three. All 1,108 finished (16,870,408
   evaluations) and produced the first five witnesses.
2. One-flip radius-three balls of the q8 certificate: 21 balls,
   319,746 evaluations, no further scheme.
3. One-flip radius-three balls of the five certificates from (1):
   115 balls, 1,750,990 evaluations, four further witnesses.

Falsifiers of a proposed certificate: a missing/extra lattice point,
nonprimitive or overlapping cells, a failed strict lifting inequality,
invalid sign, disagreement between two independently implemented
topology computations, or membership of the actual scheme in
B ∪ A ∪ Q. A candidate rejected by either implementation does not
improve the bound. An incomplete search is residue.

`run_all.sh` must exit zero only when this existence predicate has
been verified, with both independent checks and rejection/forced-answer
controls. A successful baseline replay or absence of candidates must
not produce exit zero. Search coverage has a separate collect entry
point.
