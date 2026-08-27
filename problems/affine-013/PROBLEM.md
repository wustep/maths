# Extremal affine copies of {0,1,3}

- Slug: `affine-013`
- List: P05
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Extremal additive combinatorics
- Sources: Green 100 #24; Aaronson arXiv:1805.01980
- Started: 2026-08-17

## Statement

For an n-element integer set A, the conjectured maximum number of affine copies of {0,1,3} is (1/3+o(1))n^2, but even the asymptotic constant is unknown.

## Tonight

A certified small-n extremal table, a construction beating the published constant on infinitely many n, or an exact upper bound that moves the constant. Isolated small-n counts are an incomplete search unless they imply a new infinite-family bound. Fetch Green #24 before searching.

## Result (2026-08-17)

Aaronson’s T(S) (ordered triples with x+2y=3z) satisfies T(S) ≤ ⌈n²/2⌉
for every n-element S ⊂ ℤ, by an ordering-and-injection argument
adapted from Green–Sisask’s 3AP count. Hence γ_{1,2,-3} ≤ 1/2, which
is strictly below the published Hardy–Littlewood / Aaronson 3/4.
Constructions tonight do not beat the interval’s 1/3 (the almost-interval
{0,…,n−2,n} for n=3m has T = n²/3+1; a sporadic 7-set has T=18).
The conjecture γ=1/3 remains open. Verifier: `compute/verify_half.py`.

## Result (2026-08-27)

Residue. Endpoint induction and a second family search in `compute/q1/`
do not move 1/2. The 2/3 end-budget that would give γ=1/3 already fails
at n=5; both ends can score 9/10 of n−1 without beating the interval.
No certified family has limsup T/n² > 1/3. Replay: `compute/q1/run_all.sh`.
Cert: `compute/q1/certs/q1.json`.
