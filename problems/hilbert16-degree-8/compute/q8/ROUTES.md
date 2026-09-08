# Routes and residuals

| Route | State | Test / surviving domain |
| --- | --- | --- |
| Another maximal-sign sweep on a census triangulation | dead in the prior record | All 184 were swept; neither open nest occurs. Other triangulations survive. |
| Another small even-split walk from the two completed nest components | dead in the prior record | q7 completed both. Different odd skeletons survive. |
| Structural quotient of the enormous remaining collection graph | live, exploratory | Any proposed deletion rule must preserve the full nesting tree, not merely (p,n). |
| One diagonal flip plus radius-three sign changes from the 55 seed certificates | certified dent; hunt stopped | Ball 82 gives ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩ outside B ∪ A. Exact lifting and both topology checks pass. 1,108 balls remain unsearched. |

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

## Discovery and lifting

The search stopped after 82 complete balls, 1,248,532 evaluations
and 807 distinct observed schemes. Task 81 (zero-based) uses
`deg8/o22-p07-n15/(5v1(3)v1(12)).pcom` as its seed. Replace the
diagonal [(2,3),(6,0)] with [(3,2),(5,1)] and change the signs at
(0,0), (0,1) and (7,0). Python independently returns
⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩. This scheme occurs 79 times in that ball.

The old lifting fails two strict inequalities on the changed mesh.
The existing 200,000-step projection search (`haas.regularize`,
seed 0) obtained no new lifting. That was a failed numerical search,
not evidence of nonregularity. A linear feasibility solve with
SciPy 1.18.1 / HiGHS succeeded. Clearing the rational denominators
gave integer heights between -1,290 and 0; all 2,688 global strict
inequalities have slack at least 4. The committed certificate is
checked without SciPy. `lift_candidate.py` records the optional
discovery calculation.

The 1,108 remaining balls and the larger structural routes remain
unsearched. The new scheme has 20 ovals and decides neither open
22-oval nest. There is no algebraic exclusion claim.
