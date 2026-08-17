# Frankl's union-closed sets conjecture

- Slug: `union-closed`
- List: P33
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open (ray-certified frequency 0.38285; 1/2 still open)
- Area: Extremal set theory
- Sources: Bruhn–Schaudt; Gilmer arXiv:2211.09055
- Started: 2026-08-17

## Statement

Every finite nontrivial union-closed family is conjectured to have an element in at least half its sets. Gilmer gave a positive constant; the 1/2 threshold is open.

## Tonight

A certified improvement of the published frequency constant, or a new finite classification with a verifier. Do not claim the 1/2 conjecture unless you prove it. Fetch Gilmer and the current best constant before searching.

## Result (2026-08-17)

On the two-point family `{b,1}` that Liu identified as the optimizer, the iid + Example-4 mix with weight `β = 1/5` has Gilmer ratio `≥ 1` for every mesh cell with mean `≤ 0.38285`. Liu's published number on the same family, using Example 5, is `0.382709`. Replay: `compute/verify.py` (exit 0). This is not a proof of the `1/2` conjecture, and it is not an unconditional theorem for every measure — it is the same hypothesis class as Liu Theorem 13, with a better protocol and an independent mesh.
