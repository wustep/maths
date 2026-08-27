import Mathlib.Analysis.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic

/-
# HPS algebraic coefficients

Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, Proposition 2.5 prints

  1.1184 < b(3) < 1.1185,     1.2071 < (√2+1)/2 < 1.2072.

The proofs isolate the unique real root of `δ^3 + 3δ = 2` (for `b(3)`)
or square both sides (for `b(2)`). No analysis beyond real powers and
square roots is used. The file does not claim a new bound on `N_c`.
-/

namespace IonizationExcess

noncomputable def b2 : ℝ := (Real.sqrt 2 + 1) / 2

/-- HPS `b(3)`, printed in Proposition 2.5. -/
noncomputable def b3 : ℝ :=
  (2 / 3) * (1 + Real.sqrt 2) ^ (1 / 3 : ℝ) /
    ((1 + Real.sqrt 2) ^ (2 / 3 : ℝ) - 1)

noncomputable def t3 : ℝ := (1 + Real.sqrt 2) ^ (1 / 3 : ℝ)

noncomputable def δ3 : ℝ := t3 - t3⁻¹

lemma one_add_sqrt_two_pos : 0 < 1 + Real.sqrt 2 := by positivity

lemma one_add_sqrt_two_gt_one : 1 < 1 + Real.sqrt 2 := by
  have : 0 < Real.sqrt 2 := by positivity
  linarith

lemma t3_pos : 0 < t3 :=
  Real.rpow_pos_of_pos one_add_sqrt_two_pos _

lemma t3_ne_zero : t3 ≠ 0 := t3_pos.ne'

lemma t3_gt_one : 1 < t3 :=
  Real.one_lt_rpow one_add_sqrt_two_gt_one (by norm_num)

lemma t3_sq_gt_one : 1 < t3 ^ 2 := by
  nlinarith [t3_gt_one, t3_pos]

lemma one_div_three_inv : (1 / 3 : ℝ) = (3⁻¹ : ℝ) := by norm_num

lemma two_div_three_factor : (2 / 3 : ℝ) = (1 / 3 : ℝ) * 2 := by norm_num

lemma t3_pow_three : t3 ^ 3 = 1 + Real.sqrt 2 := by
  unfold t3
  rw [one_div_three_inv]
  exact Real.rpow_inv_natCast_pow (le_of_lt one_add_sqrt_two_pos) (by decide)

lemma rpow_two_thirds :
    (1 + Real.sqrt 2) ^ (2 / 3 : ℝ) = t3 ^ 2 := by
  unfold t3
  rw [two_div_three_factor, Real.rpow_mul (le_of_lt one_add_sqrt_two_pos),
    Real.rpow_two]

lemma inv_one_add_sqrt_two : (1 + Real.sqrt 2)⁻¹ = Real.sqrt 2 - 1 := by
  have hsq : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  refine inv_eq_of_mul_eq_one_right ?_
  nlinarith

lemma sub_inv_cubic (t : ℝ) (ht : t ≠ 0) :
    (t - t⁻¹) ^ 3 + 3 * (t - t⁻¹) = t ^ 3 - t⁻¹ ^ 3 := by
  have h1 : t * t⁻¹ = 1 := mul_inv_cancel₀ ht
  have h2 : t ^ 2 * t⁻¹ = t := by
    calc
      t ^ 2 * t⁻¹ = t * t * t⁻¹ := by ring
      _ = t * 1 := by rw [mul_assoc, h1]
      _ = t := mul_one t
  have h3 : t * t⁻¹ ^ 2 = t⁻¹ := by
    calc
      t * t⁻¹ ^ 2 = t * t⁻¹ * t⁻¹ := by ring
      _ = 1 * t⁻¹ := by rw [h1]
      _ = t⁻¹ := one_mul _
  calc
    (t - t⁻¹) ^ 3 + 3 * (t - t⁻¹)
        = t ^ 3 - 3 * t ^ 2 * t⁻¹ + 3 * t * t⁻¹ ^ 2 - t⁻¹ ^ 3
            + 3 * t - 3 * t⁻¹ := by ring
    _ = t ^ 3 - 3 * t + 3 * t⁻¹ - t⁻¹ ^ 3 + 3 * t - 3 * t⁻¹ := by
        rw [h2, h3]
    _ = t ^ 3 - t⁻¹ ^ 3 := by ring

