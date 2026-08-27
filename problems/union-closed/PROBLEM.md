# Frankl's union-closed sets conjecture

- Slug: `union-closed`
- List: P33
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open (ray-certified frequency 0.38304; 1/2 still open)
- Area: Extremal set theory
- Sources: Bruhn–Schaudt; Gilmer arXiv:2211.09055
- Started: 2026-08-17

## Statement

Every finite nontrivial union-closed family is conjectured to have an element in at least half its sets. Gilmer gave a positive constant; the 1/2 threshold is open.

## Tonight

A certified improvement of the published frequency constant, or a new finite classification with a verifier. Do not claim the 1/2 conjecture unless you prove it. Fetch Gilmer and the current best constant before searching.

## Result (2026-08-27)

On the two-point family `{b,1}`, pure Liu Example 4 (`β = 1`) has first-crossing equal to the unique critical point of `1 − (1−b)h(b)` on `(1−1/√2, 1/2]`. That number is `0.3830513565868…`, defined by `h(b) = (1−b) log₂((1−b)/b)`. The certified 5-decimal constant is `0.38304`: every mesh cell with mean `≤ 0.38304` has Gilmer ratio `≥ 1.0000217` (Python and C agree). This beats the 2026-08-17 ray number `0.38285` (`β = 1/5`) and Liu's published `0.382709`. Replay: `compute/q1/run_all.sh` (exit 0). Same hypothesis class as Liu Theorem 13. Not `1/2`. Not every measure on `[0,1]`.

## Result (2026-08-17)

On the two-point family `{b,1}` that Liu identified as the optimizer, the iid + Example-4 mix with weight `β = 1/5` has Gilmer ratio `≥ 1` for every mesh cell with mean `≤ 0.38285`. Liu's published number on the same family, using Example 5, is `0.382709`. Replay: `compute/verify.py` (exit 0). This is not a proof of the `1/2` conjecture, and it is not an unconditional theorem for every measure — it is the same hypothesis class as Liu Theorem 13, with a better protocol and an independent mesh.
