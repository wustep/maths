import Mathlib.Data.Real.Basic
import Mathlib.Tactic

/-
# Real lifts of the HPS integer witnesses

This file needs only `Mathlib.Data.Real.Basic` and `Mathlib.Tactic`.
It does not introduce cube roots. The inequalities here are the
cleared-denominator forms of the printed HPS enclosures; see
`B3NatWitness.lean` for the same statements in `Nat`.
-/

namespace IonizationExcess

/-- Real form of `b3_upper_witness`. Equivalent to `b(3) < 1.1185`
once `b(3) = 2/(3δ)` and `δ^3 + 3δ = 2` are available. -/
theorem b3_upper_real_witness :
    (4000 : ℝ) ^ 3 + 3 * 4000 * 6711 ^ 2 < 2 * 6711 ^ 3 := by
  norm_num

/-- Real form of `b3_lower_witness`. Equivalent to `1.1184 < b(3)`. -/
theorem b3_lower_real_witness :
    (2 : ℝ) * 2097 ^ 3 < 1250 ^ 3 + 3 * 1250 * 2097 ^ 2 := by
  norm_num

/-- Real form of `b2_lower_witness`. Equivalent to `1.2071 < b(2)`. -/
theorem b2_lower_real_witness :
    (14142 : ℝ) ^ 2 < 2 * 10000 ^ 2 := by
  norm_num

/-- Real form of `b2_upper_witness`. Equivalent to `b(2) < 1.2072`. -/
theorem b2_upper_real_witness :
    (2 : ℝ) * 10000 ^ 2 < 14144 ^ 2 := by
  norm_num

end IonizationExcess