lemma δ3_cubic : δ3 ^ 3 + 3 * δ3 = 2 := by
  unfold δ3
  rw [sub_inv_cubic t3 t3_ne_zero, t3_pow_three, inv_pow, t3_pow_three,
    inv_one_add_sqrt_two]
  ring

lemma δ3_pos : 0 < δ3 := by
  unfold δ3
  have hinv : t3⁻¹ < 1 := by
    have := mul_lt_mul_of_pos_right t3_gt_one (inv_pos.mpr t3_pos)
    rwa [one_mul, mul_inv_cancel₀ t3_ne_zero] at this
  linarith

lemma b3_eq_of_t3 : b3 = (2 / 3) * t3 / (t3 ^ 2 - 1) := by
  unfold b3
  rw [rpow_two_thirds]

lemma b3_eq_two_div_three_δ : b3 = (2 / 3) / δ3 := by
  have hden : t3 ^ 2 - 1 ≠ 0 := ne_of_gt (sub_pos.mpr t3_sq_gt_one)
  rw [b3_eq_of_t3]
  unfold δ3
  field_simp [t3_ne_zero, hden]
  ring

lemma cubic_eval_div {a b : ℝ} (hb : b ≠ 0) :
    (a / b) ^ 3 + 3 * (a / b) - 2
      = (a ^ 3 + 3 * a * b ^ 2 - 2 * b ^ 3) / b ^ 3 := by
  field_simp [hb]
  ring

lemma cubic_at_upper_neg :
    (4000 / 6711 : ℝ) ^ 3 + 3 * (4000 / 6711) - 2 < 0 := by
  rw [cubic_eval_div (by norm_num : (6711 : ℝ) ≠ 0)]
  exact div_neg_of_neg_of_pos (by norm_num) (by norm_num)

lemma cubic_at_lower_pos :
    0 < (1250 / 2097 : ℝ) ^ 3 + 3 * (1250 / 2097) - 2 := by
  rw [cubic_eval_div (by norm_num : (2097 : ℝ) ≠ 0)]
  exact div_pos (by norm_num) (by norm_num)

/-- If `δ^3 + 3δ = 2` and `f(a) < 0` for `f(x) = x^3 + 3x - 2`, then `a < δ`.
The difference factors as `(δ - a)(δ^2 + δa + a^2 + 3)` with positive second
factor. -/
lemma lt_of_cubic_neg {δ a : ℝ}
    (hδ : δ ^ 3 + 3 * δ = 2) (ha : a ^ 3 + 3 * a - 2 < 0) : a < δ := by
  have hquad : 0 < δ ^ 2 + δ * a + a ^ 2 + 3 := by
    nlinarith [sq_nonneg (δ + a), sq_nonneg δ, sq_nonneg a]
  have hdiff :
      (δ - a) * (δ ^ 2 + δ * a + a ^ 2 + 3)
        = (δ ^ 3 + 3 * δ) - (a ^ 3 + 3 * a) := by
    ring
  have hpos : 0 < (δ - a) * (δ ^ 2 + δ * a + a ^ 2 + 3) := by
    linarith [hδ, ha, hdiff]
  nlinarith

lemma gt_of_cubic_pos {δ a : ℝ}
    (hδ : δ ^ 3 + 3 * δ = 2) (ha : 0 < a ^ 3 + 3 * a - 2) : δ < a := by
  have hquad : 0 < δ ^ 2 + δ * a + a ^ 2 + 3 := by
    nlinarith [sq_nonneg (δ + a), sq_nonneg δ, sq_nonneg a]
  have hdiff :
      (δ - a) * (δ ^ 2 + δ * a + a ^ 2 + 3)
        = (δ ^ 3 + 3 * δ) - (a ^ 3 + 3 * a) := by
    ring
  have hneg : (δ - a) * (δ ^ 2 + δ * a + a ^ 2 + 3) < 0 := by
    linarith [hδ, ha, hdiff]
  nlinarith

