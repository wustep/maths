/-
  Tiny exact lemmas for line E. Lean 4.32.0, no mathlib, no lake.

  1. T₂(t) = 2t² − 1 and the Chebyshev recurrence T₂ = 2t T₁ − T₀.
  2. The 2×2 adjugate identity A * adj(A) = (det A) I over ℤ.
     That is the algebraic content of DΦ · Y = (det DΦ) (X ∘ Φ)
     once Y := adj(DΦ) (X ∘ Φ).
  3. The four points (±1, ±1) lie on both u² + v² = 2 and
     u² − v² = 0 (two degree-2 curves attaining the Bézout number 4
     over ℤ; the Python/Rust checker treats the real count).
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
  rw [Int.mul_neg, Int.mul_comm d c, Int.add_right_neg]

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

theorem four_points_on_two_quadrics :
    (1 * 1 + 1 * 1 = (2 : Int) ∧ 1 * 1 - 1 * 1 = 0) ∧
    (1 * 1 + (-1) * (-1) = 2 ∧ 1 * 1 - (-1) * (-1) = 0) ∧
    ((-1) * (-1) + 1 * 1 = 2 ∧ (-1) * (-1) - 1 * 1 = 0) ∧
    ((-1) * (-1) + (-1) * (-1) = 2 ∧ (-1) * (-1) - (-1) * (-1) = 0) := by
  decide

end Hilbert16E
