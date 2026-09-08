# q8 claim — a scheme beyond the current census

Status: attempted, not established. Selected leaf:
`q8: escape the census by changing triangulation and signs together`
in `../LEAVES.md`.

Let B be the set of 2,367 nonempty schemes in the published
`deg8.pcoms.txz` archive of Geiselmann et al., *Limits of combinatorial
patchworking*, arXiv:2602.06888v4, §4.3. Let A be the seventeen
independently verified schemes in `../certs/new_schemes.json`.
The baseline is |B ∪ A| = 2,384.

The attempted predicate is the existence of a certificate (T, h, s)
such that T is a primitive triangulation of the 45 lattice points of
8Δ₂, h is an exact strict convex lifting for T, s assigns a sign ±1
to every lattice point, and the recomputed real scheme S(T,s) is
not in B ∪ A. This would establish the exact inequality

    number of nonempty degree-eight T-curve schemes ≥ 2,385.

The two preferred targets are ⟨4 ⊔ 1⟨2 ⊔ 1⟨14⟩⟩⟩ and
⟨14 ⊔ 1⟨2 ⊔ 1⟨4⟩⟩⟩. A regular patchwork realizing either would
also decide its algebraic realizability. No search failure will be
reported as an algebraic exclusion.

Initial finite search domain: one unimodular diagonal flip from each
of the 38 published M-certificates and the seventeen additions,
followed by all sign changes of Hamming weight at most three.
Regularity is a separate exact check. Duplicate triangulations and
equivalent sign distributions may be identified only with recorded
maps. Further routes, reductions, controls and residual domains will
be recorded in `ROUTES.md` before they are used.

Falsifiers of a proposed certificate: a missing/extra lattice point,
nonprimitive or overlapping cells, a failed strict lifting inequality,
invalid sign, disagreement between two independently implemented
topology computations, or membership of the actual scheme in B ∪ A.
A candidate rejected by either implementation does not improve the
bound. An incomplete search is residue.

`run_all.sh` must exit zero only when this existence predicate has
been verified, with both independent checks and rejection/forced-answer
controls. A successful baseline replay or absence of candidates must
not produce exit zero. Search coverage has a separate replay entry point.
