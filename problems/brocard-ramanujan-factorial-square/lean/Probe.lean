import Mathlib

example : Nat.factorial 31 % 151 = 52 := by
  norm_num [Nat.factorial]

example (m : ℕ) :
    m ^ 2 % 151 ≠ 13 ∧ m ^ 2 % 151 ≠ 14 ∧ m ^ 2 % 151 ≠ 24 := by
  rw [Nat.pow_mod]
  have hlt : m % 151 < 151 := Nat.mod_lt _ (by norm_num)
  generalize hx : m % 151 = x at hlt
  interval_cases x <;> norm_num
