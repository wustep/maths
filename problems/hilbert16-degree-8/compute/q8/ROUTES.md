# Routes and residuals

| Route | State | Test / surviving domain |
| --- | --- | --- |
| Another maximal-sign sweep on a census triangulation | dead in the prior record | All 184 were swept; neither open nest occurs. Other triangulations survive. |
| Another small even-split walk from the two completed nest components | dead in the prior record | q7 completed both. Different odd skeletons survive. |
| Structural quotient of the enormous remaining collection graph | live, exploratory | Any proposed deletion rule must preserve the full nesting tree, not merely (p,n). |
| One diagonal flip plus radius-three sign changes from the 55 seed certificates | live, selected finite domain | New geometry with a reproducible endpoint; retain exact regularity certificates and a coverage manifest. |

The first two rows rely on the recorded completed searches; they are
not independently rerun billion-evaluation claims of this campaign.
The published certificates themselves are replayed before searching.

## 2026-09-08 — resumed finite domain

The recovered source files had no saved search outputs. There are 1,190
seed/flip pairs from the 55 seeds. Each sign ball has
1 + 45 + 990 + 14,190 = 15,226 evaluations, for 18,118,940 in all,
counting repetitions between seeds. There is no symmetry reduction.

Search every combinatorial flip, including any whose regularity is not
yet known. This is a superset of the selected regular-flip domain.
If a new topology appears, solve for a strict lifting and verify it
exactly before claiming a T-curve. No failed lifting attempt is an
algebraic exclusion. The empty curve is excluded from novelty.

`search.py` writes an atomic coverage checkpoint after each complete
ball and stops on a candidate. The checkpoint records source hashes,
the seed and plan hashes, each removed/added diagonal, the resulting
triangulation hash, full scheme frequencies and any candidate signs.
`run_all.sh` is reserved for the existence claim; coverage has a
separate replay command.
