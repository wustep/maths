# Walkthrough — An exact d=2 Cohn–Elkies function below the printed 7.25520

- Problem: `problems/cohn-elkies`
- Quest: SuperGrok 2026-08-17, Green 100 #42
- Model: grok-4.6 `--reasoning-effort xhigh`
- Date: 2026-08-17
- Argument status: exact rational Laguerre–Gaussian plus independently replayed root-counts
- Problem status: open. There is still no magic function. Green #42 is not solved.

## 0. What was actually missing

The missing object was not a new analytic idea. Cohn–Elkies §7 already says how to
build a radial admissible function in dimension 2: take an odd combination `G` of
`{L_1, L_3, …, L_{23}}` that vanishes at the origin and doubly at five nodes, an
even combination `H` of `{L_0, …, L_{22}}` that shares those double nodes and
cancels `G` to second order at a last sign-change `R`, and set

```
f(x)     = (H − G)(2π |x|²) exp(−π |x|²),
hat f(x) = (H + G)(2π |x|²) exp(−π |x|²).
```

They did this with exact rationals and Sturm, and they printed
`R = 7.25520` together with five two-decimal nodes. They did **not** print
the coefficients. Without the coefficients there is nothing to check.

The degree of freedom was therefore clerical and finite: put those five
nodes in `Q`, solve the two linear systems over `Q`, isolate the last odd
root of `G`, pick a rational `R` strictly above it, and certify the sign
conditions by exact division rather than by floating-point LP.

## 1. False starts (named obstacles)

- **Treat Mo–Wen–Xia `g₂` as a CE function.** Their 4-term cosine sum is
  periodic modulo `2A2`. Poisson summation on `R²` does not apply. The
  obstruction is the function class, not the arithmetic.
- **Chase a modular-form magic function.** That *is* Green #42. Sardari’s
  interpolation on the A2 nodes is the documented reason a first-derivative
  interpolation formula does not hand you the auxiliary function. One night
  of Eisenstein series would not have produced checkable signs.
- **Float SVD of the raw Laguerre Vandermonde.** At `t ≈ 90`, `L_{23}(t)`
  is `10^18`. The `G(0)=∑ a_j` row disappears. The numerical kernel is not
  a kernel. Exact `Q` is not optional.
- **Sturm on the unreduced degree-23 `hatF`.** 1835-bit coefficients and
  six double roots. Naive square-free + Sturm hung. A verifier that does
  not finish is not a verifier.

## 2. The useful failure

The hung Sturm was useful. It forced the factorisation that the construction
already knows about:

```
hatF(t) = (t − R)² ∏_i (t − t_i)²  S(t),
F(t)    =           ∏_i (t − t_i)²  P(t).
```

Both divisions are exact in `Q[t]`. `S` has degree 11 and `P` has degree 13.
`count_roots` on those two quotients is a few seconds. The dead end taught
the shape of the certificate: divide first, then count.

## 3. The click

Feed the printed Table-4 nodes

```
t_i = 21.77, 29.02, 50.79, 65.34, 90.19
    = 2177/100, 2902/100, 5079/100, 6534/100, 9019/100
```

into the exact odd system. The last odd-multiplicity positive root of `G`
is not near 21.77 (the first double node). It sits in the isolating interval

```
(1267758233/174737932,  878736008/121118135)
≈ (7.2551976464961250, 7.2551976464961259).
```

The hexagonal target is `4π/√3 ≈ 7.255197456936871`. The printed `7.25520`
is a 3.5·10⁻⁷ relative excess over the target, and a 3·10⁻⁷ excess over the
actual last sign-change of this `G`. The same five nodes they published
already give a last sign-change that *prints* as hexagonal to seven decimals.
What was missing was a rational `R` above that isolation, the coefficients,
and a sign check that terminates.

## 4. The argument, in the order it was found

Dimension `n=2`, `α=0`. Laguerre recurrence over `Q`:

```
L_0 = 1,   L_1 = 1 − t,
(k+1) L_{k+1} = (2k+1 − t) L_k − k L_{k−1}.
```

Odd system, `m=5`: twelve coefficients on `{L_1,…,L_{23}}`, eleven
constraints (`G(0)=0` and five double nodes). One-dimensional kernel,
cleared to a primitive integer vector `a_odd`. That is `G`.

`G` has a simple zero at `0`, a simple zero near `1.711`, a simple last
sign-change in the interval above, and double zeros at the five `t_i`.
(The extra interior zero is harmless for Theorem 3.2, which cares about
`F`, not about `G` being single-signed on `(0,R)`.)

Pick `R = 3627599/500000 = 7.255198`, the least 6-decimal rational above
the isolating interval. Even system: twelve coefficients on `{L_0,…,L_{22}}`,
twelve constraints (five double nodes plus `G+H` double at `R`). Unique
solution `b_even`. That is `H`.

Set `F = H − G` and `hatF = H + G`. Then:

- `F(0) = hatF(0) > 0` (because `G(0)=0` and `H(0)>0`).
- `hatF` is divisible by `(t−R)² ∏(t−t_i)²`. The quotient `S` has
  `count_roots(S, (0,∞)) = 0`, `S(0)>0`, `S.LC()>0`. So `hatF ≥ 0` on
  `[0,∞)`, with even-multiplicity zeros only.
- `F` is divisible by `∏(t−t_i)²`. The quotient `P` has
  `count_roots(P, (R,∞)) = 0`, `P(R)<0`, `P.LC()<0`. So `F ≤ 0` on
  `[R,∞)`.

Cohn–Elkies Theorem 3.2 therefore gives

```
δ  ≤  R / (8π)  =  0.2886751562026082…
```

Hexagonal center density is `√3/6 = 0.2886751345948129…`. The ratio is
`1.0000000748515987…`.

## 5. Computer residue

- `compute/certs/ce_d2_m5.json` — exact `a_odd`, `b_even`, monomial
  coefficients of `G,H,F,hatF`, isolating interval, and the sign report.
- `compute/make_certificate.py` — builder.
- `compute/verify.py` — independent replay: rebuilds `G,H` from the stored
  Laguerre coefficients and repeats the divisions + `count_roots`.
- `compute/run_all.sh` — rebuild then verify.
- `compute/CONSTANTS.md` — hex, Levenshtein, Table 3, Table 4, and this
  certificate, all recomputed.

`verify.py` exit 0 tonight.

## 6. What is proved vs still open

**Proved.** There is an explicit admissible radial function in dimension 2,
with coefficients in `Q`, whose Fourier sign conditions reduce to two
root-counts that have been independently replayed, and which certifies

```
δ  ≤  (3627599/500000) / (8π)  <  7.25520 / (8π).
```

It meets the five-decimal Table 3 number `0.28868` and strictly improves
the printed Table 4 value `2πr² = 7.25520`.

**Still open.** Green #42: a function with `R = 4π/√3` exactly, vanishing
on every nonzero A2 shell (and with `hat f` vanishing on the dual shells).
The five-node ansatz cannot do that. The isolating interval sits
`1.9·10^{-7}` above the hexagonal target; closing the rest is the magic
function, not a tighter rationalisation of these nodes.
