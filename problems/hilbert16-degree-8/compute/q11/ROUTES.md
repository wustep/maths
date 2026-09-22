# Routes and residuals

| Route | State | Test / surviving domain |
| --- | --- | --- |
| One-flip radius-three of the seven q10 followup certificates | certified dent; domain finished | 205 balls, five schemes outside B ∪ A ∪ Q ∪ N ∪ K. Plan and seed hashes match the leftover seven. |
| One-flip radius-three of those five certificates | certified dent; domain finished | 150 balls, three further schemes. |
| One-flip of the three followup certificates | unsearched | The next leftover of the same method. |
| Two-flip, or radius four, of the same meshes | unsearched | Larger than this campaign. |
| Algebraic obstruction of either open (19,3) nest | open | Search failure here is not exclusion. |

## 2026-09-22 — leftover followup seeds

q10 searched one-flip balls of its first six certificates (169 balls)
and stopped. Seven further schemes appeared there and were not fed
back as seeds. Each ball is one unimodular diagonal flip and every
sign change of Hamming weight at most three. There is no symmetry
reduction. Search continued through every ball even after a
candidate appeared.

## Discovery and lifting

Five schemes appeared in the leftover 205 balls:

| scheme | ovals | (p,n) | first task | seed |
| --- | --- | --- | --- | --- |
| ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ | 18 | (4,14) | 17 | ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ |
| ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ | 19 | (5,14) | 17 | same mesh |
| ⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ | 16 | (3,13) | 17 | same mesh |
| ⟨1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ | 16 | (3,13) | 75 | ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ |
| ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩ | 19 | (4,15) | 167 | ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ |

⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ fills the a=0 hole of the family q9/q10 had
at a=1,2,3,4. One-flip balls of those five certificates then produced
three more: ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨10⟩⟩, ⟨1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩, and
⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩.

SciPy 1.15.3 / HiGHS produced an integer lifting in each case.
Exact arithmetic then checked every global strict inequality.
`lift_candidate.py` records the optional solve; replaying the
certificates needs no numerical package.

Neither preferred 22-oval nest appeared. No algebraic exclusion is
claimed.
