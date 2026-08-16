import Mathlib

namespace SchurNumberSeven

/-- No monochromatic equation `x + y = z` inside `[1, n]`. -/
def SumFreeOn (n : —) (c : — — Fin 7) : Prop :=
  — x y, 1 —¤ x — 1 —¤ y — x + y —¤ n —
    Â¬(c x = c y —§ c y = c (x + y))

/-- Reflection about `1698` cannot be imposed on all of `[1, 1697]`:
the reflected pair `566, 1132` is also the Schur equation `566 + 566 = 1132`. -/
theorem no_fully_reflection_symmetric_coloring_1697
    (c : — — Fin 7)
    (hsf : SumFreeOn 1697 c)
    (hsym : — x, 1 —¤ x — x —¤ 1697 — c x = c (1698 - x)) : False := by
  have hs := hsym 566 (by norm_num) (by norm_num)
  have hf := hsf 566 566 (by norm_num) (by norm_num) (by norm_num)
  apply hf
  constructor
  Â· rfl
  Â· norm_num at hs —¢
    exact hs

end SchurNumberSeven
