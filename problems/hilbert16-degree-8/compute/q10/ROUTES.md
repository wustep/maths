# Routes and residuals

| Route | State | Test / surviving domain |
| --- | --- | --- |
| One-flip radius-three of the four q9 followup certificates | certified dent; domain finished | 106 balls, six schemes outside B ∪ A ∪ Q ∪ N. Plan and seed hashes match the leftover four. |
| One-flip radius-three of those six certificates | certified dent; domain finished | 169 balls, seven further schemes. |
| One-flip of the seven followup certificates | unsearched | The next leftover of the same method. |
| Two-flip, or radius four, of the same meshes | unsearched | Larger than this campaign. |
| Algebraic obstruction of either open (19,3) nest | open | Search failure here is not exclusion. |

## 2026-09-20 — leftover followup seeds

q9 searched one-flip balls of its first five certificates (115 balls)
and stopped. Four further schemes appeared there and were not fed
back as seeds. The family ⟨a ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ occupied a=2,3,4
and not a=1. Each ball is one unimodular diagonal flip and every
sign change of Hamming weight at most three. There is no symmetry
reduction. Search continued through every ball even after a
candidate appeared.

## Discovery and lifting

Six schemes appeared in the leftover 106 balls:

| scheme | ovals | (p,n) | first task | seed |
| --- | --- | --- | --- | --- |
| ⟨1 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ | 16 | (4,12) | 0 | ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ |
| ⟨2 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ | 17 | (5,12) | 0 | same mesh |
| ⟨3 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ | 18 | (6,12) | 0 | same mesh |
| ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ | 17 | (4,13) | 15 | same seed, different flip |
| ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ | 19 | (5,14) | 41 | ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ |
| ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ | 20 | (6,14) | 41 | same mesh |

⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ fills the a=1 hole of the family q9 had
at a=2,3,4. One-flip balls of those six certificates then produced
seven more, including a=0 of ⟨a ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩, a=4 of
⟨a ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩, a=1 of ⟨a ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩, and
⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩.

SciPy 1.18.1 / HiGHS produced an integer lifting in each case.
Exact arithmetic then checked every global strict inequality.
`lift_candidate.py` records the optional solve; replaying the
certificates needs no numerical package.

Neither preferred 22-oval nest appeared. No algebraic exclusion is
claimed.
