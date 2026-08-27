/-
  Tiny exact lemmas for line E. Lean 4.32.0, no mathlib, no lake.

  1. T₂(t) = 2t² − 1 and the Chebyshev recurrence T₂ = 2t T₁ − T₀.
  2. The 2×2 adjugate identity A * adj(A) = (det A) I over ℤ.
     That is the algebraic content of DΦ · Y = (det DΦ) (X ∘ Φ)
     once Y := adj(DΦ) (X ∘ Φ).
  3. The integer points of u² + v² = 2 and u² − v² = 0 are exactly
     the four points (±1, ±1). Two degree-2 curves, four intersections.
-/

namespace Hilbert16E

def T0 (_t : Int) : Int := 1
def T1 (t : Int) : Int := t
def T2 (t : Int) : Int := 2 * t * t - 1

theorem T2_recurrence (t : Int) : T2 t = 2 * t * T1 t - T0 t := by
  rfl

theorem T2_at_integers :
    T2 0 = -1 ∧ T2 1 = 1 ∧ T2 (-1) = 1 := by
  decide

structure Mat2 where
  a : Int
  b : Int
  c : Int
  d : Int
deriving DecidableEq, Repr

def det (m : Mat2) : Int := m.a * m.d - m.b * m.c

def adj (m : Mat2) : Mat2 :=
  { a := m.d, b := -m.b, c := -m.c, d := m.a }

def mul (A B : Mat2) : Mat2 :=
  { a := A.a * B.a + A.b * B.c
    b := A.a * B.b + A.b * B.d
    c := A.c * B.a + A.d * B.c
    d := A.c * B.b + A.d * B.d }

theorem mul_adj_aa (a b c d : Int) :
    a * d + b * (-c) = a * d - b * c := by
  rw [Int.mul_neg, Int.sub_eq_add_neg]

theorem mul_adj_ab (a b : Int) :
    a * (-b) + b * a = 0 := by
  rw [Int.mul_neg, Int.mul_comm b a, Int.add_left_neg]

theorem mul_adj_ba (c d : Int) :
    c * d + d * (-c) = 0 := by
  rw [Int.mul_neg, Int.mul_comm d c, Int.add_left_neg]

theorem mul_adj_bb (a b c d : Int) :
    c * (-b) + d * a = a * d - b * c := by
  rw [Int.mul_neg, Int.mul_comm c b, Int.mul_comm d a, Int.sub_eq_add_neg,
      Int.add_comm]

theorem mul_adj (m : Mat2) :
    mul m (adj m) = { a := det m, b := 0, c := 0, d := det m } := by
  cases m with
  | mk a b c d =>
    simp [mul, adj, det]
    exact ⟨mul_adj_aa a b c d, mul_adj_ab a b, mul_adj_ba c d, mul_adj_bb a b c d⟩

lemma sq_nonneg (x : Int) : 0 ≤ x * x :=
  Int.mul_self_nonneg x

lemma sq_ge_four_of_abs_ge_two {x : Int} (h : 2 ≤ |x|) : 4 ≤ x * x := by
  have hx : 0 ≤ |x| := abs_nonneg x
  have : 2 * 2 ≤ |x| * |x| :=
    Int.mul_le_mul h h (by decide : (0 : Int) ≤ 2) hx
  simpa [Int.mul_self_abs] using this

lemma abs_le_one_of_sq_sum_two {x y : Int}
    (h : x * x + y * y = 2) : |x| ≤ 1 := by
  have hx0 : 0 ≤ x * x := sq_nonneg x
  have hy0 : 0 ≤ y * y := sq_nonneg y
  have : x * x ≤ 2 := by
    have := Int.le_add_of_nonneg_right (a := x * x) hy0
    rw [h] at this
    exact this
  by_contra hx
  have hx2 : 2 ≤ |x| := by
    have : 1 < |x| := Int.not_le.mp hx
    omega
  have : 4 ≤ x * x := sq_ge_four_of_abs_ge_two hx2
  omega

lemma sq_eq_one {x : Int} (h : x * x = 1) : x = 1 ∨ x = -1 := by
  have hx : |x| ≤ 1 := by
    by_contra hx
    have : 2 ≤ |x| := by
      have : 1 < |x| := Int.not_le.mp hx
      omega
    have : 4 ≤ x * x := sq_ge_four_of_abs_ge_two this
    omega
  have : x = -1 ∨ x = 0 ∨ x = 1 := by
    have : -1 ≤ x ∧ x ≤ 1 := abs_le.mp hx
    omega
  rcases this with h1 | h0 | h1
  · exact Or.inr h1
  · exact absurd (by simpa [h0] using h) (by decide : (0 : Int) ≠ 1)
  · exact Or.inl h1

theorem two_quadrics (x y : Int)
    (h1 : x * x + y * y = 2) (h2 : x * x - y * y = 0) :
    (x = 1 ∨ x = -1) ∧ (y = 1 ∨ y = -1) := by
  have hx1 : x * x = 1 := by
    -- add the two equations: 2 x² = 2
    have : (x * x + y * y) + (x * x - y * y) = 2 := by
      rw [h1, h2]
      rfl
    have : x * x + x * x = 2 := by
      have hcancel : (x * x + y * y) + (x * x - y * y) = x * x + x * x := by
        rw [Int.sub_eq_add_neg]
        have : x * x + y * y + (x * x + - (y * y)) =
            x * x + x * x + (y * y + - (y * y)) := by
          ac_rfl
        rw [this, Int.add_neg_cancel, Int.add_zero]
      rw [← hcancel]
      exact this
    have : 2 * (x * x) = 2 * 1 := by
      rw [Int.two_mul]
      exact this
    exact Int.eq_of_mul_eq_mul_left (by decide : (2 : Int) ≠ 0) this
  have hy1 : y * y = 1 := by
    have : (x * x + y * y) - (x * x - y * y) = 2 := by
      rw [h1, h2]
      rfl
    have : y * y + y * y = 2 := by
      have hcancel : (x * x + y * y) - (x * x - y * y) = y * y + y * y := by
        rw [Int.sub_eq_add_neg, Int.sub_eq_add_neg]
        have : - (x * x + - (y * y)) = - (x * x) + y * y := by
          rw [Int.neg_add, Int.neg_neg]
        rw [this]
        have : x * x + y * y + (- (x * x) + y * y) =
            (x * x + - (x * x)) + (y * y + y * y) := by
          ac_rfl
        rw [this, Int.add_neg_cancel, Int.zero_add]
      rw [← hcancel]
      exact this
    have : 2 * (y * y) = 2 * 1 := by
      rw [Int.two_mul]
      exact this
    exact Int.eq_of_mul_eq_mul_left (by decide : (2 : Int) ≠ 0) this
  exact ⟨sq_eq_one hx1, sq_eq_one hy1⟩

end Hilbert16E
