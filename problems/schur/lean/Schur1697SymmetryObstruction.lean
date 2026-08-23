import Std

namespace SchurNumberSeven

/-- No monochromatic equation `x + y = z` inside `[1, n]`. -/
def SumFreeOn (n : Nat) (c : Nat -> Fin 7) : Prop :=
  forall x y, 1 <= x -> 1 <= y -> x + y <= n ->
    Not (And (c x = c y) (c y = c (x + y)))

/-- Reflection about `1698` cannot be imposed on all of `[1, 1697]`:
the reflected pair `566, 1132` is also the Schur equation `566 + 566 = 1132`. -/
theorem no_fully_reflection_symmetric_coloring_1697
    (c : Nat -> Fin 7)
    (hsf : SumFreeOn 1697 c)
    (hsym : forall x, 1 <= x -> x <= 1697 -> c x = c (1698 - x)) : False := by
  have hs : c 566 = c 1132 := hsym 566 (by decide) (by decide)
  have hf := hsf 566 566 (by decide) (by decide) (by decide)
  apply hf
  exact And.intro rfl hs

end SchurNumberSeven
