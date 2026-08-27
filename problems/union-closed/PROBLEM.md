# Frankl's union-closed sets conjecture

- Slug: `union-closed`
- List: P33
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh` (2026-08-17); Grok 4.6 q1 / q2; Codex (GPT-5) q3 (2026-08-27)
- Status: open (ray-certified frequency 0.38305; 1/2 still open)
- Area: Extremal set theory
- Sources: Bruhn–Schaudt; Gilmer arXiv:2211.09055
- Started: 2026-08-17

## Statement

Every finite nontrivial union-closed family is conjectured to have an element in at least half its sets. Gilmer gave a positive constant; the 1/2 threshold is open.

## Tonight

A certified improvement of the published frequency constant, or a new finite classification with a verifier. Do not claim the 1/2 conjecture unless you prove it. Fetch Gilmer and the current best constant before searching.

## Result (2026-08-27, q3)

Dent: pure Liu Example 4 on `{b,1}` certifies
`0.38305 > 0.38304 > 0.382709087918741`. The last number is Liu's
published Example 5 value. The analytic first-crossing remains
`0.38305135658682558…`, leaving `1.3565868×10⁻⁶` above the printed
constant. On a 9,000×7,000 mesh, every retained cell with mean at most
`0.38305` has Gilmer ratio greater than 1. Python row-boundary and
exhaustive C verifiers agree on 20,440,358 retained cells, zero bad
cells, and minimum ratio `1.0000049143029008`. Replay:
`compute/q3/run_all.sh` (exit 0). A shared-input joint-entropy probe
reaches equality near `0.343708`. This leaves residue, and the q2
ceiling is unchanged. The scope remains the `{b,1}` family; Frankl's
`1/2` target and the every-measure inequality are open.

## Result (2026-08-27, q2)

The constant did not move. On `{b,1}`, every 2-sample bit protocol has first-crossing at most the q1 critical point `0.3830513565868…`, because `h(Π_{b,b}) ≤ 1`. Mixes (new `β`, Example 5, max-entropy), a half-target Fréchet protocol, and scaled `a(t)` all sit at or below that ceiling. Gilmer's KL path to `1/2` is Ellis's n=2 counterexample, replayed. Pure Example 4 fails a constructed 2-mixture at mean `0.38304` (CIID ratio `0.909137`); that is residue off the ray, not a dent. Replay: `compute/q2/run_all.sh` (exit 0). Still not `1/2`.

## Result (2026-08-27)

On the two-point family `{b,1}`, pure Liu Example 4 (`β = 1`) has first-crossing equal to the unique critical point of `1 − (1−b)h(b)` on `(1−1/√2, 1/2]`. That number is `0.3830513565868…`, defined by `h(b) = (1−b) log₂((1−b)/b)`. The certified 5-decimal constant is `0.38304`: every mesh cell with mean `≤ 0.38304` has Gilmer ratio `≥ 1.0000217` (Python and C agree). This beats the 2026-08-17 ray number `0.38285` (`β = 1/5`) and Liu's published `0.382709`. Replay: `compute/q1/run_all.sh` (exit 0). Same hypothesis class as Liu Theorem 13. Not `1/2`. Not every measure on `[0,1]`.

## Result (2026-08-17)

On the two-point family `{b,1}` that Liu identified as the optimizer, the iid + Example-4 mix with weight `β = 1/5` has Gilmer ratio `≥ 1` for every mesh cell with mean `≤ 0.38285`. Liu's published number on the same family, using Example 5, is `0.382709`. Replay: `compute/verify.py` (exit 0). This is not a proof of the `1/2` conjecture, and it is not an unconditional theorem for every measure — it is the same hypothesis class as Liu Theorem 13, with a better protocol and an independent mesh.
