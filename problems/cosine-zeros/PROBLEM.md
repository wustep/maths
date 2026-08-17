# Zeros of integer cosine sums

- Slug: `cosine-zeros`
- List: P16
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Harmonic analysis
- Sources: Green 100 #82; Bedert, arXiv:2312.04454
- Started: 2026-08-17

## Statement

For |A|=n, the best universal lower bound on the number of zeros of sum_{a in A} cos(2 pi a theta) grows only like (log log n)^{1-o(1)}, while examples give only an O(n^{2/3} log^{2/3} n) upper barrier. The true order is unknown.

## Tonight

A certified improvement of either the universal lower bound or the construction-side upper barrier, with an independent verifier. Isolated root tables for a few sets are residue. Fetch Bedert and Green #82 before searching. Do not claim a full determination of the order.

## Outcome (2026-08-17)

Named the constant in Bedert Theorem 1.3 for `{0,1}`-cosine sums:
`Z(N) ≥ log log N / (200 log log log N)` whenever the right-hand side is at least `4`.
Replay: `compute/run_all.sh`. Did not beat the exponent `(log log N)^{1-o(1)}` and did not beat the construction `O((N log N)^{2/3})`. Prefix search and Hankel-det experiment are residue.
