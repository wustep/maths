# Quest q1 — beat a documented small ℓ₂(r,2)

- Model: gpt-5.6-sol Max
- Started: 2026-08-16 ~02:46 PT
- Status: dent — ℓ₂(10,2) ≤ 50 certified
- Cost: M
- Shape: finite-cex

## What happened

Targeted simulated annealing from the Kaikkonen–Rosendahl 51-column seed produced a 50-column matrix. Independent exhaustive verification covers all 1024 syndromes. See WALKTHROUGH.md and `compute/H_r10_n50.txt`.

## Residue

- Certified: ℓ₂(10,2) ≤ 50. Matrix + verifier under compute/.
- Not a lower bound: n=49 left 7 uncovered.
- Secondary holes (8,25) and (9,38) unsolved.
- Do not claim f(2).
