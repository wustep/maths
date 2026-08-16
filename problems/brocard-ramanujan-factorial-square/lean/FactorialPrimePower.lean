import Mathlib.Algebra.Prime.Lemmas
import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Tactic

/-!
# Prime-power concentration in the Brocard--Ramanujan factorization

If `n! + 1 = m^2` and `n >= 2`, parity writes `m = 2*a + 1`.  Expanding the
square then gives

`n! = 4 * a * (a + 1)`.

The consecutive factors are coprime.  Consequently, for every odd prime `p`,
an entire power `p^k` dividing `n!` has to divide one of `m - 1` and `m + 1`.
Unlike a fixed-modulus obstruction, the largest available exponent `k` grows
with `n`.  The result is a necessary condition only; it does not settle the
Brocard--Ramanujan conjecture.
-/

namespace BrocardRamanujan

/-- A Brown equation with `n >= 2` splits `n! / 4` into two consecutive
coprime factors.  The division-free formulation is convenient in `Nat`. -/
theorem exists_consecutive_coprime_factorization
    (n m : ℕ) (hn : 2 ≤ n) (hsquare : n.factorial + 1 = m ^ 2) :
    ∃ a : ℕ,
      m = 2 * a + 1 ∧
      Nat.Coprime a (a + 1) ∧
      n.factorial = 4 * (a * (a + 1)) := by
  have hfactorial_even : Even n.factorial :=
    even_iff_two_dvd.mpr (Nat.dvd_factorial (by norm_num) hn)
  have hsquare_odd : Odd (m ^ 2) := by
    rw [← hsquare]
    exact hfactorial_even.add_one
  have hm_odd : Odd m := (odd_pow_iff (by norm_num : 2 ≠ 0)).mp hsquare_odd
  obtain ⟨a, ha⟩ := hm_odd
  refine ⟨a, ha, ?_, ?_⟩
  · simpa using Nat.coprime_one_right a
  · have hexpand : (2 * a + 1) ^ 2 = 4 * (a * (a + 1)) + 1 := by ring
    apply Nat.add_right_cancel (n := 1)
    calc
      n.factorial + 1 = m ^ 2 := hsquare
      _ = (2 * a + 1) ^ 2 := by rw [ha]
      _ = 4 * (a * (a + 1)) + 1 := hexpand

/-- Every power of an odd prime that divides `n!` is concentrated in one of
the neighboring factors `m - 1` and `m + 1`.

Taking `k` to be the full exponent of `p` in `n!` gives the variable-modulus
condition `m ≡ ±1 (mod p^k)`.  This strengthens the familiar `mod p`
condition for primes in `(n/2, n]` and applies to every odd prime at most `n`.
-/
theorem odd_prime_power_dvd_neighbor
    (n m p k : ℕ) (hn : 2 ≤ n) (hsquare : n.factorial + 1 = m ^ 2)
    (hp : Nat.Prime p) (hp_ne_two : p ≠ 2) (hpow : p ^ k ∣ n.factorial) :
    p ^ k ∣ m - 1 ∨ p ^ k ∣ m + 1 := by
  obtain ⟨a, hm, hcoprime, hfactorization⟩ :=
    exists_consecutive_coprime_factorization n m hn hsquare
  have hp_not_dvd_four : ¬p ∣ 4 := by
    intro hp_four
    have hp_two : p ∣ 2 := hp.dvd_of_dvd_pow (by simpa using hp_four)
    exact hp_ne_two ((Nat.prime_dvd_prime_iff_eq hp Nat.prime_two).mp hp_two)
  have hproduct : p ^ k ∣ a * (a + 1) := by
    rw [hfactorization] at hpow
    exact hp.pow_dvd_of_dvd_mul_left k hp_not_dvd_four hpow
  by_cases hp_dvd_a : p ∣ a
  · have hp_not_dvd_succ : ¬p ∣ a + 1 :=
      hp.coprime_iff_not_dvd.mp (hcoprime.coprime_dvd_left hp_dvd_a)
    have hpower_dvd_a : p ^ k ∣ a :=
      hp.pow_dvd_of_dvd_mul_right k hp_not_dvd_succ hproduct
    left
    rw [hm]
    simpa using dvd_mul_of_dvd_right hpower_dvd_a 2
  · have hpower_dvd_succ : p ^ k ∣ a + 1 :=
      hp.pow_dvd_of_dvd_mul_left k hp_dvd_a hproduct
    right
    rw [hm]
    convert dvd_mul_of_dvd_right hpower_dvd_succ 2 using 1 <;> omega

end BrocardRamanujan
