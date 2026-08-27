# The second term for Sidon subsets of [N]

- Slug: `sidon-second-term`
- List: P07
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort max`
- Status: dent of Hou–Zhao 0.9435. Independent 8-kernel certificate (free histograms, L=6) has √(ab)=0.94324253097, so C<0.94325. Erdős–Turán not claimed.
- Area: Additive combinatorics
- Sources: Erdos Problem #30; Green 100 #31
- Started: 2026-08-17

## Statement

A Sidon set has all pairwise sums distinct. F(N) is the size of a largest Sidon subset of [N]. Constructions give F(N) >= sqrt(N)+O(1). The best general upper bound is F(N) <= sqrt(N)+0.98183 N^{1/4}+O(1). Any strict improvement of either side for infinitely many N is open.

## Tonight

A finite Sidon record that does not improve an infinite-family bound is not a new bound. Hunt one of:
1. An explicit infinite-family construction with second term beating sqrt(N)+O(1) for infinitely many N, with a verifier.
2. A certified improvement of the 0.98183 coefficient that holds for infinitely many N.
3. A reusable exact lemma that strictly tightens one of those two sides.

Do not claim the Erdos-Turan conjecture. Isolated F(N) tables are an incomplete search unless they feed (1)-(3).

## After the fetch (2026-08-17)

Erdős #30 is still open (page edited 2026-04-06). Green #31 is still open.
The PROBLEM.md line 0.98183 is CHO25. Hou–Zhao, arXiv:2607.01169v2 (5 Jul 2026),
already has F(N) ≤ √N + 0.9435 N^{1/4} + O(1) with an eight-kernel rational
certificate. That is the published record this folder has to beat.

This folder independently verifies Hou–Zhao, then certifies an L=6 lift of
their kernels: F(N) ≤ √N + 0.94349251 N^{1/4} + O(1), which is 8.22×10^{-8}
below their exact γ0. No growing lower-bound second term. Erdős–Turán not
claimed. Replay in `compute/README.md`.

## After 2026-08-27

Hou–Zhao is still the published record to beat: 0.9435, with exact
γ0 = 0.943492590713545. The L=6 lift does not change the four-decimal
statement. A later search re-optimizes the eight kernels as free
symmetric histograms at L=6 (the published R≥4 shapes were six-mode
profiles).
The rational certificate `compute/q1/certs/joint_r8_L6.json` has

    F(N) ≤ √N + 0.94325 N^{1/4} + O(1)

with exact √(ab) = 0.9432425309706136. That is a dent of the published
0.9435, not only of γ0. Replay in `compute/q1/README.md`. Erdős–Turán
not claimed. No growing lower-bound second term.