lemma δ3_gt_upper : (4000 / 6711 : ℝ) < δ3 :=
  lt_of_cubic_neg δ3_cubic cubic_at_upper_neg

lemma δ3_lt_lower : δ3 < (1250 / 2097 : ℝ) :=
  gt_of_cubic_pos δ3_cubic cubic_at_lower_pos

lemma b3_upper_as_recip :
    (11185 / 10000 : ℝ) = 2 / (3 * (4000 / 6711)) := by
  norm_num

lemma b3_lower_as_recip :
    (11184 / 10000 : ℝ) = 2 / (3 * (1250 / 2097)) := by
  norm_num

/-- Printed HPS upper bound `b(3) < 1.1185`. -/
theorem b3_lt : b3 < 11185 / 10000 := by
  have hb : b3 = 2 / (3 * δ3) := by
    rw [b3_eq_two_div_three_δ, div_div]
  rw [hb, b3_upper_as_recip]
  have hposδ : 0 < 3 * δ3 := mul_pos (by norm_num) δ3_pos
  have hposq : 0 < 3 * (4000 / 6711 : ℝ) := by positivity
  have hlt : 3 * (4000 / 6711 : ℝ) < 3 * δ3 :=
    mul_lt_mul_of_pos_left δ3_gt_upper (by norm_num)
  have hinv : (3 * δ3)⁻¹ < (3 * (4000 / 6711 : ℝ))⁻¹ :=
    (inv_lt_inv₀ hposδ hposq).mpr hlt
  simpa [div_eq_mul_inv] using
    mul_lt_mul_of_pos_left hinv (by norm_num : (0 : ℝ) < 2)

/-- Printed HPS lower bound `1.1184 < b(3)`. -/
theorem b3_gt : (11184 / 10000 : ℝ) < b3 := by
  have hb : b3 = 2 / (3 * δ3) := by
    rw [b3_eq_two_div_three_δ, div_div]
  rw [hb, b3_lower_as_recip]
  have hposδ : 0 < 3 * δ3 := mul_pos (by norm_num) δ3_pos
  have hposq : 0 < 3 * (1250 / 2097 : ℝ) := by positivity
  have hlt : 3 * δ3 < 3 * (1250 / 2097 : ℝ) :=
    mul_lt_mul_of_pos_left δ3_lt_lower (by norm_num)
  have hinv : (3 * (1250 / 2097 : ℝ))⁻¹ < (3 * δ3)⁻¹ :=
    (inv_lt_inv₀ hposq hposδ).mpr hlt
  simpa [div_eq_mul_inv] using
    mul_lt_mul_of_pos_left hinv (by norm_num : (0 : ℝ) < 2)

theorem b3_enclosure :
    (11184 / 10000 : ℝ) < b3 ∧ b3 < (11185 / 10000 : ℝ) :=
  ⟨b3_gt, b3_lt⟩

lemma sqrt_two_gt : (14142 / 10000 : ℝ) < Real.sqrt 2 := by
  rw [Real.lt_sqrt (by positivity)]
  norm_num

lemma sqrt_two_lt : Real.sqrt 2 < (14144 / 10000 : ℝ) := by
  rw [Real.sqrt_lt (by positivity) (by positivity)]
  norm_num

/-- Printed HPS enclosure of `b(2) = (√2+1)/2`. -/
theorem b2_enclosure :
    (12071 / 10000 : ℝ) < b2 ∧ b2 < (12072 / 10000 : ℝ) := by
  unfold b2
  constructor
  · linarith [sqrt_two_gt]
  · linarith [sqrt_two_lt]

end IonizationExcess
