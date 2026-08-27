import Mathlib.Analysis.Real.Sqrt
import Mathlib.Tactic

/-!
# Algebraic conversion from Frank–Hundertmark–Jex–Nam Proposition 10 at `d = 1`

Frank–Hundertmark–Jex–Nam, arXiv:1808.09017, Proposition 10, give

  `K₁ / K₁^{cl} ≥ 16 / (243 𝒞₁²)`

for `𝒞₁ > 0`. The duality identity at `d = 1` is

  `L_{1,1} / L_{1,1}^{cl} = 1 / √(K₁ / K₁^{cl})`.

These two relations convert a `𝒞₁`-bound into

  `L_{1,1} / L_{1,1}^{cl} ≤ (9 √3 / 4) 𝒞₁`.

This file proves that conversion and the comparison of the resulting
bound against the published `1456 / 1000`. It does not claim the
Lieb–Thirring conjecture, and it does not evaluate `𝒞₁`.
-/

namespace FhjnProp10Conversion

/-- `√243 = 9 √3`. -/
theorem sqrt_243 : √(243 : ℝ) = 9 * √3 := by
  rw [Real.sqrt_eq_iff_eq_sq (by norm_num) (by positivity)]
  rw [mul_pow, Real.sq_sqrt (by norm_num)]
  norm_num

/-- `√16 = 4`. -/
theorem sqrt_16 : √(16 : ℝ) = 4 := by
  rw [Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)]
  norm_num

/-- The exact algebraic identity behind the `d = 1` conversion. -/
theorem inv_sqrt_K_lower_eq {C : ℝ} (hC : 0 < C) :
    1 / √((16 : ℝ) / (243 * C ^ 2)) = (9 * √3 / 4) * C := by
  rw [Real.sqrt_div (by positivity), Real.sqrt_mul (by norm_num), Real.sqrt_sq hC.le,
    sqrt_16, sqrt_243]
  field_simp

/-- From the Proposition 10 lower bound on `K / Kcl` and the `d = 1`
duality identity, the converted `L / Lcl` bound follows. -/
theorem L_over_Lcl_le_of_K_bound
    {KKcl LLcl C : ℝ}
    (hC : 0 < C)
    (hK : (16 : ℝ) / (243 * C ^ 2) ≤ KKcl)
    (hL : LLcl = 1 / √KKcl) :
    LLcl ≤ (9 * √3 / 4) * C := by
  have hlower_pos : 0 < (16 : ℝ) / (243 * C ^ 2) := by positivity
  have hmono : 1 / √KKcl ≤ 1 / √((16 : ℝ) / (243 * C ^ 2)) :=
    one_div_le_one_div_of_le (Real.sqrt_pos.mpr hlower_pos) (Real.sqrt_le_sqrt hK)
  rw [hL, ← inv_sqrt_K_lower_eq hC]
  exact hmono

/-- Comparing the converted bound with the published `1.456` is
equivalent to a bound on `C`. -/
theorem converted_bound_lt_1456_div_1000_iff {C : ℝ} :
    (9 * √3 / 4) * C < (1456 : ℝ) / 1000 ↔
      C < ((1456 : ℝ) / 1000) * 4 / (9 * √3) := by
  have hfac : 0 < 9 * √3 / 4 := by positivity
  have heq : ((1456 : ℝ) / 1000) / (9 * √3 / 4) =
      ((1456 : ℝ) / 1000) * 4 / (9 * √3) := by
    field_simp
  rw [mul_comm, ← heq]
  exact (lt_div_iff₀ hfac).symm

/-- A fully rational sufficient condition. The cutoff `467 / 1250 = 0.3736`
is strictly below the exact threshold `1456/1000 · 4 / (9 √3) ≈ 0.373610`
and large enough to cover the trial value `𝒞₁ ≤ 0.373556` quoted after
Frank–Hundertmark–Jex–Nam Lemma 11. The coarser cutoff `3734 / 10000`
is also sufficient, but this one is tighter. -/
theorem converted_bound_of_C_le_467_div_1250
    {C : ℝ} (h : C ≤ (467 : ℝ) / 1250) :
    (9 * √3 / 4) * C < (1456 : ℝ) / 1000 := by
  have hfac : 0 ≤ 9 * √3 / 4 := by positivity
  refine lt_of_le_of_lt (mul_le_mul_of_nonneg_left h hfac) ?_
  rw [← sq_lt_sq₀ (by positivity) (by positivity)]
  have hsq : (9 * √3 / 4 * ((467 : ℝ) / 1250)) ^ 2 =
      (243 : ℝ) * 467 ^ 2 / (16 * 1250 ^ 2) := by
    rw [mul_pow, div_pow, mul_pow, Real.sq_sqrt (by norm_num)]
    ring
  rw [hsq, div_pow]
  rw [div_lt_div_iff₀ (by positivity) (by positivity)]
  norm_num

end FhjnProp10Conversion
