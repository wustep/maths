# Improve the lower bound for the seventh Schur number

- Slug: `schur`
- Solver: Codex `gpt-5.6-sol` Max (2026-08-16 overnight; q3 on 2026-08-23). Grok watched only.
- Status: open — no 1697 coloring found
- Area: Ramsey theory / additive combinatorics
- Sources: Rowley, arXiv:2107.03560 (S(7)≥1696); Bengone et al., arXiv:2607.15034 (shifted S-templates)
- Started: 2026-08-16
- Tonight: finite-cex — a 7-coloring of [1697] with no monochromatic $x+y=z$

## In general

The Schur number $S(k)$ is the largest $n$ such that $\{1,\dots,n\}$ can be $k$-colored with no monochromatic $x+y=z$ (including $2x=z$). Exact values are known only through $S(5)$. Rowley (2021) gave $S(7)\ge 1696$ via a fully symmetric 7-coloring of [1696]. A coloring of [1697] would raise the bound by one.

## Precise statement

A $k$-coloring of $[n]$ is *sum-free* if there are no $x,y\in[n]$ (not necessarily distinct) with $x+y\le n$ monochromatic. **Tonight:** find a 7-coloring of [1697] that is sum-free, or record a precise incomplete SAT/search. Do not claim a new upper bound on $S(7)$.

## What happened (recovered)

q1: no 1697 coloring. Near-miss with 2 violations (file `compute/near_1697_two_violations.txt` recovered empty). Search log in `compute/q1-search-log.json`. Memory: commit `61e0369`.
q2: m=144 seed, still no 1697 coloring; still 2 violations. Alternate-template / CEGAR / exact SAT scripts recovered under compute/.
q3: recovered and verified Rowley's published 1696 specimen, then reconstructed and preserved a new 1697 near-coloring with exactly two violations. Unrestricted repair, lazy/full SAT repair, and color-twisted reflection all timed out. This is residue, not a lower bound.
q4: exact fixed-outside repairs through 132 mutable vertices were UNSAT; finite defect-vertex swaps and one-cut suffix color exchanges found no coloring; the 537-step color-twisted translation that forbids both residue sums was exactly UNSAT. These are named-family walls, not an upper bound.

## Related

- [Rowley, *An Improved Lower Bound for S(7)*, arXiv:2107.03560](https://arxiv.org/abs/2107.03560)
- [Bengone et al., *Shifted S-templates*, arXiv:2607.15034](https://arxiv.org/abs/2607.15034)
