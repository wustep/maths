import Mathlib

/-!
# A sharp finite modular obstruction for the Brocard--Ramanujan equation

The computation in compute/modular_hunt.py found that modulo 151, the
sixteen consecutive values n = 16, ..., 31 all make n! + 1 quadratic
nonresidues.  The adjacent values pass this particular modulus:

* 15! + 1 ≡ 49 = 7² (mod 151);
* 32! + 1 ≡ 4 = 2² (mod 151).

Thus the certified interval is maximal for this modulus.  The theorem below
formalizes only the obstruction, not the Brocard--Ramanujan conjecture.
-/

namespace BrocardRamanujan

private def Forbidden151 (r : ℕ) : Prop :=
  r = 13 ∨ r = 14 ∨ r = 24 ∨ r = 33 ∨ r = 53 ∨ r = 66 ∨ r = 71 ∨
    r = 83 ∨ r = 114 ∨ r = 129 ∨ r = 131 ∨ r = 141 ∨ r = 146

private theorem square_mod_151_not_forbidden (m : ℕ) :
    ¬Forbidden151 (m ^ 2 % 151) := by
  intro hm
  have hlt : m % 151 < 151 := Nat.mod_lt _ (by norm_num)
  rw [Nat.pow_mod] at hm
  generalize hx : m % 151 = x at hm hlt
  interval_cases x <;> norm_num [Forbidden151] at hm

/--
For every 16 ≤ n ≤ 31, n! + 1 is not a square.  The proof uses only
reduction modulo 151; no estimate of the factorial is involved.
-/
theorem factorial_add_one_ne_square_mod_151
    (n m : ℕ) (h_lower : 16 ≤ n) (h_upper : n ≤ 31) :
    n.factorial + 1 ≠ m ^ 2 := by
  intro h_square
  have hmod := congrArg (fun value : ℕ => value % 151) h_square
  have hforbidden : Forbidden151 (m ^ 2 % 151) := by
    interval_cases n <;>
      norm_num [Nat.factorial] at hmod ⊢ <;>
      omega
  exact square_mod_151_not_forbidden m hforbidden

end BrocardRamanujan
