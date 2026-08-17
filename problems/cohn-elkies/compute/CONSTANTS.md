# Independently recomputed constants (mpmath dps=40)

All values below were recomputed tonight, not copied from secondary blogs.

## Hexagonal packing (target)

- Center density `δ_hex = 1/(2√3) = √3/6 = 0.2886751345948128822545743902509787278238`
- Area density `Δ_hex = π/(2√3) = 0.906899682117108915361219637392477477...`
- Theorem 3.2 last-sign-change target: `2π r_*^2 = 4π/√3 = 7.255197456936871402376313030568622929136`

## Published Cohn–Elkies 2003 (Annals 157, 689–714)

- Table 3, n=2: best packing `0.28868`, new upper bound `0.28868` (center density, five decimals).
- Table 4, n=2: `2π r^2 = 7.25520`, forced double roots `21.77, 29.02, 50.79, 65.34, 90.19`.
- Recomputed from the printed Table 4 `R`:
  - `δ ≤ 7.25520/(8π) = 0.2886752357800797600176013700050665498581`
  - ratio vs hex `= 1.000000350516046419403644002640063972807`

## Levenshtein / CE Proposition 6.1 (exact Bessel)

- `j_1 =` first positive zero of `J_1` `= 3.831705970207512315614435886308160766565`
- `Δ ≤ j_1^2/16 = 0.9176231651327433285762361105393816868551`
- `δ ≤ j_1^2/(16π) = 0.2920885252530132815247208990820543499602`
- ratio vs hex `= 1.011824332092168126325936766864430803816`

## This certificate (`certs/ce_d2_m5.json`)

- `R = 3627599/500000 = 7.255198`
- `δ ≤ R/(8π) = 0.2886751562026082140699334855631848636009`
- ratio vs hex `= 1.000000074851598708507619246976814816322`
- Isolated last odd root of `G`: `(1267758233/174737932, 878736008/121118135)`
  `≈ (7.2551976464961250, 7.2551976464961259)`
- Meets CE Table 3 (`δ` prints as `0.28868`).
- Strictly below CE Table 4 printed `R = 7.25520`.
- Does **not** attain `4π/√3`. Not a magic function.
