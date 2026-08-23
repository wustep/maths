import Mathlib.NumberTheory.LegendreSymbol.QuadraticReciprocity
import Mathlib.NumberTheory.Wilson
import Mathlib.Tactic

/-!
# A Wilson-offset obstruction for the Brocard--Ramanujan equation

If `p = n + 2` is prime, Wilson's theorem reduces `n! + 1` to `2` modulo
`p`.  When `p` is `3` or `5` modulo `8`, the supplementary law for `2`
says that this residue is not a square.  This certifies a parameterized
family; it makes no claim about indices outside it.
-/

namespace BrocardRamanujan

theorem factorial_cast_eq_one_of_add_two_prime
    (n : ℕ) (hp : Nat.Prime (n + 2)) :
    (n.factorial : ZMod (n + 2)) = 1 := by
  letI : Fact (Nat.Prime (n + 2)) := ⟨hp⟩
  have hw := ZMod.wilsons_lemma (n + 2)
  have hpred : n + 2 - 1 = n + 1 := by omega
  rw [hpred, Nat.factorial_succ] at hw
  have hzero : ((n + 2 : ℕ) : ZMod (n + 2)) = 0 := by simp
  have hminus : ((n + 1 : ℕ) : ZMod (n + 2)) = -1 := by
    push_cast at hzero ⊢
    linear_combination hzero
  rw [Nat.cast_mul, hminus] at hw
  simpa using congrArg Neg.neg hw

/-- If `n + 2` is prime and is `3` or `5` modulo `8`, then `n! + 1`
cannot be a square. -/
theorem factorial_add_one_ne_square_of_add_two_prime
    (n m : ℕ) (hp : Nat.Prime (n + 2))
    (hclass : (n + 2) % 8 = 3 ∨ (n + 2) % 8 = 5) :
    n.factorial + 1 ≠ m ^ 2 := by
  intro hsquare
  letI : Fact (Nat.Prime (n + 2)) := ⟨hp⟩
  have hfac := factorial_cast_eq_one_of_add_two_prime n hp
  have hcast := congrArg (fun value : ℕ => (value : ZMod (n + 2))) hsquare
  norm_num [hfac] at hcast
  have hsquare_two : IsSquare (2 : ZMod (n + 2)) := by
    refine ⟨(m : ZMod (n + 2)), ?_⟩
    simpa [pow_two] using hcast
  have hp_ne_two : n + 2 ≠ 2 := by omega
  rw [ZMod.exists_sq_eq_two_iff hp_ne_two] at hsquare_two
  omega

end BrocardRamanujan
