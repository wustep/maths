/-
# Integer witnesses for the HPS coefficient enclosure

Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, Proposition 2.5 prints

  1.1184 < b(3) < 1.1185

with

  b(3) = (2/3) * (1+√2)^{1/3} / ((1+√2)^{2/3} - 1).

Let t = (1+√2)^{1/3} and δ = t - t⁻¹. Cubing gives the monic relation

  δ^3 + 3δ - 2 = 0

and the reciprocal identity b(3) = 2/(3δ). The printed enclosure is then
equivalent to the two rational cubic comparisons

  (4000/6711)^3 + 3*(4000/6711) - 2 < 0
  (1250/2097)^3 + 3*(1250/2097) - 2 > 0

because 4000/6711 and 1250/2097 are the exact reciprocals of
(3/2)*(11185/10000) and (3/2)*(11184/10000). Clearing denominators
leaves the `Nat` inequalities below.

The same reduction for b(2) = (√2+1)/2 and the printed enclosure
1.2071 < b(2) < 1.2072 is the pair of squares

  14142^2 < 2 * 10000^2 < 14144^2.

This file imports nothing from mathlib. Check it with

  lean B3NatWitness.lean
-/

namespace IonizationExcess

/-- Expanded cubes and products used in the upper-bound witness. -/
theorem pow_4000_three : 4000 ^ 3 = 64000000000 := rfl

theorem pow_6711_two : 6711 ^ 2 = 45037521 := rfl

theorem pow_6711_three : 6711 ^ 3 = 302246803431 := rfl

/-- `f(4000/6711) < 0` after multiplying through by `6711^3 > 0`.
Equivalent to `b(3) < 11185/10000`. -/
theorem b3_upper_witness :
    4000 ^ 3 + 3 * 4000 * 6711 ^ 2 < 2 * 6711 ^ 3 :=
  calc
    4000 ^ 3 + 3 * 4000 * 6711 ^ 2 = 604450252000 := rfl
    _ < 604493606862 := by decide
    _ = 2 * 6711 ^ 3 := rfl

/-- Expanded cubes used in the lower-bound witness. -/
theorem pow_1250_three : 1250 ^ 3 = 1953125000 := rfl

theorem pow_2097_two : 2097 ^ 2 = 4397409 := rfl

theorem pow_2097_three : 2097 ^ 3 = 9221366673 := rfl

/-- `f(1250/2097) > 0` after multiplying through by `2097^3 > 0`.
Equivalent to `11184/10000 < b(3)`. The fraction `1250/2097` is
`2500/4194` in lowest terms. -/
theorem b3_lower_witness :
    2 * 2097 ^ 3 < 1250 ^ 3 + 3 * 1250 * 2097 ^ 2 :=
  calc
    2 * 2097 ^ 3 = 18442733346 := rfl
    _ < 18443408750 := by decide
    _ = 1250 ^ 3 + 3 * 1250 * 2097 ^ 2 := rfl

/-- Squared form of `14142/10000 < √2`, hence of `12071/10000 < b(2)`. -/
theorem b2_lower_witness : 14142 ^ 2 < 2 * 10000 ^ 2 :=
  calc
    14142 ^ 2 = 199996164 := rfl
    _ < 200000000 := by decide
    _ = 2 * 10000 ^ 2 := rfl

/-- Squared form of `√2 < 14144/10000`, hence of `b(2) < 12072/10000`. -/
theorem b2_upper_witness : 2 * 10000 ^ 2 < 14144 ^ 2 :=
  calc
    2 * 10000 ^ 2 = 200000000 := rfl
    _ < 200052736 := by decide
    _ = 14144 ^ 2 := rfl

end IonizationExcess
