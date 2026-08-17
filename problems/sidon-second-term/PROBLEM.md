# The second term for Sidon subsets of [N]

- Slug: `sidon-second-term`
- List: P07
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort max`
- Status: open (Erdős–Turán not claimed). Hou–Zhao arXiv:2607.01169v2 already has C<0.9435. This folder certifies C<0.94349251 by an L=6 lift of their kernels (8.22e-8 below their γ0).
- Area: Additive combinatorics
- Sources: Erdos Problem #30; Green 100 #31
- Started: 2026-08-17

## Statement

A Sidon set has all pairwise sums distinct. F(N) is the size of a largest Sidon subset of [N]. Constructions give F(N) >= sqrt(N)+O(1). The best general upper bound is F(N) <= sqrt(N)+0.98183 N^{1/4}+O(1). Any strict improvement of either side for infinitely many N is open.

## Tonight

A finite Sidon record that does not improve an infinite-family bound is not a dent. Hunt one of:
1. An explicit infinite-family construction with second term beating sqrt(N)+O(1) for infinitely many N, with a verifier.
2. A certified improvement of the 0.98183 coefficient that holds for infinitely many N.
3. A reusable exact lemma that strictly tightens one of those two sides.

Do not claim the Erdos-Turan conjecture. Isolated F(N) tables are residue unless they feed (1)-(3).

## After the fetch (2026-08-17)

Erdős #30 is still open (page edited 2026-04-06). Green #31 is still open.
The PROBLEM.md line 0.98183 is CHO25. Hou–Zhao, arXiv:2607.01169v2 (5 Jul 2026),
already has F(N) ≤ √N + 0.9435 N^{1/4} + O(1) with an eight-kernel rational
certificate. That is the published record this folder has to beat.

This folder independently verifies Hou–Zhao, then certifies an L=6 lift of
their kernels: F(N) ≤ √N + 0.94349251 N^{1/4} + O(1), which is 8.22×10^{-8}
below their exact γ0. No growing lower-bound second term. Erdős–Turán not
claimed. Replay in `compute/README.md`.
