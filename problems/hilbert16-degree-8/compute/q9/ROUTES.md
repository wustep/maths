# Routes and residuals

| Route | State | Test / surviving domain |
| --- | --- | --- |
| Remaining 1,108 balls of the q8 one-flip radius-three plan | certified dent; domain finished | Tasks 82–1,189. Five schemes outside B ∪ A ∪ Q. Plan and seed hashes match q8. |
| One-flip radius-three around the q8 certificate | finished, no new scheme | 21 balls, 319,746 evaluations. |
| Published (19,3) M-certificates inside the remaining plan | finished, neither nest | Tasks 763–885. Silence here is not an algebraic exclusion. |
| One-flip radius-three around the five leftover-plan certificates | certified dent; domain finished | 115 balls, four further schemes. |

## 2026-09-12 — remaining q8 balls

The q8 search stopped after task 81. The leftover is exactly tasks
82 through 1,189 of the same 1,190-row plan, each a unimodular
diagonal flip and every sign change of Hamming weight at most three.
There is no symmetry reduction. Search continued through every ball
even after a candidate appeared.

Six workers partitioned the leftover. A seventh worker searched the
21 flips of the q8 certificate, a domain disjoint from the 1,190.

## Discovery and lifting

Five schemes appeared in the leftover plan, on eleven tasks:

| scheme | ovals | (p,n) | first task | seed |
| --- | --- | --- | --- | --- |
| ⟨3 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ | 20 | (5,15) | 107 | ⟨5 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ |
| ⟨5 ⊔ 1⟨2⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ | 20 | (8,12) | 267 | ⟨8 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ |
| ⟨5 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ | 20 | (8,12) | 313 | ⟨8 ⊔ 2⟨1⟩ ⊔ 1⟨9⟩⟩ |
| ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ | 19 | (7,12) | 313 | same mesh as previous |
| ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ | 18 | (6,12) | 313 | same mesh as previous |

⟨3 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ fills the a=3 hole in a family whose census and
prior additions already had a=0,1,2,4,5; it is the same move that
produced the q8 scheme in ⟨a ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩.

One-flip balls of those five certificates then filled the a=2 hole
of the ⟨a ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ family and produced a parallel
⟨a ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ family at a=2,3,4:

| scheme | ovals | (p,n) | first extra task |
| --- | --- | --- | --- |
| ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ | 17 | (5,12) | 37 |
| ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ | 20 | (7,13) | 50 |
| ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ | 19 | (6,13) | 50 |
| ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ | 18 | (5,13) | 50 |

SciPy 1.18.1 / HiGHS produced an integer lifting in each case.
Exact arithmetic then checked every global strict inequality.
`lift_candidate.py` records the optional solve; replaying the
certificates needs no numerical package.

Neither preferred 22-oval nest appeared. No algebraic exclusion is
claimed.
