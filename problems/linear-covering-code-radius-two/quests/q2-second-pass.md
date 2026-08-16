# Quest q2 — push ℓ₂(10,2) from 50 to 49

- Model: gpt-5.6-sol Max
- Started: 2026-08-16
- Status: residue — n=49 still 7 uncovered
- Cost: M
- Shape: finite-cex

## Idea

q1 certified n=50, r=10 (beats the published 51). A stochastic n=49 run left 7 uncovered syndromes — not a lower bound. Seed from H_r10_n50.txt and try to delete one column or anneal to 49. Independently verify any n=49 matrix (all 1024 syndromes, F₂-rank 10). Do not claim f(2). (8,25) and (9,38) are secondary.

## Residue

Still 7 uncovered on n=49. Search code recovered: `search_n49.c`, `search_n49_lifted.c`.
