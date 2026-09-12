# Finite handles — degree-eight real schemes

Reconstructed on 2026-09-08 from PROBLEM, ATTACK, WALKTHROUGH and
q1–q5/q7. There is no q6 directory. Historical completed searches are
listed as `residue`: completion of a neighborhood did not improve the
classification record. They are not exclusions of algebraic schemes.

| Leaf | Status | Evidence / what survives |
| --- | --- | --- |
| Seventeen schemes outside the published 2,367 | certified | `certs/new_schemes.json`; nonempty T-scheme count at least 2,384. |
| Maximal strata of all 184 census triangulations | residue | `certs/census_span_classification.json`; exactly the published 38 M-schemes. Other triangulations survive. |
| Radius-one thicken of all census maximal strata | residue | q1–q3; no scheme beyond census plus seventeen. Larger sign distance and other triangulations survive. |
| Up to three split changes around published deep-nest collections | residue | q4; no new M-scheme. More distant collections survive. |
| Purely odd collections through size five | residue | q3/q7; twelve known schemes. Larger odd collections and mixed odd/even collections survive; this does not bound the odd skeleton of all new M-schemes. |
| Even extensions of the published a=10 and a=17 odd skeletons | residue | q7; only the two known nests. Different odd skeletons survive. |
| Larger fixed-odd components and the all-even component | open | q7 counted some components but did not classify them all. A structural quotient is needed before further enumeration. |
| q8: escape the census by changing triangulation and signs together | certified | `q8/CLAIM.md`: number of nonempty degree-eight T-curve schemes ≥ 2,385. New scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩; exact integer lifting and independent Python/Rust checks. Search stopped after 82/1,190 balls; the leftover 1,108 are the q9 row. |
| q9: remaining 1,108 balls of the q8 one-flip radius-three domain | certified | `q9/CLAIM.md`: number of nonempty degree-eight T-curve schemes ≥ 2,394. Nine schemes outside B ∪ A ∪ {⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩}. All 1,108 leftover balls finished; 115 one-flip balls of those certificates added four more; 21 flips of the q8 certificate added nothing. Neither open nest appeared. |
| Algebraic obstruction outside combinatorial patchworking | open | Neither undecided (19,3) deep nest is decided. T-curve nonexistence alone would not decide algebraic nonexistence. |

The covering problem is frozen. One heavy process at a time; no
unbounded BFS queue. The 1,190-ball one-flip domain is finished.
Further progress is a scheme outside the 2,394, a decision of either
open (19,3) nest, or a new recorded finite handle.
