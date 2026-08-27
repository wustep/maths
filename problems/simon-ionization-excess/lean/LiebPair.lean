import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic

/-
# Lieb pair inequality

Lieb's 1984 bound `N_c < 2Z+1` uses the triangle inequality on
electron positions in the form

  (‖x‖ + ‖y‖) / ‖x - y‖ ≥ 1    for x ≠ y.

This file records that comparison and nothing further. It does not
formalize HVZ, the quadratic-form remainder, or the ionization
conjecture.
-/

namespace IonizationExcess

/-- Triangle inequality, rearranged, in any real normed group. -/
theorem lieb_pair_normed {E : Type*} [NormedAddCommGroup E]
    (x y : E) (h : x ≠ y) :
    (‖x‖ + ‖y‖) / ‖x - y‖ ≥ 1 := by
  have hpos : 0 < ‖x - y‖ := by
    rwa [norm_pos_iff, sub_ne_zero]
  exact (one_le_div hpos).2 (norm_sub_le x y)

/-- The comparison Lieb uses on pairs of electron coordinates. -/
theorem lieb_pair {x y : EuclideanSpace ℝ (Fin 3)} (h : x ≠ y) :
    (‖x‖ + ‖y‖) / ‖x - y‖ ≥ 1 :=
  lieb_pair_normed x y h

end IonizationExcess
